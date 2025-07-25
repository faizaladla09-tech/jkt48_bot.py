import os
import requests
import logging
import schedule
import threading
from telegram import Bot

# --- KONFIGURASI WAJIB ---
# Ganti dengan data yang sudah Anda siapkan.
# Untuk keamanan, SANGAT disarankan menggunakan Environment Variables jika di-hosting.
TELEGRAM_TOKEN = os.getenv("8211213291:AAHgSQzREFI2_pg2GEH7JjWWNKx3fir8AP8")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "AAAAAAAAAAAAAAAAAAAAACzo3AEAAAAAMuGK979O5yT5s%2FJMpR6xHx2LFLY%3DIBKEFsJbyfoODcux5BzZKo9a0W5vXWHVEwaHammei4tSFaALYI")")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1002411982288")

# ID Akun X @officialJKT48
TWITTER_USER_ID = "351535962"
"1649644356964597762"

# Kata kunci untuk mendeteksi notifikasi live
LIVE_KEYWORDS = ["live", "showroom", "instagram", "tiktok"]

# Setup logging untuk memantau aktivitas bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Variabel global untuk menyimpan ID tweet terakhir yang dikirim
# Ini penting agar bot tidak mengirim notifikasi yang sama berulang-ulang
LAST_SENT_TWEET_ID = None

def check_latest_tweet():
    """
    Fungsi ini memeriksa tweet terbaru dari akun target, memfilternya,
    dan mengirim notifikasi jika sesuai kriteria.
    """
    global LAST_SENT_TWEET_ID
    logging.info("Mengecek tweet terbaru dari X...")

    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    url = f"https://api.twitter.com/2/users/{TWITTER_USER_ID}/tweets"
    params = {
        "tweet.fields": "created_at",
        "max_results": 5, # Ambil 5 tweet terakhir untuk berjaga-jaga
        "exclude": "replies,retweets" # Abaikan balasan dan retweet
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code != 200:
            logging.error(f"Gagal mengakses API X: {response.status_code} - {response.text}")
            return

        tweets = response.json()
        if 'data' not in tweets or not tweets['data']:
            logging.info("Tidak ada tweet baru yang ditemukan.")
            return

        latest_tweet = tweets['data'][0]
        tweet_id = latest_tweet['id']
        tweet_text = latest_tweet['text']
        tweet_url = f"https://twitter.com/officialJKT48/status/{tweet_id}"

        # Jika ini adalah pengecekan pertama, simpan ID tweet terbaru dan hentikan
        if LAST_SENT_TWEET_ID is None:
            LAST_SENT_TWEET_ID = tweet_id
            logging.info(f"Inisialisasi berhasil. Tweet terakhir yang tercatat ID: {tweet_id}")
            return

        # Jika tweet terbaru berbeda dari yang terakhir dikirim
        if tweet_id != LAST_SENT_TWEET_ID:
            logging.info(f"Tweet baru terdeteksi! ID: {tweet_id}")
            
            # Cek apakah mengandung kata kunci live
            if any(keyword in tweet_text.lower() for keyword in LIVE_KEYWORDS):
                message = (
                    f"🔥 **NOTIFIKASI LIVE JKT48!** 🔥\n\n"
                    f"{tweet_text}\n\n"
                    f"🔗 [Lihat di X]({tweet_url})"
                )
                logging.info(f"Mengirim notifikasi live ke {TELEGRAM_CHAT_ID}")
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
            else:
                # Jika tidak mengandung kata kunci live, bisa juga dikirim sebagai info umum
                message = (
                    f"📢 **Info Terbaru dari JKT48!**\n\n"
                    f"{tweet_text}\n\n"
                    f"🔗 [Lihat di X]({tweet_url})"
                )
                logging.info(f"Mengirim info umum ke {TELEGRAM_CHAT_ID}")
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')

            # Update ID tweet terakhir yang sudah dikirim
            LAST_SENT_TWEET_ID = tweet_id

    except Exception as e:
        logging.error(f"Terjadi kesalahan saat proses pengecekan tweet: {e}")


def run_scheduler():
    """Menjalankan jadwal pengecekan secara periodik."""
    # Jadwalkan pengecekan setiap 2 menit. 
    # Jangan terlalu cepat untuk menghindari limitasi API X.
    schedule.every(2).minutes.do(check_latest_tweet)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # Validasi konfigurasi awal
    if any(val.startswith("GANTI_DENGAN") for val in [TELEGRAM_TOKEN, TWITTER_BEARER_TOKEN, TELEGRAM_CHAT_ID]):
        logging.error("!!! KESALAHAN: Harap isi semua variabel konfigurasi (TOKEN, CHAT_ID) di dalam script.")
    else:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        logging.info("Bot Info JKT48 dimulai...")
        logging.info(f"Notifikasi akan dikirim ke Chat ID: {TELEGRAM_CHAT_ID}")
        
        # Lakukan pengecekan pertama kali saat bot start untuk inisialisasi
        check_latest_tweet()
        
        # Jalankan scheduler di thread terpisah agar tidak mengganggu proses lain
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logging.info("Scheduler berhasil berjalan. Bot siap memantau info JKT48. Biarkan script ini tetap berjalan.")
        
        # Membuat bot tetap hidup
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logging.info("Bot dihentikan secara manual.")
