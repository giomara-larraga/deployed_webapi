
from database import db

from sqlalchemy import and_, desc

from copy import deepcopy
import datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource, reqparse
from models.user_models import UserModel
from models.problem_models import SolutionArchive, Problem
import simplejson as json

# For POST and PUT
archive_parser_add = reqparse.RequestParser()
archive_parser_add.add_argument(
    "method",
    type=str,
    help="'Method' missing.",
    required=True,
)
archive_parser_add.add_argument(
    "variables",
    type=str,
    help="'variables' missing.",
    required=True,
)
archive_parser_add.add_argument(
    "objectives",
    type=str,
    help="'objectives' required.",
    required=True,
)



# For GET
archive_parser_get = reqparse.RequestParser()
archive_parser_get.add_argument(
    "method",
    type=str,
    help="'method' is required.",
    required=True,
)



class Archive(Resource):
    @jwt_required()
    def post(self):
        data = archive_parser_add.parse_args()

        current_user = get_jwt_identity()
        current_user_id = UserModel.query.filter_by(username=current_user).first().id
        method = data["method"]
        # check that variables and objectives are of same length
        variables = data["variables"]
        objectives = data["objectives"]

        # check if old solutions exists
        #archive_query = SolutionArchive.query.filter(and_(SolutionArchive.method_name==method, SolutionArchive.user_id==current_user_id) ).order_by(desc('date')).first()

        #if archive_query is None:
        # add supplied solutions to new archive

        db.session.add(
            SolutionArchive(
                user_id= current_user_id,
                method_name=method,
                variables=variables,
                objectives=objectives,
                date=datetime.datetime.now(),
            )
        )
        db.session.commit()

        msg = f"Created new archive for method {method} and added solutions."
        return {"message": msg}, 201


class GetArchive(Resource):
    @jwt_required()
    def post(self):
        data = archive_parser_get.parse_args()

        current_user = get_jwt_identity()
        current_user_id = UserModel.query.filter_by(username=current_user).first().id
        method = data["method"]

        query = SolutionArchive.query.filter_by(user_id=current_user_id, method_name=method).order_by(desc("date")).first()


        # check query to be non empty
        if query is None:
            # query empty
            msg = f"No archive found for method {method}"
            return {"message": msg}, 404

        # query not empty
        data_obj = query.objectives
        data_var = query.variables
        #date = query.date.strftime("%d/%m/%Y -- %H:%M:%S")
        #print(query.solutions_dict_pickle)
        return {
            "variables": data_var,
            "objectives": data_obj,
   
        }, 200
