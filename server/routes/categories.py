from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Category
from server.schemas.category import CategorySchema
from server.utils.auth import admin_required
from server.utils.errors import APIError, NotFound

bp = Blueprint("categories", __name__)


@bp.route("/categories", methods=["GET"])
def list_categories():
    try:
        categories = db.session.query(Category).all()
        tree = []
        category_map = {}
        for cat in categories:
            category_map[cat.id] = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "parent_id": cat.parent_id,
                "icon": cat.icon,
                "children": [],
            }
        for cat in categories:
            if cat.parent_id and cat.parent_id in category_map:
                category_map[cat.parent_id]["children"].append(category_map[cat.id])
            else:
                tree.append(category_map[cat.id])
        return jsonify(tree), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/categories", methods=["POST"])
@jwt_required()
@admin_required
def create_category():
    try:
        data = request.get_json() or {}
        schema = CategorySchema()
        validated = schema.load(data)
        category = Category(**validated)
        db.session.add(category)
        db.session.commit()
        return jsonify(schema.dump(category)), 201
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/categories/<category_id>", methods=["PATCH"])
@jwt_required()
@admin_required
def update_category(category_id):
    try:
        data = request.get_json() or {}
        schema = CategorySchema(partial=True)
        validated = schema.load(data)
        category = db.session.query(Category).filter_by(id=category_id).first()
        if not category:
            raise NotFound("Category not found")
        for key, value in validated.items():
            setattr(category, key, value)
        db.session.commit()
        return jsonify(schema.dump(category)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/categories/<category_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_category(category_id):
    try:
        category = db.session.query(Category).filter_by(id=category_id).first()
        if not category:
            raise NotFound("Category not found")
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted"}), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500
