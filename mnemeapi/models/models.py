from tortoise.fields import UUIDField, TextField, IntField, BooleanField, ReverseRelation, ForeignKeyRelation, \
    ForeignKeyField, CASCADE, DatetimeField, CharField, DateField
from tortoise.models import Model


class User(Model):
    id = UUIDField(pk=True, index=True)

    # 0 == Free, 10 == Premium
    tier = IntField(default=0)

    username = CharField(max_length=255, unique=True, index=True)
    hashed_password = TextField(null=False)

    encrypted = BooleanField(default=False)
    admin = BooleanField(default=False)

    journals: ReverseRelation["Journal"]


class Journal(Model):
    id = IntField(pk=True, index=True)

    user: ForeignKeyRelation[User] = ForeignKeyField("models.User", related_name="journals", on_delete=CASCADE)

    name = TextField(null=False)
    name_lower = TextField(null=False)

    # YYYY-MM-DD or None
    deleted_on = DateField(null=True)

    entries: ReverseRelation["Entry"]


class Entry(Model):
    id = IntField(pk=True, index=True)

    journal: ForeignKeyRelation[Journal] = ForeignKeyField("models.Journal", related_name="entries", on_delete=CASCADE)

    short = TextField(null=False)
    long = TextField(null=False)

    # YYYY-MM-DD HH:MM format in UTC timezone
    date = DatetimeField(null=False)
    # YYYY-MM-DD or None
    deleted_on = DateField(null=True)

    keywords: ReverseRelation["Keyword"]


class Keyword(Model):
    id = IntField(pk=True)
    entry: ForeignKeyRelation[Entry] = ForeignKeyField("models.Entry", related_name="keywords", on_delete=CASCADE)
    word = TextField(null=False)
