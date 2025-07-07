"""create schema

Revision ID: 2d4367a39cd5
Revises: 
Create Date: 2025-07-07 14:25:15.635474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d4367a39cd5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS etl')


def downgrade() -> None:
    pass
    #op.execute('DROP SCHEMA IF EXISTS etl CASCADE')