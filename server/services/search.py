from server.extensions import db
from server.models import Listing


class SearchService:
    @staticmethod
    def search_listings(
        query=None,
        category=None,
        min_price=None,
        max_price=None,
        condition=None,
        lat=None,
        lng=None,
        radius=None,
        sort="relevance",
        page=1,
        per_page=20,
    ):
        q = db.session.query(Listing).filter_by(status="active")

        if query:
            q = q.filter(Listing.title.ilike(f"%{query}%"))

        if category:
            q = q.filter(Listing.category == category)

        if min_price is not None:
            q = q.filter(Listing.price >= min_price)

        if max_price is not None:
            q = q.filter(Listing.price <= max_price)

        if condition:
            q = q.filter(Listing.condition == condition)

        if lat is not None and lng is not None and radius is not None:
            q = q.filter(Listing.lat.isnot(None), Listing.lng.isnot(None))

        if sort == "price_asc":
            q = q.order_by(Listing.price.asc())
        elif sort == "price_desc":
            q = q.order_by(Listing.price.desc())
        elif sort == "newest":
            q = q.order_by(Listing.created_at.desc())
        elif sort == "distance" and lat is not None and lng is not None:
            q = q.order_by(Listing.lat)
        else:
            q = q.order_by(Listing.created_at.desc())

        total = q.count()
        items = q.limit(per_page).offset((page - 1) * per_page).all()

        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
        }
