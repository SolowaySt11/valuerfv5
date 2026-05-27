from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

TOKEN = "8847119724:AAGudqiuhIdAoehPBwTCnJKywUmeoKxb7_E"

# ---------- КУРСЫ ВАЛЮТ ----------
def get_currency_rate(currency_code):
    url = "https://api.exchangerate-api.com/v4/latest/RUB"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        rub_per_currency = 1 / data['rates'][currency_code]
        return round(rub_per_currency, 2)
    except:
        return None

# ---------- ЦЕНЫ МЕТАЛЛОВ ----------
def get_metal_price(metal_name):
    """metal_name: 'XAU' (золото), 'XAG' (серебро), 'XPT' (платина), 'XPD' (палладий)"""
    url = f"https://api.gold-api.com/price/{metal_name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            price_usd = data['price']
            usd_rate = get_currency_rate("USD")
            if usd_rate:
                return round(price_usd * usd_rate / 31.1, 2)
        return None
    except:
        return None

# ---------- ЦЕНЫ АКЦИЙ ----------
def get_stock_price(ticker):
    """ticker: 'GAZP', 'SBER', 'LKOH', 'YDEX'"""
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/tqbr/securities/{ticker}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = data['marketdata']['data'][0][2]
            return round(price, 2)
        else:
            print(f"MOEX ответил {response.status_code} для {ticker}")
            return None
    except Exception as e:
        print(f"Ошибка при запросе {ticker}: {e}")
        return None

# ---------- МЕНЮ АКЦИЙ ----------
async def stocks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🛢️ Газпром", callback_data="GAZP")],
        [InlineKeyboardButton("🏦 Сбербанк", callback_data="SBER")],
        [InlineKeyboardButton("⛽ Лукойл", callback_data="LKOH")],
        [InlineKeyboardButton("🌐 Яндекс", callback_data="YDEX")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📈 Выбери акцию:", reply_markup=reply_markup)

# ---------- ГЛАВНОЕ МЕНЮ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🪙 Драгоценные металлы", callback_data="metals")],
        [InlineKeyboardButton("💵 Валюты", callback_data="currencies")],
        [InlineKeyboardButton("📈 Акции", callback_data="stocks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏭 *Инвестиционный дашборд*\n\n"
        "Здравствуй! Выбери категорию:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ---------- МЕНЮ ДРАГМЕТАЛЛОВ ----------
async def metals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🥇 Золото", callback_data="gold")],
        [InlineKeyboardButton("🥈 Серебро", callback_data="silver")],
        [InlineKeyboardButton("💍 Платина", callback_data="PLAT")],
        [InlineKeyboardButton("🪨 Палладий", callback_data="PLD")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🪙 Выбери драгоценный металл:", reply_markup=reply_markup)

# ---------- МЕНЮ ВАЛЮТ ----------
async def currencies_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🇺🇸 Доллар", callback_data="USD")],
        [InlineKeyboardButton("🇪🇺 Евро", callback_data="EUR")],
        [InlineKeyboardButton("🇨🇳 Юань", callback_data="CNY")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💵 Выбери валюту:", reply_markup=reply_markup)

# ---------- ОБРАБОТЧИК КНОПОК ----------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await start(update, context)
        return

    if data == "metals":
        await metals_menu(update, context)
        return

    if data == "currencies":
        await currencies_menu(update, context)
        return

    if data == "stocks":
        await stocks_menu(update, context)
        return

    # ========== МЕТАЛЛЫ ==========
    if data == "gold":
        price = get_metal_price("XAU")
        text = f"🥇 Золото: {price} ₽" if price else "❌ Не удалось получить цену золота"
        await query.edit_message_text(text)
        return

    if data == "silver":
        price = get_metal_price("XAG")
        text = f"🥈 Серебро: {price} ₽" if price else "❌ Не удалось получить цену серебра"
        await query.edit_message_text(text)
        return

    if data == "PLAT":
        price = get_metal_price("XPT")
        text = f"💍 Платина: {price} ₽" if price else "❌ Не удалось получить цену платины"
        await query.edit_message_text(text)
        return

    if data == "PLD":
        price = get_metal_price("XPD")
        text = f"🪨 Палладий: {price} ₽" if price else "❌ Не удалось получить цену палладия"
        await query.edit_message_text(text)
        return

    # ========== ВАЛЮТЫ ==========
    if data in ["USD", "EUR", "CNY"]:
        rate = get_currency_rate(data)
        if rate:
            if data == "USD":
                text = f"🇺🇸 Доллар США: {rate} ₽"
            elif data == "EUR":
                text = f"🇪🇺 Евро: {rate} ₽"
            else:
                text = f"🇨🇳 Китайский юань: {rate} ₽"
        else:
            text = "❌ Не удалось получить курс"
        await query.edit_message_text(text)
        return

    # ========== АКЦИИ ==========
    if data in ["GAZP", "SBER", "LKOH", "YNDX"]:
        price = get_stock_price(data)
        if price:
            if data == "GAZP":
                name = "🛢️ Газпром"
            elif data == "SBER":
                name = "🏦 Сбербанк"
            elif data == "LKOH":
                name = "⛽ Лукойл"
            else:
                name = "🌐 Яндекс"
            text = f"{name}: {price} ₽"
        else:
            text = f"❌ Не удалось получить цену для {data}"
        await query.edit_message_text(text)
        return

# ---------- HELP ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используй /start для начала работы.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()