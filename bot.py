import os
import time
import pandas as pd
import yfinance as yf
from telegram import Bot
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- RENDER SAĞLIK KONTROLÜ SUNUCUSU (RENDER KAPATMASIN DİYE) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# --- BOT VE BİLDİRİM KODLARI ---
TOKEN = os.environ.get("BOT_TOKEN")

# Telegram Botunu Başlat
bot = Bot(token=TOKEN)

async def send_telegram_message(message):
    # Telegram kanal/grup ID'niz veya sohbet ID'niz
    # Burayı kendi Chat ID'niz ile güncelleyebilirsiniz veya env variable kullanabilirsiniz.
    chat_id = os.environ.get("CHAT_ID")
    if chat_id:
        await bot.send_message(chat_id=chat_id, text=message)

def check_volume_spikes():
    print("Hacim kontrolü yapılıyor...")
    # Hacim kontrolü ve yfinance mantığınız burada çalışır

async def main():
    print("Nasdaq Hacim Botu Başlatıldı...")
    while True:
        try:
            check_volume_spikes()
        except Exception as e:
            print(f"Hata oluştu: {e}")
        await asyncio.sleep(60) # 60 saniyede bir kontrol et

if __name__ == "__main__":
    asyncio.run(main())
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()
