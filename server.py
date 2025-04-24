import json

from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Список картинок для демонстрации
images = [
    "static/photo_2025-03-13_21-08-05.jpg",
    "static/photo_2025-03-14_20-35-18.jpg",
    "static/photo_2025-03-14_20-35-26.jpg"
]

d = {}


@app.route('/')
def index():
    data = request.args.get("data")
    if data:
        data = json.loads(data)
    user_id = data['user_id']
    d[user_id] = d.get(user_id, 0)
    return render_template("index.html", user_id=user_id, image_url=images[d[user_id]],
                           current_image_index=d[user_id])


@app.route('/swipe', methods=['POST'])
def handle_swipe():
    data = request.get_json()
    direction = data.get("direction")
    user_id = data.get("user_id")
    print(data)

    if direction == 'right':
        d[user_id] = (d[user_id] + 1) % len(images)
    elif direction == 'left':
        d[user_id] = (d[user_id] - 1) % len(images)

    new_image_url = images[d[user_id]]

    return jsonify({"status": "ok", "new_image_url": new_image_url, "current_image_index": d[user_id]})


if __name__ == '__main__':
    app.run(debug=True)
