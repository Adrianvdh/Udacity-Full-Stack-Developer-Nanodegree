import json

from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink  # noqa
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO DONE uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all() # noqa

# ROUTES
'''
@TODO DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


'''
@TODO DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


def validate_drink_request(title, recipe):
    """
    Validate a POST/PATCH body request for a drink.
    `title` and `recipe` cannot be blank.
    - `title` should be a valid string object
    - `recipe` is a JSON object that should conform to this scheme:
        recipe = [{'color': string, 'name':string, 'parts':number}]
    """
    errors = []
    if not title:
        errors.append({'title': 'Title field cannot be blank!'})
    if not recipe:
        errors.append({'recipe': 'Recipe field cannot be blank!'})

    for index, r in enumerate(recipe):
        color = r.get('color', None)
        if not color:
            errors.append({'missing_field': f'The recipe list object at index {index} is missing the color property!'})
        if color and not type(color) is str:
            errors.append({'incorrect_type': f'The recipe list object index {index} color property must be a string!'})

        name = r.get('name', None)
        if not name:
            errors.append({'missing_field': f'The recipe list object at index {index} is missing the name property!'})
        if not type(name) is str:
            errors.append({'incorrect_type': f'The recipe list object index {index} name property must be a string!'})

        parts = r.get('parts', None)
        if not parts:
            errors.append({'missing_field': f'The recipe list object at index {index} is missing the parts property!'})
        if not type(parts) is int:
            errors.append({'incorrect_type': f'The recipe list object index {index} parts property must be a number!'})

    return errors


'''
@TODO DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(jwt):
    body = request.get_json()
    if not body:
        abort(400)

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    errors = validate_drink_request(title, recipe)

    if len(errors) > 0:
        abort(400, errors)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 201
    except Exception as e:
        abort(500, e)


'''
@TODO DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404, 'Drink is not found!')

    body = request.get_json()
    if not body:
        abort(400)

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    errors = validate_drink_request(title, recipe)

    if len(errors) > 0:
        abort(400, errors)

    try:
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        abort(422, e)


'''
@TODO DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404, 'Drink is not found!')

    try:
        drink.delete()
    except Exception:
        abort(422, 'Could not delete drink!')

    return jsonify({
        'success': True,
        'delete': drink_id
    }), 200


# Error Handling
'''
@TODO DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': '400 Bad Request',
        'message': error.description
    }), 400


'''
@TODO DONE implement error handler for 404
    error handler should conform to general task above
'''


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


'''
@TODO DONE implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_bad_request(exception):
    return jsonify(exception.error), exception.status_code
