from math import ceil


def paginate(query, page, per_page):
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total_pages = ceil(total / per_page) if per_page > 0 else 0
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
