import argparse
import csv
import json
import random
import string

import dill
import numpy as np
import pandas as pd

# from desdeo_problem.problem import _ScalarObjective
from desdeo_problem.problem import DiscreteDataProblem

# from desdeo_problem.surrogatemodels.lipschitzian import LipschitzianRegressor
# from desdeo_problem.problem import Variable

from app import app, db
from models.problem_models import Problem as ProblemModel
from models.user_models import UserModel
from models.questionnaire_models import Question, Questionnaire

parser = argparse.ArgumentParser(
    description="Add N new user to the database with a pre-defined groupID and a given username prefix."
)
parser.add_argument(
    "--N", type=int, help="The number of usernames to be added.", required=True
)

dill.settings["recurse"] = True

# db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

args = vars(parser.parse_args())

def read_json(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data

def create_questionnaire(id: int, type: str, group: int):
    return {"id": id, "type": type, "group": group}


def create_question(
    question_id: int,
    questionnaire_id: int,
    question_txt: str,
    question_type: str,
    page: int,
):
    return {
        "id": question_id,
        "questionnaire_id": questionnaire_id,
        "question_txt": question_txt,
        "question_type": question_type,
        "page": page,
    }


def main():
    with app.app_context():
        letters = string.ascii_lowercase
        args = vars(parser.parse_args())
        methods = ["stratus", "nemo"]
        ids = [1, 2]
        usernames = [
            [f"{method}_{n}" for n in range(1, args["N"] + 1)] for method in methods
        ]
        usernames = sum(usernames, [])
        passwords = [
            ("".join(random.choice(letters) for i in range(6)))
            for j in range(len(usernames))
        ]
        groupIds = np.array([])
        # id1 = np.ones(N * len(ids)) * ids[1]
        for i in range(0, len(ids)):
            groupIds = np.append(groupIds, np.ones(args["N"]) * ids[i], axis=0)

        usernames.append("giomara1")
        passwords.append("123456")
        usernames.append("kaisa1")
        passwords.append("123456")
        usernames.append("aruiz1")
        passwords.append("123456")
        usernames.append("fruiz1")
        passwords.append("123456")
        usernames.append("bsaini1")
        passwords.append("123456")
        usernames.append("jsilvennoinen1")
        passwords.append("123456")
        groupIds = np.append(groupIds, [1] * 6).tolist()

        usernames.append("giomara2")
        passwords.append("123456")
        usernames.append("kaisa2")
        passwords.append("123456")
        usernames.append("aruiz2")
        passwords.append("123456")
        usernames.append("fruiz2")
        passwords.append("123456")
        usernames.append("bsaini2")
        passwords.append("123456")
        usernames.append("bsaini2")
        passwords.append("123456")
        
        groupIds = np.append(groupIds, [2] * 5).tolist()
        # print(usernames)
        # print(groupIds)

        problemGroups = np.array(range(len(usernames)), dtype=int)
        problemGroups = (
            problemGroups % 6
        )  # One of {0, 1, 2}. Decides the version of the sustainability problem.
        problemGroups = problemGroups.tolist()

        try:
            for username, password, groupId, problemGroup in zip(
                usernames, passwords, groupIds, problemGroups
            ):
                add_user(username, password, groupId, problemGroup)
            print(f"Added users {usernames} to the database succesfully.")
            for problemGroup in problemGroups:
                add_sus_problem(problemGroup)
        except Exception as e:
            print("something went wrong...")
            print(e)
            exit()

        with open("users_and_pass.csv", "w", newline="") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=" ", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            list(
                map(
                    lambda x: writer.writerow(x),
                    zip(usernames, passwords, groupIds, problemGroups),
                )
            )

        questionnaires = []
        questionnaires.append(
            create_questionnaire(1, "Demographic", 0)
        )  # 0 = both groups 1= one method 2= switch method
        questionnaires.append(create_questionnaire(2, "Init", 0))
        questionnaires.append(create_questionnaire(3, "End", 0))
        questionnaires.append(create_questionnaire(4, "End", 2))

        questions = []

        questions_file = "./tests/data/questions.json"
        data = read_json(questions_file)
        entries = json.loads(data)
        idx_question = 1
        for entry in entries:
            questions.append(create_question(idx_question, entry["questionnaire_id"], entry["question_txt"], entry["question_type"], entry["page"]))
            idx_question = idx_question + 1

        try:
            for questionnaire in questionnaires:
                add_questionaire(
                    id=questionnaire["id"],
                    type=questionnaire["type"],
                    group=questionnaire["group"],
                )
            for question in questions:
                add_question(
                    id=question["id"],
                    questionnaire_id=question["questionnaire_id"],
                    question_txt=question["question_txt"],
                    question_type=question["question_type"],
                    page=question["page"],
                )

        except Exception as e:
            print("something went wrong...")
            print(e)
            exit()

        print("Added questions to the database succesfully.")


def add_user(username, password, groupId, problemGroup):
    # print(problemGroup)
    with app.app_context():
        db.session.add(
            UserModel(
                username=username,
                password=UserModel.generate_hash(password),
                groupId=groupId,
                problemGroup=int(problemGroup),
            )
        )
        db.session.commit()


def add_sus_problem(problemGroup):
    # print(type(problemGroup))
    with app.app_context():
        user_query = UserModel.query.filter_by(problemGroup=int(problemGroup)).first()
        # print(type(user_query.problemGroup))
        if user_query is None:
            print(f"No users in group {problemGroup}.")
            return
        # else:
        #    id = user_query.id

        file_name = "./tests/data/sustainability_spanish.csv"

        data = pd.read_csv(file_name)
        # minus because all are to be maximized
        data[["social", "economic", "environmental"]] = -data[
            ["social", "economic", "environmental"]
        ]

        obj_order = {
            0: ["social", "economic", "environmental"],
            1: ["economic", "environmental", "social"],
            2: ["environmental", "social", "economic"],
            3: ["social", "environmental", "economic"],
            4: ["economic", "social", "environmental"],
            5: ["environmental", "economic", "social"],
        }

        var_names = [f"x{i}" for i in range(1, 12)]
        obj_names = obj_order[problemGroup]

        data = data[obj_names + var_names]  # Reorder objectives based on problemGroup
        ideal = data[obj_names].min().values
        nadir = data[obj_names].max().values

        # define the sus problem
        problem = DiscreteDataProblem(data, var_names, obj_names, ideal, nadir)

        db.session.add(
            ProblemModel(
                name=f"Spanish sustainability problem {problemGroup}",
                problem_type="Discrete",
                problem_pickle=problem,
                minimize=json.dumps([-1, -1, -1]),
                problemGroup=problemGroup,
            )
        )
        db.session.commit()
        print(f"Sustainability problem added for problem group '{problemGroup}'")


def add_question(id, questionnaire_id, question_txt, question_type, page):
    with app.app_context():
        db.session.add(
            Question(
                id=id,
                questionnaire_id=questionnaire_id,
                question_txt=question_txt,
                question_type=question_type,
                page=page,
            )
        )
        db.session.commit()


def add_questionaire(id, type, group):
    with app.app_context():
        db.session.add(Questionnaire(id=id, type=type, group=group))
        db.session.commit()


if __name__ == "__main__":
    main()
