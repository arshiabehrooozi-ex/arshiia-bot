# -*- coding: utf-8 -*-
"""
این فایل را خودتان اجرا نمی‌کنید؛ GitHub Actions هر چند دقیقه یک بار آن را اجرا می‌کند
(تنظیماتش در .github/workflows/channel.yml است).
هر بار: قیمت را می‌گیرد، طبق قانون‌ها تصمیم می‌گیرد، در صورت لزوم در کانال می‌فرستد
و state.json را بروزرسانی می‌کند (که GitHub خودش دوباره در مخزن ذخیره می‌کند).
"""

import json
import os
import time
from datetime import date, datetime

from bitpin_common import (
    IRAN_TZ, REPORT_GRACE_HOURS, ROUND_TO,
    build_price_text, build_report_text, fmt_price, get_price,
    round_price, send_channel, should_post,
)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

DEFAULT_STATE = {
    "last_price": None, "last_ts": 0, "day": None,
    "open": None, "high": None, "low": None, "close": None,
}


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return {**DEFAULT_STATE, **json.load(f)}
    except Exception:
        return dict(DEFAULT_STATE)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    state = load_state()
    now = datetime.now(IRAN_TZ)
    today = now.date().isoformat()
    price = round_price(get_price())

    if state["day"] != today:
        if state["open"] is not None and now.hour < REPORT_GRACE_HOURS:
            send_channel(build_report_text(date.fromisoformat(state["day"]), state))
            print("گزارش روزانه ارسال شد.")
        state.update(day=today, open=price, high=price, low=price, close=price,
                     last_price=None)
    else:
        state["high"] = max(state["high"], price)
        state["low"] = min(state["low"], price)
        state["close"] = price

    post, reason, shown = should_post(price, state["last_price"], state["last_ts"], time.time())
    if post:
        send_channel(build_price_text(shown, now))
        state.update(last_price=shown, last_ts=time.time())
        print(f"قیمت ارسال شد: {fmt_price(shown)} تومان ({reason})")
    else:
        print(f"قیمت فعلی {fmt_price(price)} تومان - ارسال لازم نبود.")

    save_state(state)


if __name__ == "__main__":
    main()
