import gspread
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# --- ՆՈՐ ԳՈՐԾԻՔՆԵՐ RENDER-Ի ՀԱՄԱՐ ---
import threading  # Թույլ է տալիս միաժամանակ աշխատեցնել բոտը և կայքը
from flask import Flask
import os
# ------------------------------------

# --- Flask վեբ սերվեր (որպեսզի Render-ը չանջատի բոտը) ---
app = Flask(__name__)

@app.route('/')
def home():
    # Սա այն է, ինչ Render-ը կտեսնի՝ համոզվելու համար, որ ծրագիրն աշխատում է
    return "Bot is alive and running!"

def run_flask():
    # Render-ն ինքն է նշանակում պորտը, մենք այն վերցնում ենք
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# -------------------------------------------------------


# --- ԿԱՐԳԱՎՈՐՈՒՄՆԵՐ (Ձեր հին կարգավորումները) ---
# 1. Տեղադրեք ձեր BotFather-ից ստացած TOKEN-ը
BOT_TOKEN = "8048043305:AAEw8sVXR26k3Gt06Xa7P3E3K4ZYsxGj-9k"  # <-- ՁԵՐ ԲՈՏԻ TOKEN-Ը

# 2. Տեղադրեք ձեր credentials.json ֆայլի ճիշտ անունը
SERVICE_ACCOUNT_FILE = 'credentials.json' 

# 3. Տեղադրեք ձեր Google Sheet ֆայլի ամբողջական URL-ը (հղումը)
SHEET_URL = "https://docs.google.com/spreadsheets/d/12y7hoaLCJiCSpqumovQWYF7Aqm_3LCQ-YklPJfs6Z38/edit?gid=1797135936#gid=1797135936"  # <-- ՁԵՐ GOOGLE SHEET-Ի ՀՂՈՒՄԸ
# -----------------------------------------------------------------


# Սահմանում ենք խոսակցության 7 փուլերը
ASK_NAME, ASK_PHONE, ASK_EMAIL, ASK_ORG, ASK_JOB_TITLE, ASK_GOAL, ASK_SOURCE = range(7)

# --- Google Sheets-ի միացում ---
try:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_url(SHEET_URL).sheet1
    print("Google Sheet-ը հաջողությամբ միացված է։")
except Exception as e:
    print(f"Google Sheet-ի սխալ: {e}")
    # Այստեղ exit() չենք անում, որպեսզի Render-ի լոգերում սխալը տեսնենք
    print("ՍՏՈՒԳԵՔ: credentials.json, SHEET_URL, Share, API settings...")
# -------------------------------------

# --- ՁԵՐ ԲՈՏԻ ԱՄԲՈՂՋ ԼՈԳԻԿԱՆ (առանց փոփոխության) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Բարև։ Գրանցման համար խնդրում եմ պատասխանել մի քանի հարցի։\n"
        "Դուք կարող եք ցանկացած պահի չեղարկել՝ գրելով /cancel։\n\n"
        "Խնդրում եմ նշել ձեր անունը։ (Name)"
    )
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Գրե՛ք ձեր հեռախոսահամարը։ (Phone Number)")
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Գրե՛ք ձեր Email հասցեն։ (Email)")
    return ASK_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Նշե՛ք ձեր կազմակերպությունը։ (Organization)")
    return ASK_ORG

async def get_org(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['org'] = update.message.text
    await update.message.reply_text("Նշե՛ք ձեր պաշտոնը։ (Job Title / Position)")
    return ASK_JOB_TITLE

async def get_job_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['job_title'] = update.message.text
    await update.message.reply_text("Ո՞րն է LinkedIn-ում ձեր հիմնական նպատակը։ (Your Main Goal for LinkedIn)")
    return ASK_GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['goal'] = update.message.text
    await update.message.reply_text("Ինչպե՞ս եք տեղեկացել այս ծրագրի մասին։ (How did you hear about this program?)")
    return ASK_SOURCE

async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_source = update.message.text
    user_data = context.user_data
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    row_to_insert = [
        current_time,
        user_data.get('name', ''),
        user_data.get('phone', ''),
        user_data.get('email', ''),
        user_data.get('org', ''),
        user_data.get('job_title', ''),
        user_data.get('goal', ''),
        user_source
    ]

    try:
        sh.append_row(row_to_insert)
        await update.message.reply_text(
            "Շնորհակալություն։ Ձեր տվյալներն ընդունված են։"
        )
    except Exception as e:
        print(f"Google Sheet-ում գրելու սխալ: {e}")
        await update.message.reply_text(
            "Տեղի ունեցավ սխալ։ Խնդրում եմ փորձել մի փոքր ուշ։"
        )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Գրանցումը չեղարկվեց։")
    return ConversationHandler.END

def run_bot():
    """Այս ֆունկցիան գործարկում է բոտը"""
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            ASK_ORG: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_org)],
            ASK_JOB_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_job_title)],
            ASK_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
            ASK_SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    print("Բոտը սկսում է աշխատել (polling)...")
    application.run_polling()


# --- ՀԻՄՆԱԿԱՆ ԳՈՐԾԱՐԿՈՒՄ ---
if __name__ == "__main__":
    print("1. Սկսում ենք Flask սերվերը նոր թրեդում...")
    # Միացնում ենք կայքը առանձին թրեդով, որպեսզի բոտին չխանգարի
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    print("2. Սկսում ենք Telegram բոտը հիմնական թրեդում...")
    # Միացնում ենք բոտը
    run_bot()
