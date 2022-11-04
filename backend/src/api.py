import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
"""
#db_drop_and_create_all()

## ROUTES



@app.route("/drinks")
def get_drinks_short():
    drinks = Drink.query.all()
    
    return jsonify(success=True, drinks=[drink.long() for drink in drinks]), 200 if drinks else 204



@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks(jwt):
    drinks = Drink.query.all()
    
    return jsonify(success=True, drinks=[drink.long() for drink in drinks]), 200 if drinks else 404


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drink(jwt):
    data = request.get_json()
    res, code, drink = None, None, None
    recipe = json.dumps(data.get('recipe'))
    if data and data.get('recipe')[0]['name']:
        drink = Drink(title=data.get("title"), recipe=recipe)
        drink.insert()
        res, code = True, 200
    else:
        abort(422)
    return jsonify({'success': res, 'drinks': [drink.long()]}), code


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(jwt, drink_id):
    data = request.get_json()
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)
    drink.title = data.get('title', drink.title)
    recipe = data.get('recipe', drink.recipe)
    drink.recipe = json.dumps(recipe)
    drink.update()

    return jsonify({'success':True, 'drinks': drink.long()}), 200 if drink else 404


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("patch:drinks")
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    drink.delete()
   
    return jsonify(success=True, delete=drink.id)

## Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422



@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": " Resource Not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False, "error": 405, "message": " Method Not Allowed"}), 405


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above 
"""


@app.errorhandler(AuthError)
def auth_error(error):
    return (
        jsonify(
            {
                "success": False,
                "error": error.status_code,
                # "message": error.error.get("description"),
                **error.error,
            }
        ),
        error.status_code,
    )