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

# API'den gelen gerçek sütun isimlerini görmek için (Hata ayıklama için)
print("API Sütunları:", df.columns.tolist())

# Zaman bilgisi kontrolü
# API'den gelen farklı tarih formatlarını yakalamak için
if 'date' in df.columns:
    df['tarih_saat'] = df['date']
elif 'date_time' in df.columns:
    df['tarih_saat'] = df['date_time']
elif 'rev' in df.columns:
    # Kandilli bazen tarih verisini 'rev' sütununda gönderir
    df['tarih_saat'] = df['rev']
else:
    # Eğer hiçbiri yoksa, işlem anının zamanını damga olarak vur
    df['tarih_saat'] = pd.Timestamp.now(tz='Europe/Istanbul').strftime('%d.%m.%Y %H:%M:%S')

# Koordinat isimlerini API'ye göre eşitle (geojson yapısında olabilirler)
# Eğer doğrudan lat/lng yoksa koordinat listesinden çekmeyi dener
if 'geojson' in df.columns:
    # Bazı API versiyonları koordinatı geojson içinde saklar
    df['lat'] = df['geojson'].apply(lambda x: x['coordinates'][1])
    df['lng'] = df['geojson'].apply(lambda x: x['coordinates'][0])

# Gereken sütunları güvenli seç
cols = ['tarih_saat', 'title', 'mag', 'lat', 'lng', 'depth']
# Sadece mevcut olanları al, hata vermesini engelle
df = df[[c for c in cols if c in df.columns]].head(50)

# 3. Google Sheets Bağlantısı
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key_dict = json.loads(os.environ['GCP_KEY'])
creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
client = gspread.authorize(creds)

# 4. Tabloya Yaz
spreadsheet_id = "1QfRsf8YjsQnsCq1Gqwl3wXbDbgJxcv4sQGWsGx_G3zU"
sheet = client.open_by_key(spreadsheet_id).sheet1

sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("Veriler başarıyla işlendi.")
