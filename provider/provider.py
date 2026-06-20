# This is our simple provider application (API) -- it is flask app with a single GET /orders endpoint

from flask import Flask, jsonify

from .data.orders import ORDERS


DATA_STORE = ORDERS


def create_app() -> Flask:
    app = Flask(__name__)

    @app.after_request
    def set_json_content_type(response):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

    @app.get("/orders")
    def get_orders():
        return jsonify(DATA_STORE)

    return app
