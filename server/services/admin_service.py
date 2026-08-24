from server.extensions import db
from server.models import Dispute, Listing, Order, Profile, Shop, Wallet, WalletTransaction
from server.utils.errors import NotFound


def _paginate(query, page, per_page):
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return items, total, total_pages


def get_metrics():
    total_orders = db.session.query(Order).count()
    total_revenue = db.session.query(db.func.coalesce(db.func.sum(Order.total), 0)).scalar()
    total_shops = db.session.query(Shop).count()
    total_users = db.session.query(Profile).count()
    total_listings = db.session.query(Listing).count()
    return {
        "total_orders": total_orders,
        "total_revenue": int(total_revenue or 0),
        "total_shops": total_shops,
        "total_users": total_users,
        "total_listings": total_listings,
        "period": None,
    }


def approve_shop(shop_id):
    shop = db.session.query(Shop).filter_by(id=shop_id).first()
    if not shop:
        raise NotFound("Shop not found")
    shop.status = "approved"
    db.session.commit()
    return shop


def suspend_shop(shop_id):
    shop = db.session.query(Shop).filter_by(id=shop_id).first()
    if not shop:
        raise NotFound("Shop not found")
    shop.status = "suspended"
    db.session.commit()
    return shop


def list_shops(status, page, per_page):
    query = db.session.query(Shop)
    if status:
        query = query.filter_by(status=status)
    return _paginate(query.order_by(Shop.created_at.desc()), page, per_page)


def list_users(role, page, per_page):
    query = db.session.query(Profile)
    if role:
        query = query.filter_by(role=role)
    return _paginate(query.order_by(Profile.created_at.desc()), page, per_page)


def dump_user(profile):
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "phone": profile.phone,
        "avatar_url": profile.avatar_url,
        "role": profile.role,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
    }


def list_admin_listings(status, shop_id, page, per_page):
    query = db.session.query(Listing)
    if status:
        query = query.filter_by(status=status)
    if shop_id:
        query = query.filter_by(shop_id=shop_id)
    return _paginate(query.order_by(Listing.created_at.desc()), page, per_page)


def update_listing(listing_id, data):
    listing = db.session.query(Listing).filter_by(id=listing_id).first()
    if not listing:
        raise NotFound("Listing not found")
    if "status" in data:
        listing.status = data["status"]
    if "title" in data:
        listing.title = data["title"]
    db.session.commit()
    return listing


def list_payouts(status, page, per_page):
    query = (
        db.session.query(WalletTransaction, Profile)
        .join(Wallet, WalletTransaction.wallet_id == Wallet.id)
        .join(Profile, Wallet.owner_id == Profile.id)
        .filter(WalletTransaction.type == "payout")
    )
    if status:
        query = query.filter(WalletTransaction.status == status)
    rows, total, total_pages = _paginate(
        query.order_by(WalletTransaction.created_at.desc()), page, per_page
    )
    items = [
        {
            "id": txn.id,
            "wallet_id": txn.wallet_id,
            "amount": txn.amount,
            "status": txn.status,
            "ref": txn.ref,
            "created_at": txn.created_at.isoformat() if txn.created_at else None,
            "owner_name": owner.full_name,
        }
        for txn, owner in rows
    ]
    return items, total, total_pages


def update_payout(payout_id, status):
    txn = db.session.query(WalletTransaction).filter_by(id=payout_id).first()
    if not txn:
        raise NotFound("Payout not found")
    txn.status = status
    db.session.commit()
    return txn


def list_disputes(status, page, per_page):
    query = db.session.query(Dispute)
    if status:
        query = query.filter_by(status=status)
    return _paginate(query.order_by(Dispute.created_at.desc()), page, per_page)


def resolve_dispute(dispute_id, resolver_profile_id, status, resolution_note):
    dispute = db.session.query(Dispute).filter_by(id=dispute_id).first()
    if not dispute:
        raise NotFound("Dispute not found")
    dispute.status = status
    dispute.resolution_note = resolution_note
    dispute.resolved_by = resolver_profile_id
    db.session.commit()
    return dispute
