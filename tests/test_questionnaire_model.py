import datetime
import pytest
import json

from app import app
from database import db
from flask_testing import TestCase
from models.questionnaire_models import Questionnaire, Question, Answer
from models.user_models import UserModel


@pytest.mark.questionnaire
class TestQuestionnaire(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    TESTING = True

    def create_app(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = self.SQLALCHEMY_DATABASE_URI
        app.config["TESTING"] = self.TESTING
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.app = app.test_client()

        db.session.add(
            UserModel(username="test_user", password=UserModel.generate_hash("pass"))
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, uname="test_user", pword="pass"):
        # login and get access token for test user
        payload = json.dumps({"username": uname, "password": pword})
        response = self.app.post(
            "/login", headers={"Content-Type": "application/json"}, data=payload
        )
        data = json.loads(response.data)

        access_token = data["access_token"]

        return access_token

    def test_questionnaire_demographic(self):
        access_token = self.login()

        response = self.app.get(
            "/questionnaire/demographic",
            headers={
                "Authorization": f"Bearer {access_token}",
            }
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        print(data)
        assert len(data["questions"]) == 4
       

        