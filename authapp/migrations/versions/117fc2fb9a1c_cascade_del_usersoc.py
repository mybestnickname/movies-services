"""+ cascade del usersoc

Revision ID: 117fc2fb9a1c
Revises: 2b71335ffcb4
Create Date: 2022-06-28 12:31:26.098014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '117fc2fb9a1c'
down_revision = '2b71335ffcb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'social_account', ['id'])
    op.drop_constraint('social_account_user_id_fkey', 'social_account', type_='foreignkey')
    op.create_foreign_key(None, 'social_account', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'social_account', type_='foreignkey')
    op.create_foreign_key('social_account_user_id_fkey', 'social_account', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'social_account', type_='unique')
    # ### end Alembic commands ###