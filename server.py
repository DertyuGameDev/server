from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Список картинок для демонстрации
images = [
    "https://placekitten.com/300/300",
    "https://placekitten.com/300/301",
    "https://placekitten.com/300/302"
]


@app.route('/')
def index():
    user_id = request.args.get("user_id")

    # Простейшая авторизация
    if not user_id:
        return "⛔ Доступ запрещен. Неверный user_id.", 403

    # Начальная картинка
    current_image_index = 0
    return render_template("index.html", user_id=user_id, image_url=images[current_image_index],
                           current_image_index=current_image_index)


@app.route('/swipe', methods=['POST'])
def handle_swipe():
    data = request.get_json()
    direction = data.get("direction")
    current_image_index = data.get("current_image_index")

    if direction == 'right':
        current_image_index = (current_image_index + 1) % len(images)  # Следующая картинка
    elif direction == 'left':
        current_image_index = (current_image_index - 1) % len(images)  # Предыдущая картинка

    new_image_url = images[current_image_index]

    return jsonify({"status": "ok", "new_image_url": new_image_url, "current_image_index": current_image_index})


if __name__ == '__main__':
    app.run(debug=True)
