import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# 1. Kandilli'den verileri çek
url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
response = requests.get(url)
data = response.json()['result']

# 2. Veriyi düzenle
df = pd.DataFrame(data)

# Zaman bilgisi kontrolü (Kandilli API'sine göre dinamik seçim)
if 'date' in df.columns:
    df['tarih_saat'] = df['date']
elif 'rev' in df.columns:
    df['tarih_saat'] = df['rev']
else:
    df['tarih_saat'] = pd.Timestamp.now(tz='Europe/Istanbul').strftime('%d.%m.%Y %H:%M:%S')

# Koordinat kontrolü (Felt haritası için kritik)
if 'geojson' in df.columns and 'lat' not in df.columns:
    df['lat'] = df['geojson'].apply(lambda x: x['coordinates'][1])
    df['lng'] = df['geojson'].apply(lambda x: x['coordinates'][0])

# Sadece gerekli sütunları alıyoruz ve 50 SATIR SINIRINI KALDIRDIK
cols = ['tarih_saat', 'title', 'mag', 'lat', 'lng', 'depth']
df = df[cols]

# 3. Google Sheets Bağlantısı (İsim hatalarına karşı esnek yapı)
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# GitHub'da hangi ismi verdiysen (GCP_KEY veya GCP_SERVICE_ACCOUNT_KEY) onu otomatik bulur
gcp_key_raw = os.environ.get('GCP_SERVICE_ACCOUNT_KEY') or os.environ.get('GCP_KEY')

if not gcp_key_raw:
    # Eğer ikisini de bulamazsa mevcut tüm gizli değişkenleri listele (hata ayıklama için)
    available_keys = [k for k in os.environ.keys() if "GCP" in k]
    raise ValueError(f"Hata: Anahtar bulunamadı. Mevcut GCP anahtarları: {available_keys}")

try:
    key_dict = json.loads(gcp_key_raw)
except json.JSONDecodeError as e:
    print(f"Hata: JSON formatı bozuk. Hata detayı: {e}")
    raise

creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
client = gspread.authorize(creds)

# 4. Tabloya Yaz
spreadsheet_id = "1QfRsf8YjsQnsCq1Gqwl3wXbDbgJxcv4sQGWsGx_G3zU"
sheet = client.open_by_key(spreadsheet_id).sheet1

sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print(f"İşlem başarılı: {len(df)} adet kayıt [Google Sheets](https://docs.google.com/spreadsheets/d/1QfRsf8YjsQnsCq1Gqwl3wXbDbgJxcv4sQGWsGx_G3zU/edit) tablosuna aktarıldı.")
