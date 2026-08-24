"""initial schema

Revision ID: abc123
Revises:
Create Date: 2026-08-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "abc123"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="buyer"),
        sa.Column("full_name", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("avatar_url", sa.String(1024)),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("icon", sa.String(255)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "shops",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "owner_id",
            sa.String(36),
            sa.ForeignKey("profiles.id"),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("logo_url", sa.String(1024)),
        sa.Column("category", sa.String(100)),
        sa.Column("address", sa.String(512)),
        sa.Column("lat", sa.Float),
        sa.Column("lng", sa.Float),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", index=True),
        sa.Column("rating_avg", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("rating_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "listings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("shop_id", sa.String(36), sa.ForeignKey("shops.id"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("price", sa.BigInteger, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="KES"),
        sa.Column(
            "category_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=True, index=True
        ),
        sa.Column("condition", sa.String(20), nullable=False, server_default="new"),
        sa.Column("stock", sa.Integer, nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", index=True),
        sa.Column("location", sa.String(255)),
        sa.Column("lat", sa.Float),
        sa.Column("lng", sa.Float),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "listing_images",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "listing_id", sa.String(36), sa.ForeignKey("listings.id"), nullable=False, index=True
        ),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "favorites",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column(
            "listing_id", sa.String(36), sa.ForeignKey("listings.id"), nullable=False, index=True
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "listing_id", name="uq_user_listing"),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "buyer_id", sa.String(36), sa.ForeignKey("profiles.id"), nullable=False, index=True
        ),
        sa.Column("shop_id", sa.String(36), sa.ForeignKey("shops.id"), nullable=False, index=True),
        sa.Column(
            "listing_id", sa.String(36), sa.ForeignKey("listings.id"), nullable=True, index=True
        ),
        sa.Column(
            "last_message_at", sa.DateTime, nullable=False, server_default=sa.func.now(), index=True
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "sender_id", sa.String(36), sa.ForeignKey("profiles.id"), nullable=False, index=True
        ),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("read_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now(), index=True
        ),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "buyer_id", sa.String(36), sa.ForeignKey("profiles.id"), nullable=False, index=True
        ),
        sa.Column("shop_id", sa.String(36), sa.ForeignKey("shops.id"), nullable=False, index=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending", index=True),
        sa.Column("total", sa.BigInteger, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="KES"),
        sa.Column("payment_method", sa.String(30), nullable=False),
        sa.Column("payment_status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("delivery_method", sa.String(20), nullable=False, server_default="pickup"),
        sa.Column("delivery_address", sa.String(512)),
        sa.Column("delivery_lat", sa.Float),
        sa.Column("delivery_lng", sa.Float),
        sa.Column(
            "rider_id", sa.String(36), sa.ForeignKey("profiles.id"), nullable=True, index=True
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "order_id", sa.String(36), sa.ForeignKey("orders.id"), nullable=False, index=True
        ),
        sa.Column(
            "listing_id", sa.String(36), sa.ForeignKey("listings.id"), nullable=False, index=True
        ),
        sa.Column("title_snapshot", sa.String(255), nullable=False),
        sa.Column("price_snapshot", sa.BigInteger, nullable=False),
        sa.Column("qty", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "order_id",
            sa.String(36),
            sa.ForeignKey("orders.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_ref", sa.String(255)),
        sa.Column("amount", sa.BigInteger, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("raw_payload", sa.JSON),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "deliveries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "order_id",
            sa.String(36),
            sa.ForeignKey("orders.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column(
            "rider_id", sa.String(36), sa.ForeignKey("profiles.id"), nullable=True, index=True
        ),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("pickup_lat", sa.Float),
        sa.Column("pickup_lng", sa.Float),
        sa.Column("dropoff_lat", sa.Float),
        sa.Column("dropoff_lng", sa.Float),
        sa.Column("tracking_updates", sa.JSON, server_default="[]"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "order_id",
            sa.String(36),
            sa.ForeignKey("orders.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("shop_id", sa.String(36), sa.ForeignKey("shops.id"), nullable=False, index=True),
        sa.Column(
            "buyer_id", sa.String(36), sa.ForeignKey("profiles.id"), nullable=False, index=True
        ),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "promotions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("shop_id", sa.String(36), sa.ForeignKey("shops.id"), nullable=True, index=True),
        sa.Column(
            "listing_id", sa.String(36), sa.ForeignKey("listings.id"), nullable=True, index=True
        ),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("starts_at", sa.DateTime, nullable=False),
        sa.Column("ends_at", sa.DateTime, nullable=False),
        sa.Column("discount_pct", sa.Integer),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "wallets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "owner_id",
            sa.String(36),
            sa.ForeignKey("profiles.id"),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column("balance", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="KES"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "wallet_transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "wallet_id", sa.String(36), sa.ForeignKey("wallets.id"), nullable=False, index=True
        ),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.BigInteger, nullable=False),
        sa.Column("ref", sa.String(255)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36), sa.ForeignKey("profiles.id"), nullable=False, index=True
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("read_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now(), index=True
        ),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("wallet_transactions")
    op.drop_table("wallets")
    op.drop_table("promotions")
    op.drop_table("reviews")
    op.drop_table("deliveries")
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("favorites")
    op.drop_table("listing_images")
    op.drop_table("listings")
    op.drop_table("shops")
    op.drop_table("categories")
    op.drop_table("profiles")
