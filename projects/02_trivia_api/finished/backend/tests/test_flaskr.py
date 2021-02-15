import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from typing import List
from flaskr import create_app
from flaskr.models import setup_db, Question, Category, db


def create_categories(db):
    animals = Category(type='Animals')
    animals.insert()
    pop_culture = Category(type='Pop Culture')
    pop_culture.insert()
    sports = Category(type='Sports')
    sports.insert()
    return [animals, pop_culture, sports]

def create_questions(db, count=12):
    some_category = Category(type='Some Category')
    some_category.insert()
    
    questions = []
    for index in range(count):
        question = Question(
            question=f'The question? {index}', answer='The answer',
            category=some_category.id, difficulty=5
        )
        question.insert()
        questions.append(question)    
    return questions, some_category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app, self.db = create_app('tests.config')
        self.client = self.app.test_client
    
    def tearDown(self):
        """Executed after reach test"""
        self.db.session.query(Category).delete()
        self.db.session.query(Question).delete()
        self.db.session.commit()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_hello_world(self):
        res = self.client().get('/')

        assert res.status_code == 200
        assert res.data == b'Hello world'

    def test_get_categories(self):
        """
        Test GET /categories endpoint. This should return a json
        object containing a list of `categories`, the `total` count and if the
        request was a `success` or failure.
        """
        categories = create_categories(self.db)
        
        res = self.client().get('/categories')
        
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data == {
            'categories': [
                cat.type for cat in categories
            ],
            'total_categories': len(categories),
            'success': True
        }

    def test_get_questions(self):
        questions_list, category = create_questions(self.db, count=12)
        categories = create_categories(self.db)
        categories.append(category)
        categories.sort(key=lambda cat: cat.type)

        res = self.client().get('/questions')

        assert res.status_code == 200

        data = json.loads(res.data)
        assert len(data['questions']) == 10  # page limit
        assert data == {
            'questions': [
                question.format() for question in questions_list[:10]
            ],
            'total_questions': len(questions_list),
            'categories': [
                cat.type for cat in categories
            ]
        }

    def test_get_questions_paginated_next_page(self):
        questions_list, category = create_questions(self.db, count=12)
        categories = create_categories(self.db)
        categories.append(category)
        categories.sort(key=lambda cat: cat.type)

        res = self.client().get('/questions?page=2')

        assert res.status_code == 200

        data = json.loads(res.data)
        assert len(data['questions']) == 2  # page limit
        assert data == {
            'questions': [
                question.format() for question in questions_list[10:12]
            ],
            'total_questions': len(questions_list),
            'categories': [
                cat.type for cat in categories
            ]
        }
    
    def test_get_category_questions(self):
        questions_list, category = create_questions(self.db, count=12)

        res = self.client().get(f'/categories/{category.id}/questions')

        assert res.status_code == 200

        data = json.loads(res.data)
        assert len(data['questions']) == 10  # page limit
        assert data == {
            'questions': [
                question.format() for question in questions_list[:10]
            ],
            'total_questions': len(questions_list),
            'current_category': category.type
        }
    
    def test_questions_search(self):
        question1 = Question(question='How long is a mile in kilometers?',
                             answer='Answer',
                             category='Math',
                             difficulty=5)
        question1.insert()
        question2 = Question(question='How many centimeters is an inch?',
                             answer='Answer',
                             category='Math',
                             difficulty=5)
        question2.insert()

        search_term = 'kilometers'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})

        assert res.status_code == 200
        data = json.loads(res.data)
        assert len(data['questions']) == 1
        assert data == {
            'questions': [question1.format()],
            'total_questions': 1
        }

    def test_delete_question_by_id(self):
        question = Question(question='How long is a mile in kilometers?',
                            answer='Answer',
                            category='Math',
                            difficulty=5)
        question.insert()

        res = self.client().delete(f'/questions/{question.id}')

        assert res.status_code == 200
        data = json.loads(res.data)
        assert data == {
            'success': True,
            'deleted': question.id
        }
    
    def test_create_question(self):
        some_category = Category(type='Some Category')
        some_category.insert()

        res = self.client().post('/questions', json={
            'question': 'How long is a mile in kilometers?',
            'answer': 'Answer',
            'category': some_category.id,
            'difficulty': 5
        })

        assert res.status_code == 201
        data = json.loads(res.data)
        assert data['id']
        created_question = Question.query.get(data['id'])
        assert created_question.question == data['question']
        assert created_question.answer == data['answer']
        assert created_question.category == data['category']
        assert created_question.difficulty == data['difficulty']
        
    def test_create_question_with_errors(self):
        res = self.client().post('/questions', json={
            'question': '',
            'answer': '',
            'category': '',
            'difficulty': ''
        })

        assert res.status_code == 400
        data = json.loads(res.data)
        assert data['errors'] == [
            {'question': 'Question field cannot be blank!'},
            {'answer': 'Answer field cannot be blank!'},
            {'category': 'Category field cannot be blank!'},
            {'difficulty': 'Difficulty field cannot be blank!'}
        ]
        
    def test_play_quiz(self):
        questions_list1, category1 = create_questions(self.db, count=5)
        questions_list2, category2 = create_questions(self.db, count=5)
        
        res = self.client().post('/quizzes', json={
            'previous_questions': [
                questions_list2[0].id,
                questions_list2[1].id,
                questions_list2[3].id,
                questions_list2[4].id,
            ],
            'quiz_category': category2.id
        })

        assert res.status_code == 200
        data = json.loads(res.data)

        question = questions_list2[2].format()
        assert data['question'] == question
    
    def test_play_quiz_finish(self):
        questions_list, category = create_questions(self.db, count=2)
        
        res = self.client().post('/quizzes', json={
            'previous_questions': [
                questions_list[0].id,
                questions_list[1].id
            ],
            'quiz_category': category.id
        })

        assert res.status_code == 200
        data = json.loads(res.data)
        assert not data.get('question')
    