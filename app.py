import hmac
import os
from pathlib import Path

import requests
import streamlit as st
from streamlit.components.v1 import declare_component

ROOT = Path(__file__).resolve().parent
HUB_DIR = ROOT / "hub"

# Şikayet & Görev Paneli (destekhedef) Apps Script proxy endpoint
SIKAYET_ENDPOINT = (
    "https://script.google.com/macros/s/"
    "AKfycbyii3UgQxR3Y3DUdPO6RO3S8Y8GS3DwIlx267txMHHnWNKE_WO6XOOG_D3mS5vtn91G/exec"
)

UPSTREAM_ERROR = {
    "ok": False,
    "error": {
        "code": "UPSTREAM",
        "message": "Apps Script bağlantısı kurulamadı. Web uygulaması dağıtımını kontrol edin.",
    },
}

MAX_PAYLOAD_BYTES = 256_000


def _read_secret(section: str, key: str, env_key: str) -> str:
    try:
        val = st.secrets.get(section, {}).get(key)
        if val:
            return str(val)
    except Exception:
        pass
    return os.environ.get(env_key, "")


def _handle_portal_auth(username: str, password: str) -> dict:
    expected_user = _read_secret("portal", "username", "HEDEF_PORTAL_USERNAME")
    expected_pass = _read_secret("portal", "password", "HEDEF_PORTAL_PASSWORD")

    if not expected_user or not expected_pass:
        return {
            "ok": False,
            "error": "Merkezi portal kimlik ayarları (.streamlit/secrets.toml) yapılandırılmamış.",
        }

    user_ok = hmac.compare_digest(username.strip().lower(), expected_user.strip().lower())
    pass_ok = hmac.compare_digest(password, expected_pass)

    if not (user_ok and pass_ok):
        return {
            "ok": False,
            "error": "Kullanıcı adı veya şifre hatalı.",
        }

    return {
        "ok": True,
        "username": expected_user,
        "passwords": {
            "sikayet": _read_secret("panels", "sikayet_password", "HEDEF_SIKAYET_PASSWORD"),
            "kota": _read_secret("panels", "kota_password", "HEDEF_KOTA_PASSWORD"),
            "anketportal": _read_secret("panels", "anket_password", "HEDEF_ANKET_PASSWORD"),
        },
    }


st.set_page_config(
    page_title="Hedef AVM | Birleşik Yönetim Paneli",
    page_icon="🏢",
    layout="wide",
)

st.html(
    """
<style>
header[data-testid="stHeader"], footer, #MainMenu, .stDeployButton { display: none; }
body, [data-testid="stMain"] { overflow: hidden; margin: 0; padding: 0; }
.block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
iframe[title$=".hedef_hub"] {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100dvh !important;
    border: 0;
    z-index: 999999;
    display: block;
}
</style>
"""
)

if not (HUB_DIR / "index.html").is_file():
    st.error("hub/index.html dosyası bulunamadı. Proje klasörünü kontrol edin.")
    st.stop()

hub_component = declare_component("hedef_hub", path=str(HUB_DIR))
response = st.session_state.get("hub_response")
event = hub_component(response=response, key="hedef_hub", default=None)

if isinstance(event, dict) and isinstance(event.get("id"), str):
    event_id = event["id"]
    if not response or response.get("id") != event_id:
        event_kind = event.get("kind", "sikayet_rpc")

        if event_kind == "portal_auth":
            auth_result = _handle_portal_auth(
                str(event.get("username", "")),
                str(event.get("password", "")),
            )
            st.session_state.hub_response = {
                "id": event_id,
                "kind": "portal_auth",
                "result": auth_result,
            }
            st.rerun()
        else:
            body = event.get("request")
            result = UPSTREAM_ERROR
            if isinstance(body, str) and len(body.encode("utf-8")) <= MAX_PAYLOAD_BYTES:
                try:
                    upstream = requests.post(
                        SIKAYET_ENDPOINT,
                        data=body.encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        timeout=(10, 370),
                    )
                    upstream.raise_for_status()
                    value = upstream.json()
                    if isinstance(value, dict) and isinstance(value.get("ok"), bool):
                        result = value
                except requests.Timeout:
                    result = {
                        "ok": False,
                        "error": {
                            "code": "BACKEND_TIMEOUT",
                            "message": "Apps Script zamanında yanıt vermedi. Aynı dosyayla kaldığınız yerden devam edebilirsiniz.",
                        },
                    }
                except (requests.RequestException, ValueError):
                    pass
            st.session_state.hub_response = {
                "id": event_id,
                "kind": "sikayet_rpc",
                "result": result,
            }
            st.rerun()
