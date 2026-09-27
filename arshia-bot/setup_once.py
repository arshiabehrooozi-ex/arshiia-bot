# -*- coding: utf-8 -*-
"""
این فایل را فقط یک بار، از روی لپ‌تاپ خودتان اجرا می‌کنید (بعد از اینکه Vercel آدرس داد).
کارش: ثبت توضیحات و دستورهای ربات در تلگرام + گفتن به تلگرام که آپدیت‌ها را
از این به بعد به آدرس Vercel بفرستد (webhook)، به‌جای این‌که ربات مدام بپرسد.

اجرا: python setup_once.py
"""

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"                       # توکن ربات
VERCEL_URL = "https://your-project-name.vercel.app/api"     # آدرس پروژه‌تان در Vercel + /api

import sys

import requests

from bitpin_common import BOT_COMMANDS, BOT_DESCRIPTION, BOT_SHORT_DESCRIPTION

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def call(method, **params):
    r = requests.post(f"{API}/{method}", json=params, timeout=20)
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"{method} failed: {data.get('description')}")
    return data["result"]


def main():
    if BOT_TOKEN.startswith("PUT_") or "your-project-name" in VERCEL_URL:
        print("❌ اول بالای همین فایل، توکن و آدرس Vercel را بگذارید.")
        sys.exit(1)

    me = call("getMe")
    print(f"✅ متصل شد به ربات @{me['username']}")

    call("setMyDescription", description=BOT_DESCRIPTION)
    call("setMyShortDescription", short_description=BOT_SHORT_DESCRIPTION)
    call("setMyCommands", commands=BOT_COMMANDS)
    print("✅ توضیحات و دستورهای ربات ثبت شد.")

    call("setWebhook", url=VERCEL_URL)
    print(f"✅ وب‌هوک روی {VERCEL_URL} تنظیم شد.")
    print("\nهمه چیز آماده است. حالا داخل تلگرام /start را به ربات بزنید.")


if __name__ == "__main__":
    main()
