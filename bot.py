import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "ваш_бот_токен"
WEATHER_API_KEY = "апи_ключ_сайта_погоды"

def get_keyboard():
    return ReplyKeyboardMarkup(
        [["Погода 🌤️", "Курс валют 💰"], ["Помощь ❓"]],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=get_keyboard()
    )

async def weather_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['last_action'] = 'weather'
    await update.message.reply_text("Введите название города:")

async def currency_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rates = get_currency_rates()
    await update.message.reply_text(rates, reply_markup=get_keyboard())

def get_currency_rates():
    try:
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        data = requests.get(url).json()
        usd = data["Valute"]["USD"]["Value"]
        eur = data["Valute"]["EUR"]["Value"]
        return f"💵 Курс ЦБ РФ:\nUSD: {usd} RUB\nEUR: {eur} RUB"
    except:
        return "Не удалось получить курс валют. Попробуйте позже."

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('last_action') == 'weather':
        await get_weather(update, context)
        context.user_data['last_action'] = None
    else:
        await update.message.reply_text("Выберите действие на клавиатуре", reply_markup=get_keyboard())

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={'76fc29311d991c61f83c3e2ed9c19f1c'}&units=metric&lang=ru"
        response = requests.get(url).json()
        
        if response.get("cod") != 200:
            await update.message.reply_text("Город не найден! Попробуйте еще раз", reply_markup=get_keyboard())
            return
            
        weather_data = {
            'city': response['name'],
            'temp': response['main']['temp'],
            'feels_like': response['main']['feels_like'],
            'description': response['weather'][0]['description']
        }
        
        message = (
            f"Погода в {weather_data['city']}:\n"
            f"🌡 Температура: {weather_data['temp']}°C\n"
            f"☁️ {weather_data['description'].capitalize()}"
        )
        
        await update.message.reply_text(message, reply_markup=get_keyboard())
    except:
        await update.message.reply_text("Ошибка при получении погоды", reply_markup=get_keyboard())

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Погода 🌤️$"), weather_request))
    app.add_handler(MessageHandler(filters.Regex("^Курс валют 💰$"), currency_request))
    app.add_handler(MessageHandler(filters.Regex("^Помощь ❓$"), 
                   lambda u, c: u.message.reply_text("Этот бот показывает погоду и курс валют", reply_markup=get_keyboard())))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()