# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

# API Documentation
## Getting Started
- The backend app is hosted at http://127.0.0.1:5000/
- Authentication: This application does not require authentication.


## Error Handling
Errors are returned as JSON objects in the following format;

```json
{
    "success": false,
    "error": "500 Internal Server Error",
    "message": "Bad request!"
}
```

The API will return three error types when a request fails:
- 400 Bad Request
- 404 Not Found
- 405 Methd Not Allowed
- 422 Unproccessable
- 500 Internal Server Error

## Endpoints

- Questions
    - [GET /questions](#get-questions)
    - [POST /questions](#post-questions)
    - [DELETE /questions/<question_id>](#delete-question)
    - [POST /questions/search](#search-questions)
- Categories
    - [GET /categories](#get-categories)
    - [GET /categories/<category_id>/questions](#get-category-questions)
- Quizzes
    - [POST /quizzes](#play-game)

# <a name="get-questions"></a>
### GET /questions
Get paginated questions and categories.

`$ curl http:127.0.0.1:5000/questions?page=1`

- Returns a list of questions and categories used as the initial game play data.
- The questions list is paginated in pages of 10 questions. Include a request argument to choose the page number starting from 1.

- Request arguments:
    - OPTIONAL int `page`. 10 questions per page, the default starts at 1 this argument isn't provided.
- Response body:
    - List of dict values each representing a question object.
        - int `id`
        - str `question`
        - str `answer`
        - int `category` identifier of a category object.
        - int `difficulty`
    - List of dict values each representing a category object.
        - int `id`
        - str `type`
    - int `total_questions` count of the total questions available.
    
- Actual response body:
```json
{
  "categories": [
    {
      "id": 2, 
      "type": "Art"
    }, 
    {
      "id": 5, 
      "type": "Entertainment"
    }, 
    {
      "id": 3, 
      "type": "Geography"
    }, 
    {
      "id": 4, 
      "type": "History"
    }, 
    {
      "id": 1, 
      "type": "Science"
    }, 
    {
      "id": 6, 
      "type": "Sports"
    }
  ], 
  "questions": [
    {
      "answer": "One", 
      "category": 2, 
      "difficulty": 4, 
      "id": 18, 
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    }, 
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 5, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }, 
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "answer", 
      "category": 4, 
      "difficulty": 3, 
      "id": 24, 
      "question": "How long is a mile in kilometers?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Lake Victoria", 
      "category": 3, 
      "difficulty": 2, 
      "id": 13, 
      "question": "What is the largest lake in Africa?"
    }
  ], 
  "total_questions": 14
}
```

# <a name="post-questions"></a>
### POST /questions
Creates a new question using the submitted question, answer, category and difficulty rating.

`$ curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question": "Your question", "answer": "Your answer", "category": "1", "difficulty": "3"}'`

- Returns a dict representing the newly created question.

- Request body:
    - dict representing new question values.
        - int `id`
        - str `question`
        - str `answer`
        - int `category` identifier of a category object.
        - int `difficulty`

- Actual request body:
```json
{
  "answer": "Answer", 
  "category": "1", 
  "difficulty": 1, 
  "id": 25, 
  "question": "Question"
}
```

- Response body:
    - dict representing the new question object.
        - int `id`
        - str `question`
        - str `answer`
        - int `category` identifier of a category object.
        - int `difficulty`

- Actual response body:
```json
{
    "answer": "Answer", 
    "category": "1", 
    "difficulty": 1, 
    "id": 25, 
    "question": "Question"
}
```


# <a name="delete-question"></a>
### DELETE /questions/<question_id>
Deletes an existing question by the qustion id.

`$ curl http://127.0.0.1:5000/questions/1 -X DELETE`

- Returns a dict representing the newly created question.

- Response body:
    - dict representing new question values.
        - int `deleted` question id.
        - bool `success`

- Actual response body:
```json
{
  "deleted": 20, 
  "success": true
}
```


# <a name="search-questions"></a>
### POST /questions/search
Search question objects whose question attribute matches the search term.

`$ curl http:127.0.0.1:5000/questions/search`

- Returns a list of questions matching the search results.

- Request arguments:
    - No request arguments needed.

- Request body:
    - search term used for matching questions.
        - str `searchTerm`

- Actual request body:
```json
{
    "searchTerm": "paintings"
}
```

- Response body:
    - List of dict values each representing a question object.
        - int `id`
        - str `question`
        - str `answer`
        - int `category` identify of a category object.
        - int `difficulty`
    - int `total_questions` count of the total questions matching the search request.
    
- Actual response body:
```json
{
  "questions": [
    {
      "answer": "One", 
      "category": 2, 
      "difficulty": 4, 
      "id": 18, 
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    }
  ], 
  "total_questions": 1
}
```

# <a name="get-categories"></a>
### GET /categories
Get all categories.

`$ curl http:127.0.0.1:5000/categories`

- Returns a list of categories used to display to the user before playing the game. 
- Request arguments:
    - No request arguments needed.
- Request body:
    - No request body needed.

- Response body:
    - List of string values each representing a category object.
    - bool `success`
    - int `total_categories` count of the total categories available.
    
- Actual response body:
```json
{
  "categories": [
    "Art", 
    "Entertainment", 
    "Geography", 
    "History", 
    "Science", 
    "Sports"
  ], 
  "success": true, 
  "total_categories": 6
}
```

# <a name="get-category-questions"></a>
### GET /categories/<category_id>/questions
Get a list of questions for a category.

`$ curl http://localhost:3000/categories/1/questions`

- Returns a list of categories used to display to the user before playing the game.

- Request arguments:
    - No request arguments needed.
- Request body:
    - No request body needed.

- Response body:
    - str `current_category` is the category that was selected.
    - List of dict values each representing a question object belonging to the category.
        - int `id`
        - str `question`
        - str `answer`
        - int `category` id of selected category.
        - int `difficulty`
    - int `total_questions` count of the total questions in the category.
    
- Actual response body:
```json
{
  "current_category": "Art", 
  "questions": [
    {
      "answer": "One", 
      "category": 2, 
      "difficulty": 4, 
      "id": 18, 
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "Jackson Pollock", 
      "category": 2, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }, 
    {
      "answer": "Escher", 
      "category": 2, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }
  ], 
  "total_questions": 4
}
```

# <a name="play-game"></a>
### POST /quizzes
Get a question to play the game.

This endpoint will return new question during the game excluding previously answered questions. For each question the frontend will pass the already seen question ids to allow the backend to exclude them in the response.

Start of the game. First question.
`$ curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions": [], "quiz_category": "2"}'`

During of the game. Second question. Exclude the first question.
`$ curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions": [21], "quiz_category": "2"}'`

- Returns dict representing a question object to show the user.

- Request arguments:
    - No request arguments needed.
- Request body:
    - array `previous_questions` are the question `id`'s of previously answered questions.
    - int `quiz_category` to only return questions in a category.

- Response body:
    - dict representing the new question object.
        - int `id`
        - str `question`
        - str `answer`
        - int `category` identify of a category object.
        - int `difficulty`
    
- Actual response body:
```json
{
  "question": {
    "answer": "Answer", 
    "category": 1, 
    "difficulty": 1, 
    "id": 25, 
    "question": "Question"
  }
}
```