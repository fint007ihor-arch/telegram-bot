from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = "8688428177:AAEIbKNwOKlSQJMBtG-3XCjOrFCHa0ZGkDY"
ADMIN_ID = 5763255961


# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вітаю! 👋\n\n"
        "Мене звати Дейнеріс — я бот-помічник Ігоря Олександровича.\n\n"
        "Підкажіть, будь ласка:\n"
        "🔹 Ви звернулися з особистого питання\n"
        "🔹 чи з питання малярних робіт?\n\n"
        "Напишіть:\n"
        "👉 особисте\n"
        "👉 або ремонт"
    )
    context.user_data["step"] = "choice"


# логіка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    step = context.user_data.get("step")
    user = update.message.from_user

    if step == "choice":
        if "особист" in text:
            context.user_data["step"] = "personal"
            await update.message.reply_text(
                "Напишіть, будь ласка, ваше повідомлення.\n\n"
                "Ігор Олександрович отримає його та відповість, коли буде вільний 🙌"
            )
        elif "ремонт" in text:
            context.user_data["step"] = "service"
            await update.message.reply_text(
                "Оберіть, будь ласка, тип робіт:\n\n"
                "1️⃣ Весь комплекс малярних робіт\n"
                "2️⃣ Фарбування\n"
                "3️⃣ Переробки після недоброякісних майстрів\n\n"
                "Напишіть цифру (1, 2 або 3)"
            )
        else:
            await update.message.reply_text(
                "Будь ласка, напишіть 'особисте' або 'ремонт' 😊"
            )

    elif step == "personal":
        await update.message.reply_text(
            "Дякую! 🙌\n\n"
            "Ігор Олександрович відповість вам, коли буде вільний."
        )
        # ⬇️ Пересилка особистого повідомлення
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 ОСОБИСТЕ ПОВІДОМЛЕННЯ\n\n"
                 f"👤 Від: {user.full_name} (@{user.username})\n"
                 f"💬 Текст: {update.message.text}"
        )

    elif step == "service":
        if text == "1":
            context.user_data["service"] = "комплекс"
            price_text = "💰 Вартість: від 800 грн/м²"
        elif text == "2":
            context.user_data["service"] = "фарбування"
            price_text = "💰 Вартість: уточнюється"
        elif text == "3":
            context.user_data["service"] = "переробки"
            price_text = "💰 Вартість: після огляду"
        else:
            await update.message.reply_text("Введіть 1, 2 або 3")
            return

        context.user_data["step"] = "area"
        await update.message.reply_text(
            f"{price_text}\n\n"
            "Щоб розрахувати точніше — відповідайте 👇\n\n"
            "1️⃣ Яка площа (м²)?"
        )

    elif step == "area":
        context.user_data["area"] = text
        context.user_data["step"] = "date"
        await update.message.reply_text("2️⃣ Коли плануєте почати?")

    elif step == "date":
        context.user_data["date"] = text
        context.user_data["step"] = "location"
        await update.message.reply_text("3️⃣ Вкажіть локацію 📍")

    elif step == "location":
        context.user_data["location"] = text
        context.user_data["step"] = None
        await update.message.reply_text(
            "Дякую за звернення! 🙌\n\n"
            "Ігор Олександрович вже отримав вашу заявку і зв'яжеться з вами найближчим часом ✅"
        )
        # ⬇️ Пересилка заявки на ремонт
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔨 НОВА ЗАЯВКА НА РЕМОНТ\n\n"
                 f"👤 Від: {user.full_name} (@{user.username})\n"
                 f"🛠 Послуга: {context.user_data.get('service')}\n"
                 f"📐 Площа: {context.user_data.get('area')} м²\n"
                 f"📅 Дата: {context.user_data.get('date')}\n"
                 f"📍 Локація: {context.user_data.get('location')}"
        )

    else:
        await update.message.reply_text("Напишіть /start 😊")


app = (
    ApplicationBuilder()
    .token(TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
