"""empty message

Revision ID: 3f8f18ba58ab
Revises: bac467653717
Create Date: 2020-12-30 09:06:10.421844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f8f18ba58ab'
down_revision = 'bac467653717'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('board', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'board')
    # ### end Alembic commands ###