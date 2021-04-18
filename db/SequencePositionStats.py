from mongoengine import Document, IntField


class SequencePositionStats(Document):
    A_count = IntField(required=True)
    T_count = IntField(required=True)
    G_count = IntField(required=True)
    C_count = IntField(required=True)
    position = IntField(required=True, unique=True)