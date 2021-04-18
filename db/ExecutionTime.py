from mongoengine import Document, ListField, StringField, IntField


class ExecutionTime(Document):
    name = StringField(required=True, unique=True)
    seconds = IntField(required=True)