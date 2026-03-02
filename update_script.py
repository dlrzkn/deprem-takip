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

# Zaman bilgisi için kontrol
if 'date' in df.columns:
    df['tarih_saat'] = df['date']
elif 'date_time' in df.columns:
    df['tarih_saat'] = df['date_time']
else:
    df['tarih_saat'] = "Bilinmiyor"

# Koordinat ve diğer sütunları garantiye al (API'den gelen orijinal isimleri kullanıyoruz)
# Kandilli API'sinde enlem 'lat', boylam 'lng' olarak gelir. 
# Eğer tabloda görünmüyorsa, bu isimlerin varlığını burada zorunlu tutalım:
cols_to_export = ['tarih_saat', 'title', 'mag', 'lat', 'lng', 'depth']

# Sadece bu 6 sütunu al ve ilk 50 depremi seç
df = df[cols_to_export].head(50)

# 3. Google Sheets Bağlantısı
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key_dict = json.loads(os.environ['GCP_KEY'])
creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
client = gspread.authorize(creds)

# 4. Tabloya Yaz
spreadsheet_id = "1QfRsf8YjsQnsCq1Gqwl3wXbDbgJxcv4sQGWsGx_G3zU"
sheet = client.open_by_key(spreadsheet_id).sheet1

# Tabloyu temizle ve başlıklarla birlikte veriyi yaz
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("Tüm sismik bileşenler başarıyla güncellendi.")
