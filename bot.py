import os
import asyncio
import logging
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Filtre Kriterleri
MIN_PRICE = 0.10
MAX_PRICE = 20.0
MIN_VOLUME = 100000
VOL_MULTIPLIER = 3.0    # Normal hacmin en az 3 katı
PRICE_CHANGE_MIN = 2.0  # En az %2 fiyat hareketi
COOLDOWN_MINUTES = 5

USER_CHAT_ID = None
alert_history = {}

TICKERS = [
    "AAPL", "TSLA", "NVDA", "AMZN", "AMD", "PLTR", "SOFI", "LCID", "MARA", "RIOT",
    "MULN", "SAVA", "OPEN", "FSR", "CLOV", "SNDL", "NKLA", "BB", "WKHS", "GOEV"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USER_CHAT_ID
    USER_CHAT_ID = update.message.chat_id
    await update.message.reply_text(
        "🚀 Nasdaq Hacim Takip Botu (5dk & 15dk) Aktif!\n\n"
        "Tarama başladı. $0.10 - $20 arası 5 ve 15 dakikalık hacim patlamaları bildirilecek."
    )

async def check_timeframe(ticker_symbol, timeframe, app):
    """Belirtilen zaman diliminde (5m / 15m) hacim patlamasını kontrol eder."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="5d", interval=timeframe)
        
        if df.empty or len(df) < 6:
            return

        last_bar = df.iloc[-1]
        price = last_bar['Close']
        vol_current = last_bar['Volume']

        # Fiyat Filtresi
        if not (MIN_PRICE <= price <= MAX_PRICE):
            return

        # Son 5 mumun hacim ortalaması
        avg_vol = df['Volume'].iloc[-6:-1].mean()
        if avg_vol == 0 or vol_current < MIN_VOLUME:
            return

        vol_ratio = vol_current / avg_vol
        prev_price = df.iloc[-2]['Close']
        price_change = ((price - prev_price) / prev_price) * 100

        # Hacim anomalisi ve cooldown kontrolü
        now = pd.Timestamp.now()
        alert_key = f"{ticker_symbol}_{timeframe}"
        last_alert_time = alert_history.get(alert_key)

        if vol_ratio >= VOL_MULTIPLIER and price_change >= PRICE_CHANGE_MIN:
            if last_alert_time is None or (now - last_alert_time).total_seconds() > (COOLDOWN_MINUTES * 60):
                alert_history[alert_key] = now
                
                msg = (
                    f"🚨 **VOLUME SPIKE ({timeframe.upper()})**\n"
                    f"**Ticker:** {ticker_symbol}\n\n"
                    f"💵 **Fiyat:** ${price:.2f}\n"
                    f"📊 **{timeframe} Hacim:** {vol_current:,.0f}\n"
                    f"📈 **Ort. Hacim:** {avg_vol:,.0f}\n"
                    f"🔥 **Hacim Katı:** {vol_ratio:.2f}x\n"
                    f"📈 **Fiyat Değişimi:** %{price_change:+.2f}\n"
                    f"⏰ **Zaman:** {now.strftime('%H:%M:%S')}\n"
                    f"🔗 [TradingView](https://www.tradingview.com/symbols/{ticker_symbol}/)"
                )
                await app.bot.send_message(chat_id=USER_CHAT_ID, text=msg, parse_mode="Markdown")
    except Exception:
        pass

async def scan_market(app):
    while True:
        if USER_CHAT_ID:
            for ticker_symbol in TICKERS:
                # Hem 5 dakikalık hem de 15 dakikalık mumları tara
                await check_timeframe(ticker_symbol, "5m", app)
                await check_timeframe(ticker_symbol, "15m", app)
                await asyncio.sleep(0.3)
                
        await asyncio.sleep(180) # 3 dakikada bir tarama döngüsünü yenile

async def main():
    if not TOKEN:
        print("HATA: .env dosyasında BOT_TOKEN bulunamadı!")
        return
        
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("Bot 5dk & 15dk taraması için aktif!")
    asyncio.create_task(scan_market(app))
    
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass