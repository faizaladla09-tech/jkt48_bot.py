import os
import requests
import time
import schedule
import threading
from telegram import Bot

# --- KONFIGURASI PENTING ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8211213291:AAHgSQzREFI2_pg2GEH7JjWWNKx3fir8AP8")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "AAAAAAAAAAAAAAAAAAAAACzo3AEAAAAAMuGK979O5yT5s%2FJMpR6xHx2LFLY%3DIBKEFsJbyfoODcux5BzZKo9a0W5vXWHVEwaHammei4tSFaALYI")

# Ganti dengan ID user Twitter yang ingin dipantau (misal: @officialJKT48)
# Anda bisa dapatkan ID ini dari situs seperti TweeterID
TWITTER_USER_ID = "351535962"
"1649644356964597762"

# Ganti dengan ID Channel/Grup Telegram Anda (bisa didapat dari @userinfobot)
# Awali dengan tanda minus (-) jika itu grup/channel
TELEGRAM_CHAT_ID = "-https://t.me/jkt48info134"

# Untuk menyimpan ID tweet terakhir agar tidak spam
LAST_TWEET_ID = None

bot = Bot(token=TELEGRAM_TOKEN)

def check_jkt48_live_tweet():
    global LAST_TWEET_ID
    print("Mengecek tweet terbaru...")

    try:
        url = f"https://api.twitter.com/2/users/{TWITTER_USER_ID}/tweets"
        headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
        params = {"tweet.fields": "created_at", "max_results": 5}

        response = requests.get(url, headers=headers, params=params)
        tweets = response.json()

        if 'data' in tweets:
            latest_tweet = tweets['data'][0]
            tweet_id = latest_tweet['id']
            tweet_text = latest_tweet['text']

            # Jika tweet baru dan mengandung kata kunci 'live'
            if tweet_id != LAST_TWEET_ID and ("live" in tweet_text.lower() or "showroom" in tweet_text.lower()):
                print(f"Tweet LIVE baru ditemukan: {tweet_text}")

                # Kirim notifikasi ke Telegram
                message = f"🔥 **JKT48 LIVE INFO!** 🔥\n\n{tweet_text}"
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')

                LAST_TWEET_ID = tweet_id
            else:
                print("Tidak ada tweet LIVE baru.")
        else:
            print("Gagal mendapatkan data tweet.")

    except Exception as e:
        print(f"Terjadi error: {e}")

def run_scheduler():
    # Jadwalkan pengecekan setiap 1 menit
    schedule.every(1).minutes.do(check_jkt48_live_tweet)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("Bot Info Live JKT48 Mulai...")
    # Jalankan pengecekan pertama kali saat bot start
    check_jkt48_live_tweet()

    # Jalankan scheduler di thread terpisah
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()
    print("Scheduler berjalan di latar belakang. Bot siap memantau.")
