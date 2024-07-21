"""Add sold

Revision ID: d0d4b73e4fe7
Revises: 71af9aa66ed7
Create Date: 2024-07-21 14:23:43.620860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0d4b73e4fe7'
down_revision: Union[str, None] = '71af9aa66ed7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('telegram_account', sa.Column('sold', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('telegram_account', 'sold')
    # ### end Alembic commands ###
