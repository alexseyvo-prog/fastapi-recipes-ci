from marshmallow import Schema, ValidationError, fields, post_load

from models import Author, Book


class AuthorSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    middle_name = fields.Str(
        allow_none=True,
        load_default=None,
    )

    @post_load
    def create_author(self, data: dict, **kwargs) -> Author:
        return Author(**data)


class BookSchema(Schema):
    id = fields.Int(dump_only=True)

    title = fields.Str(required=True)

    author_id = fields.Int(
        required=False,
        load_only=True,
        load_default=None,
        allow_none=True,
    )

    author = fields.Nested(
        AuthorSchema,
        required=False,
        allow_none=True,
        load_default=None,
    )

    @post_load
    def create_book(self, data: dict, **kwargs) -> Book:
        author = data.pop('author', None)

        if author is not None:
            data['author_id'] = author.id

        return Book(
            **data,
            author=author,
        )