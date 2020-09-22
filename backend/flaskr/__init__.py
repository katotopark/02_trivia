import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, db, Question, Category

QUESTIONS_PER_PAGE = 10


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
                raise Exception()
            return jsonify({"categories": categories_formatted, "success": True})
        except:
            db.session.rollback()
            abort(404)
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
                raise Exception()
            questions_formatted = [question.format() for question in questions]
            categories_formatted = [category.format() for category in categories]
            page = request.args.get("page", 1, type=int)
            questions_paginated = paginate(
                questions_formatted, page, QUESTIONS_PER_PAGE
            )
            total_questions = len(questions_formatted)
            return jsonify(
                {
                    "categories": categories_formatted,
                    "current_category": None,
                    "questions": questions_paginated,
                    "success": True,
                    "total_questions": total_questions,
                }
            )
        except:
            db.session.rollback()
            abort(404)
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
                raise Exception()
            question.delete()
            return jsonify({"question_id": question.id, "success": True})
        except:
            db.session.rollback()
            abort(404)
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

    """
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  """

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
                raise Exception()
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
        except:
            db.session.rollback()
            abort(404)
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

    """
      @TODO: 
      Create error handlers for all expected errors 
      including 404 and 422. 
    """

    return app
