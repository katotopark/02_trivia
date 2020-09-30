import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_404_get_categories_with_invalid_argument(self):
        res = self.client().get("/categories/0", json={"categories": {}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertFalse(data["current_category"])

    def test_404_get_questions_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", json={"questions": []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        question = Question(question="foo", answer="bar", category="2", difficulty=3)
        question.insert()
        question_id = question.id

        res = self.client().delete(f"/questions/{question_id}")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question_id"], question_id)

    def test_404_question_to_delete_not_found(self):
        res = self.client().delete("questions/450")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_insert_question(self):
        previous_questions = Question.query.all()
        question = {
            "question": "foo",
            "answer": "bar",
            "category": "2",
            "difficulty": 3,
        }

        res = self.client().post("/questions", json=question)
        data = json.loads(res.data)
        current_questions = Question.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(current_questions), len(previous_questions) + 1)

    def test_400_insert_question_with_no_payload(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)

        self.assertTrue(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_search_questions(self):
        search_term = {"search_term": "hi"}
        res = self.client().post("questions/search", json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
        self.assertGreaterEqual(data["total_questions"], 0)

    def test_405_search_with_invalid_method(self):
        search_term = {"search_term": "hi"}
        res = self.client().get("/questions/search", json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_get_questions_of_category(self):
        res = self.client().get("categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), data["total_questions"])

    def test_404_get_questions_of_invalid_category(self):
        res = self.client().get("/categories/0/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_quizzes(self):
        quiz_data = {"category": {"id": 6}, "previous_questions": []}
        res = self.client().post("/quizzes", json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_get_quizzes_unprocessable_payload(self):
        quiz_data = {"category": {"type": "Art"}}
        res = self.client().post("/quizzes", json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()