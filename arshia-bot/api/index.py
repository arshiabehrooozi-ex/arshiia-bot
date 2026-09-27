# -*- coding: utf-8 -*-
"""
این فایل روی Vercel اجرا می‌شود، نه روی لپ‌تاپ شما.
هر بار که کاربر داخل ربات پیامی بفرستد یا دکمه‌ای بزند، تلگرام یک درخواست
به همین آدرس می‌فرستد (وب‌هوک) و این فایل جواب می‌دهد.
"""

import json
from http.server import BaseHTTPRequestHandler

from bitpin_common import handle_update


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            update = json.loads(raw or b"{}")
            handle_update(update)
        except Exception as error:
            print(f"خطا در پردازش آپدیت: {error}")
        # تلگرام فقط یک 200 ساده می‌خواهد؛ محتوای جواب برایش مهم نیست
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Arshia Exchange webhook is running ✅".encode("utf-8"))
