"""fix naming

Revision ID: 40c308a20f34
Revises: c6431b42deee
Create Date: 2023-08-12 02:29:11.414716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40c308a20f34'
down_revision: Union[str, None] = 'c6431b42deee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('is_completed', sa.Boolean(), nullable=True))
    op.drop_column('tasks', 'is_complited')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('is_complited', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('tasks', 'is_completed')
    # ### end Alembic commands ###
