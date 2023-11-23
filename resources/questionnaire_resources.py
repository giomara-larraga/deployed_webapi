from database import db
import datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource, reqparse
from models.questionnaire_models import Question, Answer, Questionnaire
from models.user_models import UserModel
import simplejson as json
from sqlalchemy import and_

answer_entry_parser = reqparse.RequestParser()
answer_entry_parser.add_argument("key", type=int, action="append")
answer_entry_parser.add_argument(
    "value",
    action="append",
)


class QuestionnaireDemographic(Resource):
    def get(self):
        # TODO: remove try catch block and check the problems query
        try:
            question_list = Question.query.filter(Question.question_type != 'objective', Question.questionnaire_id == 1).all()
            group_question_list = Question.query.filter_by(
                questionnaire_id=1, question_type="objective"
            ).all()
            #question_list = Question.query.filter_by(questionnaire_id=1).all()

            text_elements = [
                {
                    "name": str(question.id),
                    "title": question.question_txt,
                    "type": question.question_type,
                    "isRequired": True,
                }
                for question in question_list
            ]
            # print(text_elements)

            group_elements = [
                {
                    "type": "multipletext",
                    "name": "groupelements",
                    "title": "What objective function values do you think you can achieve as your final solution?",
                    "isRequired": True,
                    "items": [
                        {
                            "name": str(question.id),
                            "title": question.question_txt,
                            # "type": question.question_type,
                            "isRequired": True,
                        }
                        for question in group_question_list
                    ],
                }
            ]
            text_elements.append(group_elements[0])
            response = {
                "elements": text_elements,
                "showQuestionNumbers": True,
            }

            response["elements"]
            for element in response["elements"]:
                if element["title"] == "Age":
                    element["inputType"] = "number"
                    element["min"] = 0
                    element["max"] = 100
                    element["defaultValue"] = 0
                if element["title"] == "Gender":
                    element["showNoneItem"] = False
                    element["showOtherItem"] = False
                    element["choices"] = [
                        "Male",
                        "Female",
                        "Non-binary",
                        "Prefer not to disclose",
                    ]
                if element["type"] == "Boolean":
                    element["valueTrue"] = "Yes"
                    element["valueFalse"] = "No"
                    element["renderAs"] = "radio"
                if element["type"] == "rating":
                    element["minRateDescription"] = "Not tired"
                    element["maxRateDescription"] = "Very tired"
            return response, 200
        except Exception as e:
            print(f"DEBUG: {e}")
            return {"message": "Could not fetch questions!"}, 404


""" class QuestionnaireInit(Resource):
    def get(self):
        # TODO: remove try catch block and check the problems query
        try:
            question_list = Question.query.filter_by(
                questionnaire_id=2, question_type="rating"
            ).all()

            group_question_list = Question.query.filter_by(
                questionnaire_id=2, question_type="text"
            ).all()

            text_elements = [
                {
                    "name": str(question.id),
                    "title": question.question_txt,
                    "type": question.question_type,
                    "isRequired": True,
                }
                for question in question_list
            ]
            # print(text_elements)

            group_elements = [
                {
                    "type": "multipletext",
                    "name": "groupelements",
                    "title": "What objective function values do you think you can achieve as your final solution?",
                    "isRequired": True,
                    "items": [
                        {
                            "name": str(question.id),
                            "title": question.question_txt,
                            # "type": question.question_type,
                            "isRequired": True,
                        }
                        for question in group_question_list
                    ],
                }
            ]
            text_elements.append(group_elements[0])
            
            # print(text_elements)
            response = {
                "elements": text_elements,
                "showQuestionNumbers": True,
            }

            response["elements"]
            for element in response["elements"]:
                if element["type"] == "rating":
                    element["minRateDescription"] = "Not tired"
                    element["maxRateDescription"] = "Very tired"
            print(response)
            return response, 200
        except Exception as e:
            print(f"DEBUG: {e}")
            return {"message": "Could not fetch questions!"}, 404 """


class QuestionnairePhase1(Resource):
    def _get_rows(self, id_page):
        question_list = Question.query.filter(
            Question.questionnaire_id == 2,
            Question.page == id_page,
            Question.question_type == "matrix",
        ).all()
        response = {
            "rows": [
                {
                    "value": str(question.id),
                    "text": question.question_txt,
                }
                for question in question_list
            ],
        }
        return response

    def _get_open(self, id_page):
        open_questions= []
        count = Question.query.filter(
            Question.questionnaire_id == 2,
            Question.page == id_page,
            Question.question_type == "text",
        ).count()
        question = Question.query.filter(
                Question.questionnaire_id == 2,
                Question.page == id_page,
                Question.question_type == "text",
            ).all()
        if count >= 1:
            for item in question:
                question_r = {
                    "name": str(item.id),
                    "type": "text",
                    "title": item.question_txt,
                    "isRequired": True,
                }
                open_questions.append(question_r)
            print(open_questions)
        return open_questions

    def _compose_element(self, id_page):
        rows = self._get_rows(id_page)["rows"]
        text_questions = self._get_open(id_page)
        element = [
            {
                "type": "matrix",
                "name": "page" + str(id_page),
                "title": "Please indicate if you agree or disagree with the following statements",
                "columns": [
                    {"value": 5, "text": "Strongly agree"},
                    {"value": 4, "text": "Agree"},
                    {"value": 3, "text": "Neither agree nor disagree"},
                    {"value": 2, "text": "Disagree"},
                    {"value": 1, "text": "Strongly disagree"},
                ],
                "rows": rows,
                "alternateRows": True,
                "isAllRowRequired": True,
            }
        ]
        if text_questions != None:
            for item in text_questions:
                element.append(item)

        return element

    def get(self):
        # TODO: remove try catch block and check the problems query
        try:
            num_pages = 4
            response = {
                "pages": [
                    {
                        "elements": self._compose_element(j + 1),
                    }
                    for j in range(0, num_pages)
                ]
            }
            return response, 200
        except Exception as e:
            print(f"DEBUG: {e}")
            return {"message": "Could not fetch questions!"}, 404


class QuestionnairePhase2(Resource):
    def _get_rows(self, id_page):
        question_list = Question.query.filter(
            Question.questionnaire_id == 3,
            Question.page == id_page,
            Question.question_type == "matrix",
        ).all()
        response = {
            "rows": [
                {
                    "value": str(question.id),
                    "text": question.question_txt,
                }
                for question in question_list
            ],
        }
        return response

    def _get_open(self, id_page):
        open_questions= []
        count = Question.query.filter(
            Question.questionnaire_id == 3,
            Question.page == id_page,
            Question.question_type == "text",
        ).count()
        questions = Question.query.filter(
                Question.questionnaire_id == 3,
                Question.page == id_page,
                Question.question_type == "text",
            ).all()
        if count >= 1:
            for question in questions:
                question_r = {
                    "name": str(question.id),
                    "type": "text",
                    "title": question.question_txt,
                    "isRequired": True,
                }
                open_questions.append(question_r)
            print(open_questions)
        return open_questions

    def _compose_element(self, id_page):
        rows = self._get_rows(id_page)["rows"]
        text_questions = self._get_open(id_page)
        if len(rows) > 0 :
            element = [
                {
                    "type": "matrix",
                    "name": "page" + str(id_page),
                    "title": "Please indicate if you agree or disagree with the following statements",
                    "columns": [
                        {"value": 5, "text": "Strongly agree"},
                        {"value": 4, "text": "Agree"},
                        {"value": 3, "text": "Neither agree nor disagree"},
                        {"value": 2, "text": "Disagree"},
                        {"value": 1, "text": "Strongly disagree"},
                    ],
                    "rows": rows,
                    "alternateRows": True,
                    "isAllRowRequired": True,
                }
            ]
            if text_questions != None:
                for item in text_questions:
                    element.append(item)
        else:
            question_list = Question.query.filter( Question.questionnaire_id == 3, Question.page == id_page).all()
            element = [
                {
                    "name": str(question.id),
                    "title": question.question_txt,
                    "type": question.question_type,
                    "isRequired": True,
                }
                for question in question_list
            ]

            for item in element:
                if item["type"] == "rating":
                    item["minRateDescription"] = "Not tired"
                    item["maxRateDescription"] = "Very tired"


        return element

    def get(self):
        # TODO: remove try catch block and check the problems query
        try:
            num_pages = 4
            response = {
                "pages": [
                    {
                        "elements": self._compose_element(j + 1),
                    }
                    for j in range(0, num_pages)
                ]
            }
            return response, 200
        except Exception as e:
            print(f"DEBUG: {e}")
            return {"message": "Could not fetch questions!"}, 404


class QuestionnaireFinal(Resource):
    def _get_rows(self, id_page):
        question_list = Question.query.filter(
            Question.questionnaire_id == 4,
            Question.page == id_page,
            Question.question_type == "matrix",
        ).all()
        response = {
            "rows": [
                {
                    "value": str(question.id),
                    "text": question.question_txt,
                }
                for question in question_list
            ],
        }
        return response

    def _get_open(self, id_page):
        open_questions= []
        count = Question.query.filter(
            Question.questionnaire_id == 4,
            Question.page == id_page,
            Question.question_type == "text",
        ).count()
        questions = Question.query.filter(
                Question.questionnaire_id == 4,
                Question.page == id_page,
                Question.question_type == "text",
        ).all()
        if count >= 1:
            for question in questions:
                question_r = {
                    "name": str(question.id),
                    "type": "text",
                    "title": question.question_txt,
                    "isRequired": True,
                }
                open_questions.append(question_r)
            print(open_questions)
        return open_questions

    def _compose_element(self, id_page):
        rows = self._get_rows(id_page)["rows"]
        text_questions = self._get_open(id_page)
        element = [
            {
                "type": "matrix",
                "name": "page" + str(id_page),
                "title": "Please indicate if you agree or disagree with the following statements",
                "columns": [
                    {"value": 5, "text": "Strongly agree"},
                    {"value": 4, "text": "Agree"},
                    {"value": 3, "text": "Neither agree nor disagree"},
                    {"value": 2, "text": "Disagree"},
                    {"value": 1, "text": "Strongly disagree"},
                ],
                "rows": rows,
                "alternateRows": True,
                "isAllRowRequired": True,
            }
        ]
        if text_questions != None:
            for item in text_questions:
                element.append(item)

        return element

    def get(self):
        # TODO: remove try catch block and check the problems query
        try:
            num_pages = 1
            response = {
                "pages": [
                    {
                        "elements": self._compose_element(j + 1),
                    }
                    for j in range(0, num_pages)
                ]
            }
            return response, 200
        except Exception as e:
            print(f"DEBUG: {e}")
            return {"message": "Could not fetch questions!"}, 404

class AnswerQuestionnaire(Resource):
    @jwt_required()
    def post(self):
        try:
            answers = answer_entry_parser.parse_args()
            current_user = get_jwt_identity()
            current_user_id = (
                UserModel.query.filter_by(username=current_user).first().id
            )

            for key, value in zip(answers.key, answers.value):
                # create a new log entry
                answer_id = int(key)
                answer_text = str(value)
                answer_entry = Answer(
                    question_id=answer_id,
                    user_id=current_user_id,
                    answer_text=answer_text,
                    time=datetime.datetime.now(),
                )
                db.session.add(answer_entry)
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Got an exception while creating saving answer: {e}")
            print(answers)
            return {"message": "Could not add answer."}, 500

        return {"message": "Answer added successfully."}, 201
