import os
import math
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, db, Question, Category

QUESTIONS_PER_PAGE = 10


class ErrorWithCode(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return repr(self.code)


def paginate(list, page, perPage):
    start = (page - 1) * perPage
    end = start + perPage
    return list[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
  @DONE: Use the after_request decorator to set Access-Control-Allow
  """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, PUT, PATCH, POST, DELETE, OPTIONS"
        )
        return response

    """
    @DONE: 
    Create an endpoint to handle GET requests 
    for all available categories.
    """

    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            categories_formatted = [category.format() for category in categories]
            if len(categories) == 0:
                raise ErrorWithCode(404)
            return jsonify({"categories": categories_formatted, "success": True})
        except ErrorWithCode as e:
            db.session.rollback()
            abort(e.code)
        finally:
            db.session.close()

    """
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        try:
            questions = Question.query.all()
            categories = Category.query.all()
            if len(questions) == 0 or len(categories) == 0:
                raise ErrorWithCode(404)
            questions_formatted = [question.format() for question in questions]
            categories_formatted = [category.format() for category in categories]
            total_questions = len(questions_formatted)
            page = request.args.get("page", 1, type=int)
            if page > math.ceil(total_questions / QUESTIONS_PER_PAGE):
                raise ErrorWithCode(404)
            questions_paginated = paginate(
                questions_formatted, page, QUESTIONS_PER_PAGE
            )
            return jsonify(
                {
                    "categories": categories_formatted,
                    "current_category": None,
                    "questions": questions_paginated,
                    "success": True,
                    "total_questions": total_questions,
                }
            )
        except ErrorWithCode as e:
            db.session.rollback()
            abort(e.code)
        finally:
            db.session.close()

    """
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id=question_id).one_or_none()
            if question is None:
                raise ErrorWithCode(404)
            question.delete()
            return jsonify({"question_id": question.id, "success": True})
        except ErrorWithCode as e:
            db.session.rollback()
            abort(e.code)
        finally:
            db.session.close()

    """
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  """

    @app.route("/questions", methods=["POST"])
    def insert_question():
        data = request.get_json()
        try:
            if not data:
                raise ErrorWithCode(400)
            else:
                new_question = Question(
                    question=data.get("question"),
                    answer=data.get("answer"),
                    category=data.get("category"),
                    difficulty=data.get("difficulty"),
                )
            new_question.insert()
            questions = Question.query.all()
            return jsonify(
                {
                    "question": new_question.format(),
                    "success": True,
                    "total_questions": len(questions),
                }
            )
        except ErrorWithCode as e:
            print(e)
            db.session.rollback()
            abort(e.code)
        finally:
            db.session.close()

    """
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  """

    @app.route("/questions/search", methods=["POST"])
    def search_question():
        data = request.get_json()
        search_term = data.get("search_term")
        if search_term is None:
            raise ErrorWithCode(400)
        try:
            questions = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).all()
            questions_formatted = [question.format() for question in questions]
            return jsonify(
                {
                    "current_category": None,
                    "questions": questions_formatted,
                    "success": True,
                    "total_questions": len(questions),
                }
            )
        except ErrorWithCode as e:
            db.session.rollback()
            abort(e.code)
        finally:
            db.session.close()

    """
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_of_category(category_id):
        try:
            category = Category.query.filter_by(id=category_id).one_or_none()
            questions = Question.query.filter_by(category=category_id).all()
            if category is None or len(questions) == 0:
                raise ErrorWithCode(404)
            category_formatted = category.format()
            questions_formatted = [question.format() for question in questions]
            page = request.args.get("page", 1, type=int)
            questions_paginated = paginate(
                questions_formatted, page, QUESTIONS_PER_PAGE
            )
            total_questions = len(questions_formatted)
            return jsonify(
                {
                    "current_category": category_formatted,
                    "questions": questions_paginated,
                    "success": True,
                    "total_questions": total_questions,
                }
            )
        except ErrorWithCode as e:
            db.session.rollback()
            abort(e.code)
        finally:
            db.session.close()

    """
      @TODO:
      Create a POST endpoint to get questions to play the quiz.
      This endpoint should take category and previous question parameters
      and return a random questions within the given category,
      if provided, and that is not one of the previous questions.

      TEST: In the "Play" tab, after a user selects "All" or a category,
      one question at a time is displayed, the user is allowed to answer
      and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def get_questions_by_category():
        data = request.get_json()
        try:
            if not data:
                raise ErrorWithCode(400)
            else:
                previous_questions = data.get("previous_questions", [])
                quiz_category = data.get("category", {})
            questions = []

            if "id" not in quiz_category:
                raise ErrorWithCode(422)
            if quiz_category["id"] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)
                ).all()
            else:
                questions = (
                    Question.query.filter(Question.category == quiz_category["id"])
                    .filter(Question.id.notin_(previous_questions))
                    .all()
                )
            if len(questions) > 0:
                new_question = questions[random.randrange(0, len(questions))].format()
                return jsonify({"question": new_question, "success": True})
            else:
                return jsonify({"question": None, "success": True})
        except ErrorWithCode as e:
            db.session.rollback()
            abort(e.code)
        finally:
            db.session.close()

    """
      @TODO: 
      Create error handlers for all expected errors 
      including 404 and 422. 
    """

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "error": error.code,
                    "message": "bad request",
                    "success": False,
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "error": error.code,
                    "message": "resource not found",
                    "success": False,
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify(
                {
                    "error": error.code,
                    "message": "method not allowed",
                    "success": False,
                }
            ),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"error": error.code, "message": "unprocessable", "success": False}
            ),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "error": error.code,
                    "message": "internal server error",
                    "success": False,
                }
            ),
            500,
        )

    return app
