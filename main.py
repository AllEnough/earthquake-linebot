# 主程式入口
from flask import Flask
from earthquake import quake_check_loop
from line_bot import handle_webhook
import threading
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    return handle_webhook()

if __name__ == "__main__":
    threading.Thread(target=quake_check_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
