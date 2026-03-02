import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# 1. Kandilli API'den tam veriyi çek
url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
response = requests.get(url)
data = response.json()['result']

# 2. Veriyi DataFrame'e aktar ve bileşenleri doğrula
df = pd.DataFrame(data)

# 'date' sütununu 'tarih_saat' olarak daha okunaklı yapalım
df['tarih_saat'] = df['date']

# Tüm bileşenleri içeren sütunları seçelim
# lat: Enlem, lng: Boylam, mag: Büyüklük, depth: Derinlik
df = df[['tarih_saat', 'title', 'mag', 'lat', 'lng', 'depth']].head(50)

# 3. Google Sheets Bağlantısı
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key_dict = json.loads(os.environ['GCP_KEY'])
creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
client = gspread.authorize(creds)

# 4. Tabloyu Güncelle
spreadsheet_id = "1QfRsf8YjsQnsCq1Gqwl3wXbDbgJxcv4sQGWsGx_G3zU"
sheet = client.open_by_key(spreadsheet_id).sheet1

sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("Tüm veri bileşenleri başarıyla aktarıldı.")
