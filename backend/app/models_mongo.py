from mongoengine import Document, StringField, BooleanField, ReferenceField, ListField

class User(Document):
    username = StringField(max_length=255, unique=True, required=True)
    hashed_password = StringField(max_length=255, required=True)
    is_active = BooleanField(default=True)
    conversations = ListField(ReferenceField('Conversation'))

class Conversation(Document):
    message = StringField()
    translation = StringField()
    created_at = StringField()
    role = StringField()
    user = ReferenceField(User)
    character = ReferenceField('Character')

class Character(Document):
    name = StringField(max_length=255, unique=True, required=True)
    avatar_uri = StringField()
    gpt_model_path = StringField()
    sovits_model_path = StringField()
    refer_path = StringField()
    refer_text = StringField()
    conversations = ListField(ReferenceField(Conversation))

    meta = {
        'collection': 'characters',
        'indexes': [
            {'fields': ['name'], 'unique': True}
        ]
    }