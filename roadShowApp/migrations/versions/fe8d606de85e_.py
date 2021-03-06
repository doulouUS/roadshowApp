"""empty message

Revision ID: fe8d606de85e
Revises: 86036bc60a76
Create Date: 2017-10-30 15:19:14.916372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe8d606de85e'
down_revision = '86036bc60a76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'clients', ['client_id'], ['client_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'client_id')
    # ### end Alembic commands ###
