"""empty message

Revision ID: 011d88b5457a
Revises: 400bda6f061e
Create Date: 2024-11-11 19:01:33.313540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011d88b5457a'
down_revision = '400bda6f061e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.drop_constraint('goal_task_id_fkey', type_='foreignkey')
        batch_op.drop_column('task_id')

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('goal_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'goal', ['goal_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('goal_id')

    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('task_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('goal_task_id_fkey', 'task', ['task_id'], ['id'])

    # ### end Alembic commands ###
