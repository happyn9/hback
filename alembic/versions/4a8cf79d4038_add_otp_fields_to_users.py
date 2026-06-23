"""add otp fields to users

Revision ID: 4a8cf79d4038
Revises: edea99564e0c
Create Date: 2026-06-23

"""
from alembic import op
import sqlalchemy as sa

revision = '4a8cf79d4038'
down_revision = 'edea99564e0c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('otp_code', sa.String(), nullable=True))
    op.add_column('users', sa.Column('otp_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'otp_expires_at')
    op.drop_column('users', 'otp_code')
