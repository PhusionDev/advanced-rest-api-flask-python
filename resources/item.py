from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, fresh_jwt_required
from models.item import ItemModel


ERRORS = {
    'BLANK_FIELD': "'{}' cannot be blank.",
    'ITEM_NOT_FOUND': "Item not found.",
    'NAME_EXISTS': "An item with name '{}' already exists.",
    'ERROR_INSERTING': "An error occurred while inserting the item."
}
MESSAGES = {
    'ITEM_DELETED': "Item Deleted."
}


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help=ERRORS['BLANK_FIELD'].format("price")
    )
    parser.add_argument(
        "store_id",
        type=int,
        required=True,
        help=ERRORS['BLANK_FIELD'].format("store_id")
    )

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": ERRORS['ITEM_NOT_FOUND']}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return (
                {"message": ERRORS['NAME_EXISTS'].format(name)},
                400,
            )

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": ERRORS['ERROR_INSERTING']}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": MESSAGES['ITEM_DELETED']}, 200
        return {"message": ERRORS['ITEM_NOT_FOUND']}, 404

    @classmethod
    def put(cls, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json(), 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": [item.json() for item in ItemModel.find_all()]}, 200
