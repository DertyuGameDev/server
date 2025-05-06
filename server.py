import threading
import json
import os
import random
import bot  # модуль с aiogram-ботом
import requests
from flask import Flask, request, render_template, jsonify

from data.liked import Liked
from data.u2u import U2U
from data.user import UserCard
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/love.db')


@app.route('/')
def index():
    data = request.args.get("data")
    if data:
        data = json.loads(data)
    user_id = data['user_id']
    db_sess = db_session.create_session()
    users = db_sess.query(UserCard).filter(UserCard.disabled == 0).filter(UserCard.tg_id != user_id)
    try:
        swiped = random.choice(list(users))
        capture = f'{swiped.name}, {swiped.old}' + (f' - {swiped.capture}' if swiped.capture != '-' else '')
        return render_template("index.html", user_id=user_id, swiped=swiped.tg_id, image_url=swiped.picture,
                               caption=capture)
    except Exception:
        return render_template("index.html", user_id=user_id, swiped=user_id,
                               image_url='static/img/default.jpg', caption='Никого нет в сети(')


@app.route('/swipe', methods=['POST'])
def handle_swipe():
    data = request.get_json()
    direction = data.get("direction")
    user_id = data.get("user_id")
    user_id_swiped = data.get("user_id_swiped")
    db_sess = db_session.create_session()
    if user_id == user_id_swiped and len(db_sess.query(UserCard).all()) == 1:
        return jsonify({
            'src': 'static/img/default.jpg',
            'caption': 'Никого нет в сети(',
            'user_id': user_id
        })

    liker = db_sess.query(UserCard).filter_by(tg_id=user_id).first()
    to_like = db_sess.query(UserCard).filter_by(tg_id=user_id_swiped).first()

    if not liker or not to_like:
        return jsonify({"status": "error", "message": "Пользователь не найден"}), 404

    reaction = U2U(
        user1=user_id,
        user2=user_id_swiped,
        like=1 if direction == 'like' else 0
    )
    db_sess.add(reaction)
    if direction == 'like':
        to_like.like += 1

        liked_entry = db_sess.query(Liked).filter_by(user1=user_id).first()
        if not liked_entry:
            liked_entry = Liked(user1=user_id, like_for=[user_id_swiped])
            db_sess.add(liked_entry)
        else:
            if user_id_swiped not in liked_entry.like_for:
                liked_entry.like_for.append(user_id_swiped)

        mutual = db_sess.query(U2U).filter_by(user1=user_id_swiped, user2=user_id, like=1).first()
        if mutual:
            bot.message_like({'user1': user_id, 'user2': user_id_swiped})
    available_users = db_sess.query(UserCard).filter(UserCard.disabled == 0).filter(UserCard.tg_id
                                                                                    != user_id).all()

    users_liked_by_user = db_sess.query(Liked).filter(Liked.user1 == user_id).first()
    liked_user_ids = set(users_liked_by_user.like_for) if users_liked_by_user else set()

    sorted_users = sorted(available_users, key=lambda user: (user.tg_id in liked_user_ids, user.tg_id))
    best = sorted_users[0]
    db_sess.commit()
    capture = f'{best.name}, {best.old}' + (f' - {best.capture}' if best.capture != '-' else '')
    return jsonify({"status": "ok", 'src': best.picture, 'user_id': best.tg_id, 'caption': capture})


def run_flask():
    app.run(debug=False, port=5000)


def run_bot():
    import asyncio
    asyncio.run(bot.main())


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    bot_thread = threading.Thread(target=run_bot)

    flask_thread.start()
    bot_thread.start()

    flask_thread.join()
    bot_thread.join()
