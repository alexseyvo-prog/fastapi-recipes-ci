"""merge surname and patronymic branches

Revision ID: 2f899932d99e
Revises: d00fb3d44ad2, e0e1e5165c2a
Create Date: 2026-09-29 18:59:26.804350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f899932d99e'
down_revision: Union[str, None] = ('d00fb3d44ad2', 'e0e1e5165c2a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
