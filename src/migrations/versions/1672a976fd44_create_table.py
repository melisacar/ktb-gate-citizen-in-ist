"""create table

Revision ID: 1672a976fd44
Revises: 2d4367a39cd5
Create Date: 2025-07-07 14:38:43.598698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1672a976fd44'
down_revision: Union[str, None] = '2d4367a39cd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ist_sinir_kapilari_giris_yapan_vatandas',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tarih', sa.Date, nullable=False),
        sa.Column('sehir', sa.String, nullable=False),
        sa.Column('sinir_kapilari', sa.String, nullable=False),
        sa.Column('vatandas_sayisi', sa.Integer, nullable=False),
        sa.Column('erisim_tarihi', sa.Date, nullable=False),
        sa.UniqueConstraint('tarih', 'sehir', 'sinir_kapilari', 'vatandas_sayisi', name='unq_ist_sinir_kapilari_giris_yapan_vatandas'),
        schema='etl'
    )


def downgrade() -> None:
    op.execute("""
    DROP TABLE IF EXISTS etl.ist_sinir_kapilari_giris_yapan_vatandas
    """)