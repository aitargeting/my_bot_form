import gspread
from datetime import datetime  # Ժամի համար
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# --- ԿԱՐԳԱՎՈՐՈՒՄՆԵՐ (Խմբագրեք այս բաժինը) ---------------------
# 1. Տեղադրեք ձեր BotFather-ից ստացած TOKEN-ը
BOT_TOKEN = "8048043305:AAEw8sVXR26k3Gt06Xa7P3E3K4ZYsxGj-9k"  # <-- ՁԵՐ ԲՈՏԻ TOKEN-Ը

# 2. Տեղադրեք ձեր credentials.json ֆայլի ճիշտ անունը
SERVICE_ACCOUNT_FILE = 'credentials.json' 

# 3. Տեղադրեք ձեր Google Sheet ֆայլի ամբողջական URL-ը (հղումը)
SHEET_URL = "https://docs.google.com/spreadsheets/d/12y7hoaLCJiCSpqumovQWYF7Aqm_3LCQ-YklPJfs6Z38/edit?gid=1797135936#gid=1797135936"  # <-- ՁԵՐ GOOGLE SHEET-Ի ՀՂՈՒՄԸ
# -----------------------------------------------------------------


# Սահմանում ենք խոսակցության 7 փուլերը
# (Name, Phone, Email, Org, Job, Goal, Source)
ASK_NAME, ASK_PHONE, ASK_EMAIL, ASK_ORG, ASK_JOB_TITLE, ASK_GOAL, ASK_SOURCE = range(7)

# --- Google Sheets-ի միացում ---
try:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_url(SHEET_URL).sheet1  # Բացում ենք URL-ով
    print("Google Sheet-ը հաջողությամբ միացված է։")
except Exception as e:
    print(f"Google Sheet-ի սխալ: {e}")
    print("ՍՏՈՒԳԵՔ: 1. 'credentials.json' ֆայլը կա՞։ 2. SHEET_URL-ը ճիշտ է։ 3. Share արե՞լ եք շիթը service account-ի email-ի հետ (Editor իրավունքով)։ 4. Google Sheets API-ն և Google Drive API-ն միացված են Google Cloud-ում։")
    exit()
# -------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Սկսում է խոսակցությունը և հարցնում անունը։"""
    await update.message.reply_text(
        "Բարև։ Գրանցման համար խնդրում եմ պատասխանել մի քանի հարցի։\n"
        "Դուք կարող եք ցանկացած պահի չեղարկել՝ գրելով /cancel։\n\n"
        "Խնդրում եմ նշել ձեր անունը։ (Name)"
    )
    return ASK_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Պահպանում է անունը և հարցնում հեռախոսահամարը։"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Գրե՛ք ձեր հեռախոսահամարը։ (Phone Number)")
    return ASK_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Պահպանում է հեռախոսը և հարցնում Email։"""
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Գրե՛ք ձեր Email հասցեն։ (Email)")
    return ASK_EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Պահպանում է Email-ը և հարցնում կազմակերպությունը։"""
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Նշե՛ք ձեր կազմակերպությունը։ (Organization)")
    return ASK_ORG


async def get_org(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Պահպանում է կազմակերպությունը և հարցնում պաշտոնը։"""
    context.user_data['org'] = update.message.text
    await update.message.reply_text("Նշե՛ք ձեր պաշտոնը։ (Job Title / Position)")
    return ASK_JOB_TITLE


async def get_job_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Պահպանում է պաշտոնը և հարցնում նպատակը։"""
    context.user_data['job_title'] = update.message.text
    await update.message.reply_text("Ո՞րն է LinkedIn-ում ձեր հիմնական նպատակը։ (Your Main Goal for LinkedIn)")
    return ASK_GOAL


async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Պահպանում է նպատակը և հարցնում աղբյուրը։"""
    context.user_data['goal'] = update.message.text
    await update.message.reply_text("Ինչպե՞ս եք տեղեկացել այս ծրագրի մասին։ (How did you hear about this program?)")
    return ASK_SOURCE


async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Պահպանում է վերջին հարցը, գրում ամեն ինչ Google Sheet-ում և ավարտում։"""
    
    user_source = update.message.text
    user_data = context.user_data
    
    # Ստանում ենք ընթացիկ ժամը ձեր ուզած ֆորմատով
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    # Պատրաստում ենք տողը (8 սյունակ)
    row_to_insert = [
        current_time,                        # ՍՅՈՒՆԱԿ 1 (Նոր)
        user_data.get('name', ''),           # Սյունակ 2
        user_data.get('phone', ''),          # Սյունակ 3
        user_data.get('email', ''),          # Սյունակ 4
        user_data.get('org', ''),            # Սյունակ 5
        user_data.get('job_title', ''),      # Սյունակ 6
        user_data.get('goal', ''),           # Սյունակ 7
        user_source                          # Սյունակ 8 (վերջին պատասխանը)
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
    """Չեղարկում է ընթացիկ գործողությունը։"""
    context.user_data.clear()
    await update.message.reply_text(
        "Գրանցումը չեղարկվեց։"
    )
    return ConversationHandler.END


def main() -> None:
    """Գործարկում է բոտը։"""
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

    print("Բոտը սկսում է աշխատել...") # <--- Այս տողը պետք է հայտնվի
    application.run_polling()


# Շատ կարևոր է, որ այս երկու տողը լինեն ֆայլի վերջում
if __name__ == "__main__":
    main()