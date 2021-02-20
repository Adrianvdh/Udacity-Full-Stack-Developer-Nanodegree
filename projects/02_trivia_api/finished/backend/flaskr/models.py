from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(session_options={
    'expire_on_commit': False
})


def setup_db(app):
    """
    binds a flask application and a SQLAlchemy service
    """
    db.app = app
    db.init_app(app)
    db.create_all()
    return db


class BaseModel(db.Model):
    __abstract__ = True

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Question(BaseModel):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


class Category(BaseModel):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return self.type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
