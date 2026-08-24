"""shop cover photos and disputes

Revision ID: abc124
Revises: abc123
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "abc124"
down_revision: str | None = "abc123"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("shops", sa.Column("cover_url", sa.String(1024), nullable=True))

    op.create_table(
        "disputes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id"), nullable=False, index=True),
        sa.Column(
            "raised_by", sa.String(36), sa.ForeignKey("profiles.id"), nullable=False, index=True
        ),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open", index=True),
        sa.Column("resolution_note", sa.Text),
        sa.Column("resolved_by", sa.String(36), sa.ForeignKey("profiles.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("disputes")
    op.drop_column("shops", "cover_url")
