"""Initial migration

Revision ID: 1d909ba75c8c
Revises: 
Create Date: 2026-02-27 16:35:53.496247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1d909ba75c8c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade()-> None:
    """Upgrade schema
    """

def downgrade() -> None:
    """Downgrade Schema
    """