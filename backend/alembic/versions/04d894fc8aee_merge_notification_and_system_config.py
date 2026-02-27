"""merge notification and system config

Revision ID: 04d894fc8aee
Revises: 003, 008
Create Date: 2026-02-25 22:12:39.421383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04d894fc8aee'
down_revision = ('003', '008')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass