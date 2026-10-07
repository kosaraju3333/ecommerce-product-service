"""create products table

Revision ID: 7efe9c40be73
Revises: 
Create Date: 2026-10-07 11:35:19.006863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7efe9c40be73'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_products_id",
        "products",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_products_sku",
        "products",
        ["sku"],
        unique=True
    )

def downgrade() -> None:
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")