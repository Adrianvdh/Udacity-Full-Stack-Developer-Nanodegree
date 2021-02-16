import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from .models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginated_objects(request, objects_list):
    page = request.args.get('page', default=1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return objects_list[start:end]


def create_app(config='flaskr.config'):
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config)
    db = setup_db(app)

    '''
    @TODO DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    '''
    @TODO DONE: Use the after_request decorator to set Access-Control-Allow
    '''
      # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO DONE: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.type).all()

        return jsonify({
            'categories': [
                cat.type for cat in categories
            ],
            'total_categories': len(categories),
            'success': True
        }), 200

    '''
    @TODO DONE: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.difficulty.desc()).all()
        categories = Category.query.order_by(Category.type).all()
        
        questions_paginated = paginated_objects(request, questions)

        return jsonify({
            'questions': [
                question.format() for question in questions_paginated
            ],
            'total_questions': len(questions),
            'categories': [
                { 'id': cat.id, 'type': cat.type } for cat in categories
            ]
        }), 200

    '''
    @TODO DONE: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404, 'Question not found!')
        
        question.delete()
        
        return jsonify({
            'success': True,
            'deleted': question.id
        }), 200


    '''
    @TODO DONE: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)
        
        errors = []
        if not question:
            errors.append({'question': 'Question field cannot be blank!'})
        if not answer:
            errors.append({'answer': 'Answer field cannot be blank!'})
        if not category:
            errors.append({'category': 'Category field cannot be blank!'})
        if not difficulty:
            errors.append({'difficulty': 'Difficulty field cannot be blank!'})
        
        if len(errors) > 0:
            abort(400, errors)
        
        try:
            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            question.insert()

            return jsonify({
                'id': question.id,
                'question': question.question,
                'answer': question.answer,
                'category': str(question.category),
                'difficulty': question.difficulty
            }), 201
        except:
            abort(500)

    '''
    @TODO DONE: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        if not 'searchTerm' in body:
            abort(400)
        
        search_term = body.get('searchTerm')
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        return jsonify({
            'questions': [
                question.format() for question in questions
            ],
            'total_questions': len(questions)
        }), 200

    '''
    @TODO DONE: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()
        
        if category is None:
            abort(404, 'Category not found!')
        
        questions = Question.query.filter(Question.category == str(category_id)) \
            .order_by(Question.difficulty.desc()).all()
        
        questions_paginated = paginated_objects(request, questions)

        return jsonify({
            'questions': [
                question.format() for question in questions_paginated
            ],
            'total_questions': len(questions),
            'current_category': category.type
        }), 200

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        previous_questions_ids = body.get('previous_questions', None)
        quiz_category_id = str(body.get('quiz_category', None))

        question = Question.query \
            .filter(Question.id.notin_(previous_questions_ids)) \
            .filter(Question.category == str(quiz_category_id)) \
            .first()
        
        if not question:
            return jsonify({}), 200
        
        return jsonify({
            'question': question.format()
        }), 200


    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': '400 Bad Request',
            'message': error.description
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '404 Not Found',
            'message': str(error.description)
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': '405 Method Not Allowed',
            'message': str(error.description)
        }), 405

    @app.errorhandler(422)
    def unproccessable(error):
        return jsonify({
            'success': False,
            'error': '422 Unproccessable',
            'message': str(error.description)
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': '500 Internal Server Error',
            'message': str(error.description)
        }), 500
    
    return app, db
