"""empty message

Revision ID: d1c2baf717a0
Revises: 
Create Date: 2020-12-29 03:23:36.902584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1c2baf717a0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('team_members', 'team_role_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_index('fki_team_members_team_roles_fkey', table_name='team_members')
    op.create_foreign_key(None, 'team_members', 'team_roles', ['team_role_id'], ['id'])
    op.alter_column('team_roles', 'team_role_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.drop_index('ix_team_roles_default_role', table_name='team_roles')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_team_roles_default_role', 'team_roles', ['default_role'], unique=False)
    op.alter_column('team_roles', 'team_role_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.drop_constraint(None, 'team_members', type_='foreignkey')
    op.create_index('fki_team_members_team_roles_fkey', 'team_members', ['team_role_id'], unique=False)
    op.alter_column('team_members', 'team_role_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###