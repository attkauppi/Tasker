"""messages_muutoksia_lisaa

Revision ID: e61c48e22a89
Revises: 9c200a8f95e2
Create Date: 2021-01-04 01:49:35.084056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e61c48e22a89'
down_revision = '9c200a8f95e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_message_read_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_message_read_time')
    # ### end Alembic commands ###
