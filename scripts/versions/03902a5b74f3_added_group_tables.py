"""added group tables

Revision ID: 03902a5b74f3
Revises: 0ead09fabe3c
Create Date: 2023-04-18 17:28:43.058289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03902a5b74f3'
down_revision = '0ead09fabe3c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tg_group',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('group_mailing ',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('MANUAL_START_ALERT', 'MANUAL_START', 'SHIFT', 'CLEANING', 'PROMOCODE', 'BONUS', 'REFUND', name='mailingtype'), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['tg_group.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', 'type')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('group_mailing ')
    op.drop_table('tg_group')
    # ### end Alembic commands ###
