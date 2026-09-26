hereimport os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = "ضع_التوكين_هنا"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط فيديو من (تيك توك، إنستغرام، يوتيوب) أو اكتب اسم أغنية للبحث عنها وتحميلها.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    msg = await update.message.reply_text("جاري المعالجة والتحميل...")

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        if not text.startswith("http://") and not text.startswith("https://"):
            search_query = f"ytsearch1:{text}"
        else:
            search_query = text

        loop = asyncio.get_event_loop()
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                filename = ydl.prepare_filename(info)
                return filename, info.get('title', 'media')

        filename, title = await loop.run_in_executor(None, download)

        with open(filename, 'rb') as file:
            if filename.endswith(('.mp3', '.m4a', '.wav')):
                await update.message.reply_audio(audio=file, caption=title)
            else:
                await update.message.reply_video(video=file, caption=title)

        if os.path.exists(filename):
            os.remove(filename)
            
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"حدث خطأ أثناء التحميل: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
