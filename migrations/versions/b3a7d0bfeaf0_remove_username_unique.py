"""remove username unique

Revision ID: b3a7d0bfeaf0
Revises: 
Create Date: 2026-03-06 11:41:14.994755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3a7d0bfeaf0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', recreate='always') as batch_op:
        pass


def downgrade():
    pass
