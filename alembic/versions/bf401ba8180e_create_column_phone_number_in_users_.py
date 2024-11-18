"""create column phone_number in users table

Revision ID: bf401ba8180e
Revises: 
Create Date: 2024-11-18 14:41:24.012879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf401ba8180e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String, nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
