"""empty message

Revision ID: 270170394707
Revises: bfa6848f4bb4
Create Date: 2022-08-10 12:02:08.581408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '270170394707'
down_revision = 'bfa6848f4bb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venues', sa.Boolean(), nullable=False))
    op.drop_column('Artist', 'looking_for_venues')
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.drop_column('Venue', 'looking_for_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Venue', 'seeking_talent')
    op.add_column('Artist', sa.Column('looking_for_venues', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Artist', 'seeking_venues')
    # ### end Alembic commands ###
