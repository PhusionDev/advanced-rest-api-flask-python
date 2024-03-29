from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from marshmallow import ValidationError
from schemas.user import UserSchema
from models.user import UserModel
from blacklist import BLACKLIST

user_schema = UserSchema()


ERRORS = {
    'BLANK_FIELD': "'{}' cannot be blank",
    'USER_ALREADY_EXISTS': "A user with that username already exists.",
    'USER_NOT_FOUND': "User not found.",
    'INVALID_CREDENTIALS': "Invalid credentials!"
}
MESSAGES = {
    'CREATED_SUCCESSFULLY': "User created successfully.",
    'USER_DELETED': "User deleted.",
    'USER_LOGGED_OUT': "User <id={user_id}> successfully logged out."
}


class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.username):
            return {"message": ERRORS['USER_ALREADY_EXISTS']}, 400

        if user.password is None or user.password == "":
            return {"message": ERRORS['BLANK_FIELD'].format("password")}

        user.save_to_db()

        return {"message": MESSAGES['CREATED_SUCCESSFULLY']}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app.
    We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful
    when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": ERRORS['USER_NOT_FOUND']}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": ERRORS['USER_NOT_FOUND']}, 404
        user.delete_from_db()
        return {"message": MESSAGES['USER_DELETED']}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_username(user_data.username)

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, user_data.password):
            # identity= is what the identity() function
            # did in security.py—now stored in the JWT
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": ERRORS['INVALID_CREDENTIALS']}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": MESSAGES['USER_LOGGED_OUT'].format(user_id=user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
