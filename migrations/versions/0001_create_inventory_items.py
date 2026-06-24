"""create inventory_items table

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(16), nullable=False),
        sa.Column("price_per_unit", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inventory_name", "inventory_items", ["name"])
    op.create_index("ix_inventory_category", "inventory_items", ["category"])


def downgrade() -> None:
    op.drop_index("ix_inventory_category", table_name="inventory_items")
    op.drop_index("ix_inventory_name", table_name="inventory_items")
    op.drop_table("inventory_items")
