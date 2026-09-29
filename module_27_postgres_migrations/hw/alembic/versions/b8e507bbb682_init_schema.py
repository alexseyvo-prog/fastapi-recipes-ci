"""init schema

Revision ID: b8e507bbb682
Revises: 
Create Date: 2026-09-29 18:41:01.251026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8e507bbb682'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "coffee",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=200), nullable=True),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column("reviews", sa.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("has_sale", sa.Boolean(), nullable=True),
        sa.Column("address", sa.JSON(), nullable=True),
        sa.Column("coffee_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["coffee_id"], ["coffee.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("coffee")
