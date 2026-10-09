from tortoise.fields import IntField, CharField,DatetimeField,TextField,ForeignKeyField
from tortoise.models import Model


class Project(Model):
    id = IntField(pk=True)
    name = CharField(max_length=100)

class CodeFile(Model):
    id = IntField(pk=True)
    project = ForeignKeyField(
        "models.Project",
        on_delete="CASCADE",
        related_name="files"
    )
    path = CharField(max_length=1000)
    language = CharField(max_length=10)
    content = TextField(null=True)
    created_at = DatetimeField(auto_now_add=True)

class CodeChunk(Model):
    id = IntField(pk=True)
    file = ForeignKeyField(
        "models.CodeFile",
        on_delete="CASCADE",
        related_name="chunks"
    )
    content = TextField()
    start_line = IntField()
    end_line = IntField()
    chunk_index = IntField()
    # embedding =

