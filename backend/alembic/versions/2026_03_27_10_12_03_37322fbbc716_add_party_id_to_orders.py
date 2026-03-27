"""add_party_id_to_orders

Revision ID: 37322fbbc716
Revises: 1d909ba75c8c
Create Date: 2026-03-27 10:12:03.011243+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '37322fbbc716'
down_revision: Union[str, Sequence[str], None] = '1d909ba75c8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('orders', sa.Column('party_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_orders_party_id'), 'orders', ['party_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_orders_party_id'), table_name='orders')
    op.drop_column('orders', 'party_id')