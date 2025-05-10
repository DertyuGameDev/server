from sqlalchemy.dialects.sqlite import JSON
from .db_session import SqlAlchemyBase
import sqlalchemy


class Liked(SqlAlchemyBase):
    __tablename__ = 'liked'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user1 = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    like_for = sqlalchemy.Column(JSON, default=[])

    def __repr__(self):
        return f"<UserCard {self.name} ({self.tg_id})>"
