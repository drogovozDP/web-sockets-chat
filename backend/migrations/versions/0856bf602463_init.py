"""Init

Revision ID: 0856bf602463
Revises: 
Create Date: 2023-03-25 20:56:30.870856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0856bf602463'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('registered_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('sender', sa.Integer(), nullable=True),
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.ForeignKeyConstraint(['sender'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unchecked_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('unchecked_message')
    op.drop_table('user_chat')
    op.drop_table('message')
    op.drop_table('chat')
    op.drop_table('auth_user')
    # ### end Alembic commands ###