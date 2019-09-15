from flask_restful import Resource
from models.store import StoreModel


ERRORS = {
    'NAME_ALREADY_EXISTS': "A store with name '{}' already exists.",
    'ERROR_INSERTING': "An error occurred while inserting the store.",
    'STORE_NOT_FOUND': "Store not found."
}
MESSAGES = {
    'STORE_DELETED': "Store deleted."
}


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": ERRORS['STORE_NOT_FOUND']}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return (
                {"message": ERRORS['NAME_ALREADY_EXISTS'].format(name)},
                400,
            )

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": ERRORS['ERROR_INSERTING']}, 500

        return store.json(), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": MESSAGES['STORE_DELETED']}


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": [x.json() for x in StoreModel.find_all()]}
