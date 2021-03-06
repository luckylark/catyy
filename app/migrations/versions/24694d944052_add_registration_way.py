"""add registration way

Revision ID: 24694d944052
Revises: a51278937a0c
Create Date: 2018-07-28 08:30:27.278175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24694d944052'
down_revision = 'a51278937a0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activities', sa.Column('registration', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activities', 'registration')
    # ### end Alembic commands ###
