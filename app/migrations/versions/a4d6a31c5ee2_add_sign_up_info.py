"""add sign up info

Revision ID: a4d6a31c5ee2
Revises: 2df61690d5b6
Create Date: 2018-07-29 09:05:42.430589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4d6a31c5ee2'
down_revision = '2df61690d5b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activity_contacts', sa.Column('age', sa.SmallInteger(), nullable=True))
    op.add_column('activity_contacts', sa.Column('gender', sa.SmallInteger(), nullable=True))
    op.add_column('activity_contacts', sa.Column('phone', sa.String(length=15), nullable=True))
    op.add_column('activity_contacts', sa.Column('province', sa.SmallInteger(), nullable=True))
    op.add_column('join_activities', sa.Column('comment', sa.String(length=100), nullable=True))
    op.add_column('join_activities', sa.Column('registration', sa.SmallInteger(), nullable=True))
    op.add_column('join_activities', sa.Column('solution', sa.SmallInteger(), nullable=True))
    op.add_column('join_activities', sa.Column('team_id', sa.Integer(), nullable=True))
    op.add_column('join_activities', sa.Column('volunteer', sa.SmallInteger(), nullable=True))
    op.create_foreign_key(None, 'join_activities', 'teams', ['team_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'join_activities', type_='foreignkey')
    op.drop_column('join_activities', 'volunteer')
    op.drop_column('join_activities', 'team_id')
    op.drop_column('join_activities', 'solution')
    op.drop_column('join_activities', 'registration')
    op.drop_column('join_activities', 'comment')
    op.drop_column('activity_contacts', 'province')
    op.drop_column('activity_contacts', 'phone')
    op.drop_column('activity_contacts', 'gender')
    op.drop_column('activity_contacts', 'age')
    # ### end Alembic commands ###
