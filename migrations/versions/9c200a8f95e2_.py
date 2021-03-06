"""empty message

Revision ID: 9c200a8f95e2
Revises: 46e5f0e29cb8
Create Date: 2021-01-02 06:07:25.883668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c200a8f95e2'
down_revision = '46e5f0e29cb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('team_tasks_task_id_fkey', 'team_tasks', type_='foreignkey')
    op.drop_constraint('team_tasks_team_id_fkey', 'team_tasks', type_='foreignkey')
    op.create_foreign_key(None, 'team_tasks', 'teams', ['team_id'], ['id'], ondelete='cascade')
    op.create_foreign_key(None, 'team_tasks', 'tasks', ['task_id'], ['id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'team_tasks', type_='foreignkey')
    op.drop_constraint(None, 'team_tasks', type_='foreignkey')
    op.create_foreign_key('team_tasks_team_id_fkey', 'team_tasks', 'teams', ['team_id'], ['id'])
    op.create_foreign_key('team_tasks_task_id_fkey', 'team_tasks', 'tasks', ['task_id'], ['id'])
    # ### end Alembic commands ###
