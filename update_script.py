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
# Sadece gerekli sütunları alalım ve ilk 50 depremi seçelim (kalabalığı önlemek için)
df = df[['date', 'title', 'mag', 'lat', 'lng', 'depth']].head(50)

# 3. Google Sheets Bağlantısı
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
# GitHub Secrets'a eklediğin anahtarı kullanır
key_dict = json.loads(os.environ['GCP_KEY'])
creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
client = gspread.authorize(creds)

# 4. Tabloya Yaz
spreadsheet_id = "1QfRsf8YjsQnsCq1Gqwl3wXbDbgJxcv4sQGWsGx_G3zU"
sheet = client.open_by_key(spreadsheet_id).sheet1

# Tabloyu temizle ve yeni veriyi yaz
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("Deprem verileri başarıyla güncellendi!")
