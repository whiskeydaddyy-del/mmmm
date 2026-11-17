import os
import requests
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from telegram.request import HTTPXRequest

# بيانات بوت التليجرام الخاص بك (بوت الأتمتة)
TELEGRAM_BOT_TOKEN = "9096627772:AAFZVGAmgGcSr9cmMTkFagyarkt_XwjYYxw"
ADMIN_ID = 8607731717  # الآيدي الخاص بك

# بيانات جيت هب الخاصة بك يا المرعب اليماني
GITHUB_TOKEN = "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"
GITHUB_USERNAME = "whiskeydaddyy-del"

def create_github_repo_and_upload(file_path, file_name):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    repo_name = file_name.replace(".py", "").lower() + "-bot-247"
    
    # 1. إنشاء مستودع جديد على جيت هب
    repo_data = {"name": repo_name, "private": False}
    r = requests.post("https://api.github.com/user/repos", json=repo_data, headers=headers)
    
    if r.status_code not in [201, 422]:
        return None, f"خطأ في جيت هب: {r.text}"

    # 2. قراءة ملف البوت ورفعه إلى المستودع باسم main.py
    with open(file_path, "rb") as f:
        content_bytes = f.read()
    content_encoded = base64.b64encode(content_bytes).decode("utf-8")
    
    file_data = {
        "message": "Add bot script for hosting",
        "content": content_encoded
    }
    upload_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/main.py"
    requests.put(upload_url, json=file_data, headers=headers)
    
    # 3. رفع ملف requirements.txt تلقائياً لتثبيت المكتبات
    req_content = "requests\npyrogram\ntgcrypto\napscheduler\nflask\n"
    req_data = {
        "message": "Add requirements",
        "content": base64.b64encode(req_content.encode("utf-8")).decode("utf-8")
    }
    requests.put(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/requirements.txt", json=req_data, headers=headers)

    return repo_name, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("عذراً، هذا البوت مخصص للمرعب اليماني فقط.")
        return
    await update.message.reply_text("أهلاً بك يا المرعب اليماني 🛡️.\nأرسل لي أي ملف بوت `.py` وسأقوم برفعه وتجهيزه في مستودع GitHub فوراً لتعمله استضافة دائمة!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    if update.message.document:
        document = update.message.document
        if not document.file_name.endswith('.py'):
            await update.message.reply_text("⚠️ يرجى إرسال ملف بايثون ينتهي بـ (.py) فقط.")
            return

        msg = await update.message.reply_text("⚡ جاري استقبال الملف ورفعه إلى مستودع GitHub...")
        
        file = await context.bot.get_file(document.file_id)
        file_path = f"./{document.file_name}"
        await file.download_to_drive(file_path)

        # رفع لجيت هب
        repo_name, err = create_github_repo_and_upload(file_path, document.file_name)
        if not repo_name:
            await msg.edit_text(f"❌ فشل الرفع: {err}")
            return

        # رسالة النجاح
        repo_link = f"https://github.com/{GITHUB_USERNAME}/{repo_name}"
        render_link = "https://dashboard.render.com"
        
        success_text = (
            "✅ **تم رفع البوت إلى مستودع GitHub بنجاح تام!**\n\n"
            f"📦 اسم المستودع: `{repo_name}`\n"
            f"🔗 رابط المستودع: {repo_link}\n\n"
            "🚀 **للتشغيل الدائم 24/7:**\n"
            f"ادخل إلى [موقع Render]({render_link}) واضغط `New +` ثم اختر `Background Worker` واربطه بهذا المستودع وسيعمل فوراً!"
        )
        
        await msg.edit_text(success_text, parse_mode="Markdown")

        if os.path.exists(file_path):
            os.remove(file_path)
    else:
        await update.message.reply_text("أهلاً بك يا المرعب اليماني، أنا جاهز.. أرسل لي ملف البوت (.py) لأقوم برفعه لجيت هب فوراً.")

def main():
    # تخصيص إعدادات الاتصال لتناسب بيئة الهاتف وتجنب أخطاء الشبكة والمهلة الزمنية
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    
    print("بوت الأتمتة يعمل الآن باتصال محسّن...")
    app.run_polling()

if __name__ == "__main__":
    main()
