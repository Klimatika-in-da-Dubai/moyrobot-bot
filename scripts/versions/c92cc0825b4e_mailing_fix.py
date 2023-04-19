"""mailing fix

Revision ID: c92cc0825b4e
Revises: 03902a5b74f3
Create Date: 2023-04-18 17:45:59.215878

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c92cc0825b4e"
down_revision = "03902a5b74f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    ...


def downgrade() -> None:
    ...
