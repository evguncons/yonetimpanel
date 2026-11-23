# Hedef AVM — Birleşik Yönetim Paneli

Hedef AVM'nin 3 yönetim sistemini **tek yönetici girişiyle (SSO)** bir araya getiren Streamlit uygulaması.

## Entegre Sistemler

1. **Şikayet & Personel Görev Paneli** (`hub/modules/sikayet/index.html`)
2. **Şube Kota & Net Peşinat Takip Sistemi** (`hub/modules/kota/index.html`)
3. **Anket & Değerlendirme Portalı** (`hub/modules/anketportal/index.html`)

## Streamlit Community Cloud ile Yayınlama

1. Bu paketin içeriğini yeni bir **GitHub** deposuna (tercihen **Private**) yükleyin.
2. [share.streamlit.io](https://share.streamlit.io) adresinden **Create app** diyerek deponuzu seçin ve ana dosya olarak `app.py` belirleyin.
3. Uygulama ayarlarından **Settings → Secrets** bölümüne `.streamlit/secrets.toml.example` şablonundaki gibi giriş şifrelerinizi girip kaydedin:

```toml
[portal]
username = "admin"
password = "MERKEZI_PORTAL_SIFRENIZ"

[panels]
sikayet_password = "SIKAYET_PANEL_YONETICI_SIFRESI"
kota_password = "KOTA_PANEL_YONETICI_SIFRESI"
anket_password = "ANKET_PORTAL_YONETICI_SIFRESI"
```

> **Güvenlik Notu:** `.streamlit/secrets.toml` dosyası `.gitignore` içindedir; şifreler hiçbir zaman GitHub reposuna veya istemci HTML koduna yazılmaz.

## Yerel Çalıştırma

1. `.streamlit/secrets.toml.example` dosyasını `.streamlit/secrets.toml` olarak kopyalayıp şifreleri doldurun.
2. `baslat.bat` dosyasına çift tıklayın veya terminalde çalıştırın:

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8509
```
