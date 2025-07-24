import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- KONFIGURASI ---
# Masukkan TOKEN bot Anda yang didapat dari @BotFather
# Untuk keamanan, lebih baik menggunakan Environment Variable jika di-hosting online
TELEGRAM_TOKEN = "8211213291:AAHgSQzREFI2_pg2GEH7JjWWNKx3fir8AP8"

# Setup logging untuk melihat error
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- DATABASE MEMBER (Bisa diperbanyak) ---
# Data ini bisa Anda kembangkan sendiri atau ambil dari API jika ada
MEMBER_DATABASE = {
    "freyanashifa": {"nama": "Freyanashifa Jayawardana", "panggilan": "Freya", "gen": 7, "status": "Aktif", "jikoshoukai": "Gadis koleris yang suka berimajinasi, terangi harimu dengan senyuman karamelku. Halo semuanya, aku Freya!"},
    "azizi": {"nama": "Azizi Asadel", "panggilan": "Zee", "gen": 7, "status": "Lulus", "jikoshoukai": "Si gadis tomboy yang semangatnya meletup-letup! Panggil aku Zee!"},
    "shani": {"nama": "Shani Indira Natio", "panggilan": "Shani", "gen": 3, "status": "Lulus", "jikoshoukai": "Semanis coklat, selembut sutra. Halo, aku Shani!"},
    "gracia": {"nama": "Shania Gracia", "panggilan": "Gracia", "gen": 3, "status": "Aktif", "jikoshoukai": "Senyumku akan terekam jelas dalam ingatanmu seperti foto dengan sejuta warna. Aku Gracia!"},
    "feni": {"nama": "Feni Fitriyanti", "panggilan": "Feni", "gen": 3, "status": "Aktif", "jikoshoukai": "Matahari yang akan menyinari hari-harimu, hangat dan bercahaya selalu! Aku Feni!"},
}

# --- FUNGSI-FUNGSI UTAMA ---

# Fungsi untuk mengambil jadwal dari website
def get_theater_schedule():
    try:
        url = "https://jkt48.com/theater/schedule"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        schedule_list = soup.find_all('div', class_='entry-schedule__item')
        if not schedule_list:
            return "Saat ini tidak ada jadwal theater yang tersedia."

        message = "📅 **Jadwal Theater JKT48 Terbaru** 📅\n\n"
        for item in schedule_list[:5]: # Ambil 5 jadwal teratas
            day = item.find('div', class_='entry-schedule__item--day').text.strip()
            date = item.find('div', class_='entry-schedule__item--date').text.strip()
            title = item.find('h3', class_='entry-schedule__item--title').text.strip()
            
            message += f"**{day}, {date}**\n_{title}_\n\n"
        return message
    except Exception as e:
        logging.error(f"Error saat mengambil jadwal: {e}")
        return "Maaf, terjadi kesalahan saat mengambil data jadwal dari website."

# Fungsi untuk mengambil berita dari website
def get_latest_news():
    try:
        url = "https://jkt48.com/news/list"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        news_list = soup.find_all('div', class_='entry-news__item')
        if not news_list:
            return "Tidak ada berita terbaru yang ditemukan."
            
        message = "📰 **Berita Terbaru JKT48** 📰\n\n"
        for item in news_list[:5]: # Ambil 5 berita teratas
            title = item.find('h3', class_='entry-news__item--title').text.strip()
            link = "https://jkt48.com" + item.find('a')['href']
            message += f"• [{title}]({link})\n"
        return message
    except Exception as e:
        logging.error(f"Error saat mengambil berita: {e}")
        return "Maaf, terjadi kesalahan saat mengambil data berita dari website."

# --- PERINTAH-PERINTAH BOT ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Jadwal Theater", callback_data='jadwal')],
        [InlineKeyboardButton("📰 Berita Terbaru", callback_data='berita')],
        [InlineKeyboardButton("🎤 Info Member", callback_data='info_member')],
        [InlineKeyboardButton("🔴 Cek Live SHOWROOM", callback_data='showroom_live')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "Halo! Selamat datang di Bot Info JKT48.\n\n"
        "Gunakan tombol di bawah atau ketik perintah untuk mendapatkan informasi:\n"
        "• `/jadwal` - Melihat jadwal theater.\n"
        "• `/berita` - Melihat berita terbaru.\n"
        "• `/member [nama]` - Contoh: `/member freya`\n"
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'jadwal':
        message = get_theater_schedule()
        await query.edit_message_text(text=message, parse_mode='Markdown')
    elif query.data == 'berita':
        message = get_latest_news()
        await query.edit_message_text(text=message, parse_mode='Markdown', disable_web_page_preview=True)
    elif query.data == 'info_member':
        await query.edit_message_text(text="Silakan ketik `/member [nama panggilan]`.\nContoh: `/member zee`")
    elif query.data == 'showroom_live':
        # Ini adalah contoh, idealnya ini akan memanggil fungsi pengecekan live
        await query.edit_message_text(text="Fitur pengecekan live SHOWROOM sedang dalam pengembangan!")

async def jadwal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_theater_schedule()
    await update.message.reply_text(message, parse_mode='Markdown')

async def berita_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_latest_news()
    await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)

async def member_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Mengambil nama member dari argumen, contoh: /member freya
        member_key = context.args[0].lower()
        member_data = MEMBER_DATABASE.get(member_key)

        if member_data:
            message = (
                f"👤 **Profil Member: {member_data['nama']}**\n\n"
                f"**Panggilan:** {member_data['panggilan']}\n"
                f"**Generasi:** {member_data['gen']}\n"
                f"**Status:** {member_data['status']}\n\n"
                f"**Jikoshoukai:**\n_{member_data['jikoshoukai']}_"
            )
        else:
            message = f"Maaf, member dengan nama '{member_key}' tidak ditemukan di database."
            
    except (IndexError, ValueError):
        message = "Format perintah salah. Gunakan: `/member [nama panggilan]`\nContoh: `/member shani`"
        
    await update.message.reply_text(message, parse_mode='Markdown')

# --- MAIN PROGRAM ---
if __name__ == '__main__':
    if TELEGRAM_TOKEN == "GANTI_DENGAN_TOKEN_BOT_ANDA":
        print("!!! KESALAHAN: Harap ganti 'TELEGRAM_TOKEN' dengan token bot Anda yang asli di dalam script.")
    else:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Daftarkan semua handler
        application.add_handler(CommandHandler('start', start_command))
        application.add_handler(CommandHandler('jadwal', jadwal_command))
        application.add_handler(CommandHandler('berita', berita_command))
        application.add_handler(CommandHandler('member', member_command))
        application.add_handler(CallbackQueryHandler(button_handler))

        print("Bot sedang berjalan... Tekan Ctrl+C untuk berhenti.")
        # Mulai bot
        application.run_polling()
