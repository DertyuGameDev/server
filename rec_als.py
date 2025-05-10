import pandas as pd
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares
from data import db_session
from data.u2u import U2U


def als_rec(user_id, num_recommendations, db_sess):
    likes = db_sess.query(U2U).filter(U2U.like == 1).all()
    df = pd.DataFrame([{
        'user1': like.user1,
        'user2': like.user2,
        'like': like.like
    } for like in likes])

    if df.empty:
        return []

    user_ids = list(set(df['user1']).union(df['user2']))
    user_id_map = {tg_id: i for i, tg_id in enumerate(user_ids)}
    reverse_user_id_map = {i: tg_id for tg_id, i in user_id_map.items()}

    rows = df['user1'].map(user_id_map)
    cols = df['user2'].map(user_id_map)
    data = df['like']

    num_users = len(user_ids)
    user_item_matrix = coo_matrix((data, (rows, cols)), shape=(num_users, num_users)).tocsr()

    model = AlternatingLeastSquares(factors=20, regularization=0.1, iterations=15)
    model.fit(user_item_matrix.T)

    if user_id not in user_id_map:
        return []

    internal_id = user_id_map[user_id]

    recommendations = model.recommend(
        userid=internal_id,
        user_items=user_item_matrix[internal_id],
        N=num_recommendations,
        filter_already_liked_items=True,
        filter_items=[internal_id],
        recalculate_user=True
    )

    recommended_tg_ids = [reverse_user_id_map[i] for i, score in zip(*recommendations)]
    while user_id in recommended_tg_ids:
        recommended_tg_ids.remove(user_id)
    db_sess.close()
    return recommended_tg_ids
