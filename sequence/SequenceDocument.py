from mongoengine import Document, ListField, StringField, IntField


class SequenceDocument(Document):
    version = StringField(required=True, max_length=100)
    length = IntField(required=True)
    fasta = StringField(required=True)
    sequence = StringField(required=True)
    name = StringField(required=False)
    region = StringField(required=False)
    location = ListField(required=False)
    base_sequence = StringField(required=False)  # change to Reference
    wild_type_sequence = StringField(required=False)  # change to Reference
    distance_to_rCRS = IntField(required=False)
    distance_to_RSRS = IntField(required=False)
