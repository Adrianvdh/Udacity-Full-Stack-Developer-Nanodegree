import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json


db = SQLAlchemy(session_options={
    'expire_on_commit': False
})

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
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

'''
Question
'''
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

'''
Category

'''
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