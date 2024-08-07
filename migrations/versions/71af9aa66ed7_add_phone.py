"""Add phone

Revision ID: 71af9aa66ed7
Revises: aaa9dd605d4e
Create Date: 2024-07-21 14:22:57.449013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71af9aa66ed7'
down_revision: Union[str, None] = 'aaa9dd605d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('telegram_account', sa.Column('phone', sa.String(length=50), nullable=False))
    op.create_unique_constraint(None, 'telegram_account', ['id'])
    op.create_unique_constraint(None, 'telegram_account', ['phone'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'telegram_account', type_='unique')
    op.drop_constraint(None, 'telegram_account', type_='unique')
    op.drop_column('telegram_account', 'phone')
    # ### end Alembic commands ###
