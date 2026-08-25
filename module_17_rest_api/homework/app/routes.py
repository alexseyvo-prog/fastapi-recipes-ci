from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from models import (
    DATA,
    add_author,
    add_book,
    delete_author_by_id,
    delete_book_by_id,
    get_all_books,
    get_author_by_id,
    get_author_books,
    get_book_by_id,
    init_db,
    update_book_by_id,
)
from schemas import AuthorSchema, BookSchema


app = Flask(__name__)
api = Api(app)


@app.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({
        'error': error.name,
        'message': error.description,
    }), error.code


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception(error)

    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error),
    }), 500


class BookList(Resource):
    def get(self):
        schema = BookSchema()

        return schema.dump(
            get_all_books(),
            many=True,
        ), 200

    def post(self):
        data = request.get_json(silent=True)

        if data is None:
            return {
                'error': 'Request body must be JSON'
            }, 400

        schema = BookSchema()

        try:
            book = schema.load(data)

            if book.author is not None:
                author = add_author(book.author)
                book.author_id = author.id

            if book.author_id is None:
                return {
                    'error': 'author_id or author is required'
                }, 400

            book = add_book(book)

        except ValidationError as error:
            return error.messages, 400

        except ValueError as error:
            return {
                'error': str(error)
            }, 400

        return schema.dump(book), 201


class BookResource(Resource):
    def get(self, book_id: int):
        book = get_book_by_id(book_id)

        if book is None:
            return {
                'error': f'Book with id {book_id} not found'
            }, 404

        schema = BookSchema()

        return schema.dump(book), 200

    def put(self, book_id: int):
        data = request.get_json(silent=True)

        if data is None:
            return {
                'error': 'Request body must be JSON'
            }, 400

        schema = BookSchema()

        try:
            book = schema.load(data)
        except ValidationError as error:
            return error.messages, 400

        if book.author is not None:
            author = add_author(book.author)
            book.author_id = author.id

        if book.author_id is None:
            return {
                'error': 'author_id or author is required'
            }, 400

        book.id = book_id

        try:
            updated_book = update_book_by_id(book)
        except ValueError as error:
            return {
                'error': str(error)
            }, 400

        if updated_book is None:
            return {
                'error': f'Book with id {book_id} not found'
            }, 404

        return schema.dump(updated_book), 200

    def delete(self, book_id: int):
        deleted = delete_book_by_id(book_id)

        if not deleted:
            return {
                'error': f'Book with id {book_id} not found'
            }, 404

        return {
            'message': f'Book with id {book_id} deleted'
        }, 200


class AuthorResource(Resource):
    def post(self):
        data = request.get_json(silent=True)

        if data is None:
            return {
                'error': 'Request body must be JSON'
            }, 400

        schema = AuthorSchema()

        try:
            author = schema.load(data)
            author = add_author(author)
        except ValidationError as error:
            return error.messages, 400

        return schema.dump(author), 201

    def get(self, author_id: int):
        result = get_author_books(author_id)

        if result is None:
            return {
                'error': f'Author with id {author_id} not found'
            }, 404

        author, books = result

        return {
            'author': AuthorSchema().dump(author),
            'books': BookSchema().dump(books, many=True),
        }, 200

    def delete(self, author_id: int):
        author = get_author_by_id(author_id)

        if author is None:
            return {
                'error': f'Author with id {author_id} not found'
            }, 404

        delete_author_by_id(author_id)

        return {
            'message': (
                f'Author with id {author_id} and all books deleted'
            )
        }, 200


api.add_resource(BookList, '/api/books/')
api.add_resource(BookResource, '/api/books/<int:book_id>')

api.add_resource(
    AuthorResource,
    '/api/authors/',
    '/api/authors/<int:author_id>',
)


if __name__ == '__main__':
    init_db(initial_records=DATA)
    app.run(debug=True)