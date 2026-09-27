# -*- coding: utf-8 -*-
"""
منطق مشترک ربات Arshia Exchange.
این فایل هیچ حلقه یا سروری اجرا نمی‌کند؛ فقط توابع را در اختیار دو بخش دیگر می‌گذارد:
  - channel_check.py   (روی GitHub Actions هر چند دقیقه یک بار اجرا می‌شود)
  - api/index.py        (روی Vercel، هر بار که کاربر دکمه‌ای بزند اجرا می‌شود)
"""

import html
import math
import os
from datetime import datetime, timedelta, timezone

import requests

# ==========================================================
# مقادیر محرمانه: همیشه از متغیرهای محیطی خوانده می‌شوند
# (در GitHub: Settings -> Secrets, در Vercel: Settings -> Environment Variables)
# ==========================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")          # بدون @  مثال: Arshia_Exchange_bot
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@Arshiia_Exchange")
SUPPORT_USERNAME = os.environ.get("SUPPORT_USERNAME", "Arshiia_bh")

# ==========================================================
# قانون‌های ارسال قیمت در کانال (اعداد به تومان)
# ==========================================================
ROUND_TO = 100
JUMP_MOVE = 2000
JUMP_ROUND = 1000
STALE_MINUTES = 120
REPORT_GRACE_HOURS = 3
USE_PERSIAN_DIGITS = False

SYMBOL = "USDT_IRT"

# ==========================================================
# متن‌ها
# ==========================================================
BRAND = "Arshia Exchange"
BULLET = "◼️"
SEPARATOR = "──────────────"
BTN_CHANNEL = "🛒 ثبت سفارش"
BTN_LIVE = "💲 قیمت لحظه‌ای"
CHANNEL_CALL_TO_ACTION = "برای ثبت سفارش روی دکمه‌ی زیر بزنید 👇"

STYLE_ORDER = "success"
STYLE_INFO = "primary"

WELCOME = (
    "سلام {name} 👋\n"
    "به <b>Arshia Exchange</b> خوش آمدید.\n\n"
    "در این ربات می‌توانید:\n"
    "▫️ قیمت لحظه‌ای تتر را ببینید\n"
    "▫️ مراحل ثبت سفارش را قدم‌به‌قدم بخوانید\n"
    "▫️ سفارش خود را ثبت کنید و مستقیم با کارشناس در ارتباط باشید\n\n"
    "یکی از گزینه‌های زیر را انتخاب کنید 👇"
)

BOT_DESCRIPTION = (
    "به ربات Arshia Exchange خوش آمدید 👋\n\n"
    "در این ربات می‌توانید:\n"
    "• قیمت لحظه‌ای تتر را ببینید\n"
    "• مراحل ثبت سفارش را قدم‌به‌قدم بخوانید\n"
    "• سفارش خود را ثبت کنید و مستقیم با کارشناس در ارتباط باشید\n\n"
    "برای شروع، دکمه‌ی شروع (Start) را بزنید."
)
BOT_SHORT_DESCRIPTION = "Arshia Exchange | قیمت لحظه‌ای تتر و ثبت سفارش"
BOT_COMMANDS = [
    {"command": "start", "description": "شروع و نمایش منوی اصلی"},
    {"command": "price", "description": "قیمت لحظه‌ای تتر"},
]

BUY_TEXT = (
    "🛒 <b>ثبت سفارش</b>\n\n"
    "برای ثبت سفارش با کارشناس ما در ارتباط باشید. "
    "مقدار موردنظر و شبکه‌ی انتقال را همان‌جا اعلام کنید."
)
SUPPORT_TEXT = (
    "🎧 <b>پشتیبانی</b>\n\n"
    "برای هر سؤال یا مشکلی، مستقیم با کارشناس ما در ارتباط باشید."
)
FAQ_TEXT = (
    "❓ <b>سوالات متداول</b>\n\n"
    "<b>قیمت‌ها از کجا می‌آید؟</b>\n"
    "قیمت لحظه‌ای بر اساس نرخ روز بازار تتر نمایش داده می‌شود. "
    "قیمت نهایی هنگام ثبت سفارش توسط کارشناس تأیید می‌شود.\n\n"
    "<b>چطور سفارش بدهم؟</b>\n"
    "دکمه‌ی «ثبت سفارش» را بزنید و مقدار موردنظرتان را به کارشناس اعلام کنید.\n\n"
    "<b>شبکه‌ی انتقال را چطور انتخاب کنم؟</b>\n"
    "شبکه‌ی مقصد را هنگام سفارش اعلام کنید و مطمئن شوید کیف پولتان "
    "همان شبکه را پشتیبانی می‌کند."
)
GUIDE_SLIDES = [
    "<b>۱️⃣ ثبت درخواست</b>\n\n"
    "روی «ثبت سفارش» بزنید و مقدار موردنیازتان را به کارشناس اعلام کنید.",

    "<b>۲️⃣ تأیید قیمت و پرداخت</b>\n\n"
    "قیمت نهایی قبل از پرداخت برایتان تأیید می‌شود. "
    "بعد از تأیید، پرداخت را انجام دهید.",

    "<b>۳️⃣ دریافت تتر</b>\n\n"
    "بعد از تأیید پرداخت، تتر به کیف پول شما ارسال می‌شود.\n\n"
    "⚠️ شبکه و آدرس کیف پول را قبل از ارسال با دقت بررسی کنید.",
]

# ==========================================================
BITPIN_URLS = [
    "https://api.bitpin.ir/api/v1/mkt/tickers/",
    "https://api.bitpin.org/api/v1/mkt/tickers/",
]
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


# ---------------------------------------------------------- ابزارهای کمکی
def fa(value):
    text = str(value)
    return text.translate(FA_DIGITS) if USE_PERSIAN_DIGITS else text


def round_price(price):
    return int(math.floor(price / ROUND_TO + 0.5)) * ROUND_TO


def round_jump(price, last_price):
    if price >= last_price:
        return int(math.floor(price / JUMP_ROUND)) * JUMP_ROUND
    return int(math.ceil(price / JUMP_ROUND)) * JUMP_ROUND


def fmt_price(price):
    return fa(f"{int(price):,}")


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
            + (gy2 + 399) // 400 - 80 + gd + g_d_m[gm - 1])
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


def jalali_date(d):
    jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
    return fa(f"{jy}/{jm:02d}/{jd:02d}")


def now_fa():
    now = datetime.now(IRAN_TZ)
    return f"{jalali_date(now)} - {fa(now.strftime('%H:%M'))}"


def btn(text, data, style=None):
    button = {"text": text, "callback_data": data}
    if style:
        button["style"] = style
    return button


def url_btn(text, url, style=None):
    button = {"text": text, "url": url}
    if style:
        button["style"] = style
    return button


# ---------------------------------------------------------- بیت‌پین و تلگرام
def get_price():
    last_error = None
    for url in BITPIN_URLS:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            tickers = response.json()
            for item in tickers:
                if item.get("symbol") == SYMBOL:
                    return float(item["price"])
            similar = [t.get("symbol") for t in tickers if "USDT" in str(t.get("symbol"))]
            raise ValueError(f"نماد {SYMBOL} پیدا نشد. نمادهای مشابه: {similar[:10]}")
        except Exception as error:
            last_error = error
    raise last_error


def tg(method, **params):
    response = requests.post(f"{API}/{method}", json=params, timeout=20)
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"{method}: {data.get('description')}")
    return data["result"]


def send_channel(text):
    markup = {"inline_keyboard": [[
        url_btn(BTN_CHANNEL, f"https://t.me/{BOT_USERNAME}?start=channel", STYLE_ORDER),
        btn(BTN_LIVE, "live", STYLE_INFO),
    ]]}
    tg("sendMessage", chat_id=CHANNEL_ID, text=text, reply_markup=markup)


def build_price_text(price, now):
    return (
        f"💲 نرخ تتر: {fmt_price(price)} تومان\n"
        f"{SEPARATOR}\n"
        f"📅 تاریخ: {jalali_date(now)}\n"
        f"🕐 ساعت: {fa(now.strftime('%H:%M'))}\n\n"
        f"{CHANNEL_CALL_TO_ACTION}"
    )


def build_report_text(day, stats):
    return (
        "📌 گزارش نرخ تتر\n"
        f"📅 تاریخ: {jalali_date(day)}\n"
        f"{SEPARATOR}\n"
        f"{BULLET} شروع قیمت: {fmt_price(stats['open'])}\n"
        f"{BULLET} بیشترین قیمت: {fmt_price(stats['high'])}\n"
        f"{BULLET} کمترین قیمت: {fmt_price(stats['low'])}\n"
        f"{BULLET} پایان قیمت: {fmt_price(stats['close'])}\n\n"
        f"{CHANNEL_CALL_TO_ACTION}"
    )


def should_post(price, last_price, last_ts, now_ts):
    """
    (بله/خیر, دلیل, قیمتی که نمایش داده می‌شود)
    ۱) جهش >= ۲ هزار تومان ← فوراً، رُند به هزار تومان
    ۲) بعد از ۲ ساعت بدون پیام، اگر قیمت فرق داشت ← همان قیمت
    """
    if last_price is None:
        return True, "اولین قیمت", price
    minutes = (now_ts - last_ts) / 60
    if abs(price - last_price) >= JUMP_MOVE:
        return True, "جهش", round_jump(price, last_price)
    if price != last_price and minutes >= STALE_MINUTES:
        return True, "بروزرسانی بعد از دو ساعت", price
    return False, "", None


# ---------------------------------------------------------- صفحه‌های داخل ربات
def live_popup_text():
    try:
        now = datetime.now(IRAN_TZ)
        price = round_price(get_price())
        return (f"💲 نرخ لحظه‌ای تتر: {fmt_price(price)} تومان\n"
                f"🕐 ساعت: {fa(now.strftime('%H:%M'))}")
    except Exception:
        return "⚠️ الان امکان دریافت قیمت نیست. چند لحظه بعد دوباره امتحان کنید."


def screen_home(name=""):
    text = WELCOME.format(name=html.escape(name or "")).replace("سلام  ", "سلام ")
    keyboard = [
        [btn("🛒 ثبت سفارش", "buy", STYLE_ORDER)],
        [btn("💲 قیمت لحظه‌ای", "price", STYLE_INFO), btn("📖 راهنما", "guide:1", STYLE_INFO)],
        [btn("❓ سوالات متداول", "faq"), btn("🎧 پشتیبانی", "support", STYLE_INFO)],
    ]
    return text, {"inline_keyboard": keyboard}


def screen_buy():
    keyboard = [
        [url_btn("💬 ارتباط با کارشناس", f"https://t.me/{SUPPORT_USERNAME}", STYLE_ORDER)],
        [btn("💲 دیدن قیمت", "price", STYLE_INFO)],
        [btn("🏠 منوی اصلی", "home")],
    ]
    return BUY_TEXT, {"inline_keyboard": keyboard}


def screen_price():
    try:
        price = round_price(get_price())
        text = (
            "💲 <b>قیمت لحظه‌ای تتر</b>\n\n"
            f"💰 {fmt_price(price)} تومان\n"
            f"🕐 {now_fa()}\n\n"
            "قیمت به‌صورت لحظه‌ای تغییر می‌کند."
        )
    except Exception:
        text = "⚠️ الان امکان دریافت قیمت نیست. لطفاً چند لحظه بعد دوباره تلاش کنید."
    keyboard = [
        [btn("🔄 بروزرسانی", "price", STYLE_INFO)],
        [btn("🛒 ثبت سفارش", "buy", STYLE_ORDER)],
        [btn("🏠 منوی اصلی", "home")],
    ]
    return text, {"inline_keyboard": keyboard}


def screen_guide(n):
    total = len(GUIDE_SLIDES)
    n = max(1, min(total, n))
    dots = " ".join("●" if i == n else "○" for i in range(1, total + 1))
    text = f"📖 <b>راهنمای ثبت سفارش</b>\n{dots}\n\n{GUIDE_SLIDES[n - 1]}"
    nav = []
    if n > 1:
        nav.append(btn("قبلی", f"guide:{n - 1}"))
    if n < total:
        nav.append(btn("بعدی", f"guide:{n + 1}"))
    keyboard = [nav] if nav else []
    if n == total:
        keyboard.append([btn("🛒 شروع ثبت سفارش", "buy", STYLE_ORDER)])
    keyboard.append([btn("🏠 منوی اصلی", "home")])
    return text, {"inline_keyboard": keyboard}


def screen_faq():
    keyboard = [[btn("🛒 ثبت سفارش", "buy", STYLE_ORDER)], [btn("🏠 منوی اصلی", "home")]]
    return FAQ_TEXT, {"inline_keyboard": keyboard}


def screen_support():
    keyboard = [
        [url_btn("💬 ارتباط با پشتیبان", f"https://t.me/{SUPPORT_USERNAME}", STYLE_INFO)],
        [btn("🏠 منوی اصلی", "home")],
    ]
    return SUPPORT_TEXT, {"inline_keyboard": keyboard}


def render(data, name=""):
    if data == "buy":
        return screen_buy()
    if data == "price":
        return screen_price()
    if data == "faq":
        return screen_faq()
    if data == "support":
        return screen_support()
    if data.startswith("guide:"):
        return screen_guide(int(data.split(":")[1]))
    return screen_home(name)


# ---------------------------------------------------------- پردازش یک آپدیت تلگرام
def handle_update(update):
    """یک آپدیت (پیام یا کلیک دکمه) را پردازش می‌کند. برای وب‌هوک هم استفاده می‌شود."""
    if "message" in update:
        message = update["message"]
        if message.get("chat", {}).get("type") != "private":
            return
        name = message.get("from", {}).get("first_name", "")
        command = (message.get("text") or "").strip().lower()
        text, keyboard = screen_price() if command.startswith("/price") else screen_home(name)
        tg("sendMessage", chat_id=message["chat"]["id"], text=text,
           parse_mode="HTML", reply_markup=keyboard)

    elif "callback_query" in update:
        query = update["callback_query"]
        if query.get("data") == "live":
            tg("answerCallbackQuery", callback_query_id=query["id"],
               text=live_popup_text(), show_alert=True)
            return
        name = query.get("from", {}).get("first_name", "")
        text, keyboard = render(query.get("data", "home"), name)
        try:
            tg("editMessageText",
               chat_id=query["message"]["chat"]["id"],
               message_id=query["message"]["message_id"],
               text=text, parse_mode="HTML", reply_markup=keyboard)
        except RuntimeError as error:
            if "not modified" not in str(error):
                raise
        tg("answerCallbackQuery", callback_query_id=query["id"])
