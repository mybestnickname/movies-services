"""partition constraints

Revision ID: c66f52579b20
Revises: 117fc2fb9a1c
Create Date: 2022-06-29 17:20:57.775796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c66f52579b20'
down_revision = '117fc2fb9a1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uix_auth_timestamp', 'auth_history', ['id', 'timestamp'])
    op.add_column('users', sa.Column('registration_timestamp', sa.DateTime(), nullable=True))
    op.create_unique_constraint('uix_user_reg_time', 'users', ['id', 'registration_timestamp'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uix_user_reg_time', 'users', type_='unique')
    op.drop_column('users', 'registration_timestamp')
    op.drop_constraint('uix_auth_timestamp', 'auth_history', type_='unique')
    # ### end Alembic commands ###