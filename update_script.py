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

# Hata giderme: API'deki farklı isimlendirmeleri kontrol et
# Eğer 'date' yoksa 'date_time' veya başka bir isim olabilir, en güvenli olanı seçiyoruz
if 'date' in df.columns:
    df['tarih_saat'] = df['date']
elif 'date_time' in df.columns:
    df['tarih_saat'] = df['date_time']
else:
    # Hiçbiri yoksa hata vermemesi için boş bir sütun oluştur
    df['tarih_saat'] = "Bilinmiyor"

# Gerekli sütunları güvenli bir şekilde seç (Hata almamak için var olanları filtreler)
cols = ['tarih_saat', 'title', 'mag', 'lat', 'lng', 'depth']
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

print("Veriler başarıyla güncellendi.")
