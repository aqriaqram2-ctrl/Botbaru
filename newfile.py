import smtplib
import imaplib
import email
import asyncio
from email.mime.text import MIMEText
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ================== KEEP ALIVE ==================
from flask import Flask
from threading import Thread

app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot hidup"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ================== CONFIG ==================
BOT_TOKEN = "8218474846:AAHXoSifC8wwB-avAwX1l9jaTNkG-NhaHUk"

EMAIL_SENDER = "aqri1205@gmail.com"
EMAIL_PASSWORD = "d v b r j s d g y t k w p h e b"
EMAIL_RECEIVER = "smb@support.whatsapp.com"

IMAP_SERVER = "imap.gmail.com"

user_last_report = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("START MASUK")
    await update.message.reply_text("Masukkan nomor WhatsApp (contoh: 628xxxx):")

# ================== HANDLE INPUT ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    number = update.message.text.strip()

    subject = "WhatsApp Business Account Issue - Login Not Available"
    body = f"""Hello WhatsApp Support,

I am experiencing an issue with my WhatsApp Business account.

Phone number: +{number}

Problem:
Login is not available. I cannot access my account.

Please help me resolve this issue as soon as possible.

Thank you.
"""

    try:
        send_email(subject, body)
        user_last_report[user_id] = number

        await update.message.reply_text("✅ Laporan berhasil dikirim, menunggu balasan...")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal kirim email:\n{e}")

# ================== SEND EMAIL ==================
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ================== CEK BALASAN ==================
async def check_replies(app):
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_SENDER, EMAIL_PASSWORD)
            mail.select("inbox")

            status, messages = mail.search(None, '(UNSEEN)')

            for num in messages[0].split():
                status, msg_data = mail.fetch(num, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                sender = msg["From"]

                if sender and "whatsapp" in sender.lower():
                    for user_id in user_last_report:
                        await app.bot.send_message(
                            chat_id=user_id,
                            text="✅ Balasan dari WhatsApp diterima!\nStatus: SUCCESS"
                        )

            mail.logout()

        except Exception as e:
            print("Error cek email:", e)

        await asyncio.sleep(30)

# ================== POST INIT ==================
async def post_init(app):
    app.create_task(check_replies(app))

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("BOT RUNNING...")

    app.run_polling()

# ================== RUN ==================
if __name__ == "__main__":
    keep_alive()  # 🔥 biar tidak sleep di Replit
    main()