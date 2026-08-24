import math

from flask import Blueprint, jsonify, request

from server.extensions import db
from server.models import Listing
from server.schemas.listing import ListingSchema
from server.utils.errors import APIError

bp = Blueprint("search", __name__)


def _apply_full_text(query, q):
    like = f"%{q}%"
    ilike_filter = db.or_(
        Listing.title.ilike(like),
        Listing.description.ilike(like),
    )
    dialect = "postgresql"
    try:
        bind = db.session.get_bind()
        dialect = bind.dialect.name
    except Exception:
        dialect = "postgresql"
    if dialect == "postgresql":
        tsvector = db.func.to_tsvector(
            "english",
            db.func.coalesce(Listing.title, "") + " " + db.func.coalesce(Listing.description, ""),
        )
        fts = tsvector.op("@@")(db.func.plainto_tsquery("english", q))
        return query.filter(db.or_(fts, ilike_filter))
    return query.filter(ilike_filter)


def _sort_clause(sort):
    if sort == "price_asc":
        return Listing.price.asc()
    if sort == "price_desc":
        return Listing.price.desc()
    if sort == "newest":
        return Listing.created_at.desc()
    if sort == "popular":
        return Listing.created_at.desc()
    return Listing.created_at.desc()


@bp.route("/search", methods=["GET"])
def search():
    try:
        q = request.args.get("q")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        category_id = request.args.get("category_id")
        min_price = request.args.get("min_price", type=int)
        max_price = request.args.get("max_price", type=int)
        condition = request.args.get("condition")
        lat = request.args.get("lat", type=float)
        lng = request.args.get("lng", type=float)
        radius_km = request.args.get("radius_km", type=float)
        sort = request.args.get("sort", "relevance")

        query = db.session.query(Listing).filter(Listing.status == "active")
        if category_id:
            query = query.filter(Listing.category_id == category_id)
        if min_price is not None:
            query = query.filter(Listing.price >= min_price)
        if max_price is not None:
            query = query.filter(Listing.price <= max_price)
        if condition:
            query = query.filter(Listing.condition == condition)
        if lat is not None and lng is not None and radius_km is not None:
            lat_delta = radius_km / 111.0
            cos_lat = max(abs(math.cos(math.radians(lat))), 1e-6)
            lng_delta = radius_km / (111.0 * cos_lat)
            query = query.filter(
                Listing.lat.between(lat - lat_delta, lat + lat_delta),
                Listing.lng.between(lng - lng_delta, lng + lng_delta),
            )
        if q:
            query = _apply_full_text(query, q)

        total = query.count()
        items = (
            query.order_by(_sort_clause(sort)).offset((page - 1) * per_page).limit(per_page).all()
        )
        schema = ListingSchema(many=True)
        return (
            jsonify(
                {
                    "items": schema.dump(items),
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page,
                }
            ),
            200,
        )
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
