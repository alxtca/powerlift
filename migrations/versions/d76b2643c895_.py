"""empty message

Revision ID: d76b2643c895
Revises: f40795e5850c
Create Date: 2021-01-27 11:44:15.355656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd76b2643c895'
down_revision = 'f40795e5850c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workout', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_workout_timestamp'), 'workout', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_workout_timestamp'), table_name='workout')
    op.drop_column('workout', 'timestamp')
    # ### end Alembic commands ###
