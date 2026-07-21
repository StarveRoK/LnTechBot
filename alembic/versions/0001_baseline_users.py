"""baseline users table

Revision ID: 0001
Revises:
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.Text(), nullable=True),
        sa.Column("money", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("oblaka", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("purchases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("admin", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("discount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("referal", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("server", sa.Text(), nullable=False, server_default="no"),
        sa.Column("price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("use_discount", sa.Text(), nullable=False, server_default="no"),
        sa.Column("inviting_user", sa.Text(), nullable=False, server_default="no"),
        sa.Column("user_invited", sa.Text(), nullable=False, server_default="no"),
        sa.Column("pay_id", sa.Text(), nullable=False, server_default="0"),
        sa.Column("url_pay", sa.Text(), nullable=False, server_default="no"),
        sa.UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
    )


def downgrade() -> None:
    op.drop_table("users")
