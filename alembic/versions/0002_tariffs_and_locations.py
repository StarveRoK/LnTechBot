"""tariffs and locations catalog

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

locations_table = sa.table(
    "locations",
    sa.column("flag", sa.Text),
    sa.column("country", sa.Text),
)

tariffs_table = sa.table(
    "tariffs",
    sa.column("code", sa.Text),
    sa.column("flag", sa.Text),
    sa.column("cores", sa.Integer),
    sa.column("ram_gb", sa.Integer),
    sa.column("ssd_gb", sa.Integer),
    sa.column("price", sa.Float),
    sa.column("is_visible", sa.Boolean),
    sa.column("sort_order", sa.Integer),
)

# Values carried over as-is from the hardcoded app/description.py catalog this replaces.
LOCATIONS = [
    {"flag": "🇷🇺", "country": "Россия"},
    {"flag": "🇵🇱", "country": "Польша"},
    {"flag": "🇺🇸", "country": "США"},
]

TARIFFS = [
    ("serv_0", "🇷🇺", 4, 8, 2400, True),
    ("serv_1", "🇷🇺", 6, 16, 4000, True),
    ("serv_2", "🇷🇺", 8, 24, 5500, True),
    ("serv_3", "🇷🇺", 10, 32, 7000, True),
    ("serv_4", "🇵🇱", 4, 8, 2400, True),
    ("serv_5", "🇵🇱", 6, 16, 4000, True),
    ("serv_6", "🇵🇱", 8, 24, 5500, True),
    ("serv_7", "🇵🇱", 10, 32, 7000, True),
    ("serv_8", "🇺🇸", 4, 8, 2400, True),
    ("serv_9", "🇺🇸", 6, 16, 4000, True),
    ("serv_10", "🇺🇸", 8, 24, 5500, True),
    ("serv_11", "🇺🇸", 10, 32, 7000, True),
    # Hidden admin-only entry used by the admin panel's "Проверить оплату" button.
    ("check_kassa", "🇷🇺", 0, 0, 100, False),
]


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("flag", sa.Text(), primary_key=True),
        sa.Column("country", sa.Text(), nullable=False),
    )

    op.create_table(
        "tariffs",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("flag", sa.Text(), nullable=False),
        sa.Column("cores", sa.Integer(), nullable=False),
        sa.Column("ram_gb", sa.Integer(), nullable=False),
        sa.Column("ssd_gb", sa.Integer(), nullable=False, server_default="128"),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False),
    )

    op.bulk_insert(locations_table, LOCATIONS)
    op.bulk_insert(
        tariffs_table,
        [
            {
                "code": code,
                "flag": flag,
                "cores": cores,
                "ram_gb": ram_gb,
                "ssd_gb": 128,
                "price": float(price),
                "is_visible": is_visible,
                "sort_order": order,
            }
            for order, (code, flag, cores, ram_gb, price, is_visible) in enumerate(TARIFFS)
        ],
    )


def downgrade() -> None:
    op.drop_table("tariffs")
    op.drop_table("locations")
