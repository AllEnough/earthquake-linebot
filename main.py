# 主程式入口
from flask import Flask, request
import threading
import os
from line_bot import handle_line_event
from earthquake import quake_check_loop

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    return handle_line_event(signature, body)

if __name__ == "__main__":
    threading.Thread(target=quake_check_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)