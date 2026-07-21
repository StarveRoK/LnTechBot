"""app_settings key/value table for discount percentages

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

app_settings_table = sa.table(
    "app_settings",
    sa.column("key", sa.Text),
    sa.column("value", sa.Text),
)

# Percentages carried over as-is from the hardcoded literals this replaces:
# pgsql/database.py: add_discount_oblaka (20) and add_referal_discount (10).
SETTINGS = [
    {"key": "oblaka_discount_percent", "value": "20"},
    {"key": "referal_discount_percent", "value": "10"},
]


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.Text(), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
    )
    op.bulk_insert(app_settings_table, SETTINGS)


def downgrade() -> None:
    op.drop_table("app_settings")
