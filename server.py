import json
import random

from flask import Flask, request, render_template, jsonify
from data.liked import Liked
from data.u2u import U2U
from data.user import UserCard
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/love.db')

d = []


@app.route('/')
def index():
    data = request.args.get("data")
    if data:
        data = json.loads(data)
    user_id = data['user_id']
    db_sess = db_session.create_session()
    with db_sess.no_autoflush:
        me = db_sess.query(UserCard).filter(UserCard.tg_id == user_id).first()
        if me.disabled == 1:
            return render_template("disabled.html")
        users = db_sess.query(UserCard).filter(UserCard.disabled == 0).filter(UserCard.tg_id != user_id)
        try:
            swiped = random.choice(list(users))
            capture = f'{swiped.name}, {swiped.old}' + (f' - {swiped.capture}' if swiped.capture != '-' else '')
            db_sess.close()
            return render_template("index.html", user_id=user_id, swiped=swiped.tg_id, image_url=swiped.picture,
                                   caption=capture)
        except Exception:
            db_sess.close()
            return render_template("index.html", user_id=user_id, swiped=user_id,
                                   image_url='static/img/default.jpg', caption='Никого нет в сети(')


@app.route('/check_user', methods=['POST'])
def check_user():
    data = request.json
    user_id = data.get("user_id")

    db_sess = db_session.create_session()
    with db_sess.no_autoflush:
        user = db_sess.query(UserCard).filter(UserCard.tg_id == user_id).first()
        db_sess.close()
        return jsonify({"exists": user is not None})


@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    db_sess = db_session.create_session()
    with db_sess.no_autoflush:
        user = UserCard(**data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return jsonify({'status': 'ok'})


@app.route('/create_picture', methods=['POST'])
def create_picture():
    file = request.files.get('file')
    filename = file.filename
    file.save(filename)

    return jsonify({'status': 'ok', 'filename': filename})


@app.route('/get_events', methods=["GET"])
def get_events():
    f = d.copy()
    j = {'events': []}
    d.clear()
    for i in f:
        j['events'].append({'user1': i[0], 'user2': i[1]})
    return jsonify(j)


@app.route('/get_disabled', methods=["POST"])
def get_dis():
    data = request.json
    user_id = data.get("user_id")

    db_sess = db_session.create_session()
    with db_sess.no_autoflush:
        user = db_sess.query(UserCard).filter(UserCard.tg_id == user_id).first()
        db_sess.close()
        return jsonify({"disabled": user.disabled})


@app.route('/swipe', methods=['POST'])
def handle_swipe():
    data = request.get_json()
    direction = data.get("direction")
    user_id = int(data.get("user_id"))
    user_id_swiped = int(data.get("user_id_swiped"))
    db_sess = db_session.create_session()
    with db_sess.no_autoflush:
        if user_id == user_id_swiped and len(db_sess.query(UserCard).all()) == 1:
            return jsonify({
                'src': 'static/img/default.jpg',
                'caption': 'Никого нет в сети(',
                'user_id': user_id
            })

        liker = db_sess.query(UserCard).filter_by(tg_id=user_id).first()
        to_like = db_sess.query(UserCard).filter_by(tg_id=user_id_swiped).first()

        if not liker or not to_like:
            db_sess.close()
            return jsonify({"status": "error", "message": "Пользователь не найден"}), 404

        reaction = U2U(
            user1=user_id,
            user2=user_id_swiped,
            like=1 if direction == 'like' else 0
        )
        db_sess.add(reaction)
        print(3)
        db_sess.commit()
        if direction == 'like':
            to_like.like += 1

            liked_entry = db_sess.query(Liked).filter_by(user1=user_id).first()
            liked_entry1 = db_sess.query(Liked).filter_by(user1=user_id_swiped).first()
            if not liked_entry:
                liked_entry = Liked(user1=user_id, like_for=[user_id_swiped])
                db_sess.add(liked_entry)
            elif user_id_swiped not in liked_entry.like_for:
                liked_entry.like_for = liked_entry.like_for + [user_id_swiped]
            if not liked_entry1:
                liked_entry1 = Liked(user1=user_id_swiped, like_for=[])
                db_sess.add(liked_entry1)
            db_sess.commit()
            mutual2 = db_sess.query(Liked).filter_by(user1=user_id).first()
            mutual = db_sess.query(Liked).filter_by(user1=user_id_swiped).first()
            if user_id in mutual.like_for:
                if (user_id, user_id_swiped) not in d and (user_id_swiped, user_id) not in d:
                    d.append((user_id, user_id_swiped))
                    new_list = mutual.like_for.copy()
                    new_list.remove(user_id)
                    mutual.like_for = new_list

                    new_list = mutual2.like_for.copy()
                    new_list.remove(user_id_swiped)
                    mutual2.like_for = new_list
                    db_sess.commit()
        else:
            liked_entry = db_sess.query(Liked).filter_by(user1=user_id_swiped).first()
            if user_id in liked_entry.like_for:
                liked_entry.like_for.remove(user_id)
        available_users = db_sess.query(UserCard).filter(UserCard.disabled == 0).filter(UserCard.tg_id
                                                                                        != user_id).all()

        # users_liked_by_user = db_sess.query(Liked).filter(user_id in Liked.like_for).first()
        # if users_liked_by_user:
        #     list_users = []
        #     for i in users_liked_by_user:
        #
        # elif len(available_users) == 1:
        #     best = available_users[0]
        # else:
        if len(available_users) == 0:
            return jsonify({
                'src': 'static/img/default.jpg',
                'caption': 'Никого нет в сети(',
                'user_id': user_id
            })
        elif len(available_users) == 1:
            best = db_sess.query(UserCard).filter(UserCard.tg_id == user_id_swiped).first()
        elif len(available_users) == 2:
            best = db_sess.query(UserCard).filter(UserCard.tg_id != user_id_swiped).filter(
                UserCard.tg_id != user_id).first()
        else:
            l1 = db_sess.query(Liked).filter(user_id in Liked.like_for).all()
            l1 = list(filter(lambda x: x in available_users, l1))
            l2 = list(map(lambda x: x not in l1, available_users))
            sorted_list = l1 + l2
            sorted_list.remove(user_id_swiped)
            sorted_list.insert(-1, user_id_swiped)
            best = sorted_list[0]
        capture = f'{best.name}, {best.old}' + (f' - {best.capture}' if best.capture != '-' else '')
        db_sess.close()
        return jsonify({"status": "ok", 'src': best.picture, 'user_id': int(best.tg_id), 'caption': capture})


@app.route("/edit_user/<int:tg_id>", methods=["PUT"])
def edit_user(tg_id):
    db_sess = db_session.create_session()
    with db_sess.no_autoflush:
        user = db_sess.query(UserCard).filter(UserCard.tg_id == tg_id).first()
        keys = [
            "old",
            "name",
            "capture",
            "disabled"
        ]
        key = list(request.json.keys())[0]
        val = list(request.json.values())[0]
        if not user:
            return
        elif key not in keys:
            return
        if key == "disabled":
            exec(f"user.{key} = {int(val)}")
        else:
            exec(f"user.{key} = \"{val}\"")
        db_sess.commit()
        db_sess.close()
        return jsonify({"success": "ok"})


def run_flask():
    app.run(debug=False, port=5000)


run_flask()
