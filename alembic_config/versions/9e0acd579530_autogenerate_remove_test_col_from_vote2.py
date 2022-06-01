"""autogenerate remove test_col from vote2

Revision ID: 9e0acd579530
Revises: 95e505a88010
Create Date: 2022-06-01 18:50:00.614548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e0acd579530'
down_revision = '95e505a88010'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('votes', 'test_col')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('votes', sa.Column('test_col', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
