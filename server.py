from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    user_id = request.args.get("user_id")

    # Простейшая авторизация
    if user_id != "123":
        return "⛔ Доступ запрещен. Неверный user_id.", 403

    return render_template("index.html", user_id=user_id)


@app.route('/swipe', methods=['POST'])
def handle_swipe():
    data = request.get_json()
    user_id = data.get("user_id")
    direction = data.get("direction")
    print(f"Пользователь {user_id} свайпнул: {direction}")
    return jsonify({"status": "ok", "received": direction})


if __name__ == '__main__':
    app.run(debug=True)
