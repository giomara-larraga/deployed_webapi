from database import db


class Answer(db.Model):
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    answer_text = db.Column(db.String(200), nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return (
            f"id: {self.id}, question_id: {self.question_id}, user_id: {self.user_id}, answer_text: {self.answer_text}, "
            f"time: {self.time}"
        )


class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), nullable=False)
    question_txt = db.Column(db.String(200), nullable=False)
    question_type = db.Column(db.String(200), nullable=False)
    page = db.Column(db.Integer)
    #answer = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return (
            f"id: {self.id}, questionnaire_id: {self.questionnaire_id}, question_txt: {self.question_txt}, question_type: {self.question_type}, "
            f"page: {self.page}"
        )


class Questionnaire(db.Model):
    __tablename__ = "questionnaire"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    #user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.String(1000), nullable=False)
    group = db.Column(db.Integer, nullable=False)
    #start_time = db.Column(db.DateTime, nullable=False)
    #completion_time = db.Column(db.DateTime, nullable=False)

    #questions = db.relationship(Question)
    #questions_open = db.relationship(QuestionOpen)

    def __repr__(self):
        return (
            f"id: {self.id}, type: {self.type}, group: {self.group} "
            #f"question children: {self.questions}"
        )
