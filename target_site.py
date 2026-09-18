#!/usr/bin/env python3
"""
Target Site Mock (Pure Python)
خادم محلي وهمي يمثل الموقع الهدف الذي يتم توجيه الطلبات إليه على المنفذ 5000
"""

from http.server import HTTPServer, BaseHTTPRequestHandler


class TargetSiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """عرض صفحة تسجيل الدخول عند فتح الرابط"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html_content = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>الموقع الهدف - تسجيل الدخول</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #eef2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 300px; }
                h2 { text-align: center; color: #2c3e50; margin-bottom: 20px; }
                label { font-size: 14px; color: #555; }
                input { width: 100%; padding: 10px; margin: 8px 0 16px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
                button { width: 100%; padding: 10px; background-color: #27ae60; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
                button:hover { background-color: #219150; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>تسجيل الدخول</h2>
                <form action="/login" method="POST">
                    <label>اسم المستخدم:</label>
                    <input type="text" name="username" required placeholder="ادخل اسم المستخدم">

                    <label>كلمة المرور:</label>
                    <input type="password" name="password" required placeholder="••••••••">

                    <label>رمز التحقق (MFA):</label>
                    <input type="text" name="mfa_code" required placeholder="123456">

                    <button type="submit">تسجيل الدخول</button>
                </form>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))

    def do_POST(self):
        """استقبال بيانات الدخول من المستخدم وإرجاع صفحة نجاح"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        response_html = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"><title>تم التسجيل</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #eef2f5;">
            <div style="background: white; display: inline-block; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h2 style="color: #27ae60;">تم تسجيل الدخول بنجاح في الموقع الهدف!</h2>
                <p>البيانات التي وصلتنا في السيرفر:</p>
                <code style="background: #f8f9fa; padding: 10px; border: 1px solid #ddd; display: block; dir: ltr;">{post_data}</code>
            </div>
        </body>
        </html>
        """
        self.wfile.write(response_html.encode('utf-8'))


def run():
    server_address = ('127.0.0.1', 5000)
    httpd = HTTPServer(server_address, TargetSiteHandler)
    print("[*] Target Server is running on http://127.0.0.1:5000 ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Stopping Target Server.")


if __name__ == '__main__':
    run()
