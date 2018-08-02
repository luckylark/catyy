"""add qrcode

Revision ID: d7607a1c8947
Revises: 1936b36be525
Create Date: 2018-08-02 23:04:28.397353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7607a1c8947'
down_revision = '1936b36be525'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activities', sa.Column('qrcode', sa.String(length=128), nullable=True))
    op.add_column('team_join_activities', sa.Column('qrcode', sa.String(length=128), nullable=True))
    op.add_column('teams', sa.Column('qrcode', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('teams', 'qrcode')
    op.drop_column('team_join_activities', 'qrcode')
    op.drop_column('activities', 'qrcode')
    # ### end Alembic commands ###
