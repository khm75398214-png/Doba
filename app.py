from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import time

app = Flask(__name__)

# Firebase 연결
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

ADMINS = ["헤헿"]  # 관리자 닉네임
ALLOWED_ROOM = "AT클랜"

def is_admin(sender):
    return sender in ADMINS

@app.route("/")
def home():
    return "AT1 놀이봇 서버 ON"

@app.route("/bot", methods=["POST"])
def bot():
    data = request.get_json()

    room = data.get("room", "")
    msg = data.get("msg", "")
    sender = data.get("sender", "")

    if room != ALLOWED_ROOM:
        return jsonify({"reply": ""})

    # 핑
    if msg == "!핑":
        return jsonify({"reply": "🏓 퐁!"})

    # 반복 중지
    if msg == "!반복중지":
        if not is_admin(sender):
            return jsonify({"reply": "❌ 관리자만 사용할 수 있어요."})

        db.collection("bot").document("repeat").set({
            "running": False
        })

        return jsonify({"reply": "🛑 반복 공지를 중지했어요."})

    # 사용법: !반복공지 3 내용
    if msg.startswith("!반복공지 "):
        if not is_admin(sender):
            return jsonify({"reply": "❌ 관리자만 사용할 수 있어요."})

        parts = msg.split(" ")
        if len(parts) < 3:
            return jsonify({"reply": "❌ 사용법: !반복공지 3 내용"})

        try:
            count = int(parts[1])
        except:
            return jsonify({"reply": "❌ 횟수는 숫자로 입력해주세요."})

        text = " ".join(parts[2:])

        if count < 1 or count > 5:
            return jsonify({"reply": "❌ 횟수는 1~5까지만 가능해요."})

        db.collection("bot").document("repeat").set({
            "running": True
        })

        replies = []
        replies.append("🚀 반복 공지 시작")

        for i in range(count):
            doc = db.collection("bot").document("repeat").get()
            running = doc.to_dict().get("running", False)

            if not running:
                replies.append("🛑 중지됨")
                break

            replies.append(text)
            time.sleep(1.2)

        db.collection("bot").document("repeat").set({
            "running": False
        })

        replies.append("✅ 반복 공지 완료")

        return jsonify({"reply": "\n\n".join(replies)})

    return jsonify({"reply": ""})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)