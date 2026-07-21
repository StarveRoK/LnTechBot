"""reconcile pre-existing legacy users table (lntech_tg) with baseline schema

На проде users уже существовала до перехода на Alembic (старая база lntech_tg,
из-за которой упал `alembic upgrade head` с DuplicateTable — таблица 0001
создавать не должна была, она уже там). Эта миграция не создаёт таблицу,
а докручивает её схему до состояния 0001: добавляет UNIQUE(telegram_id)
(нужен для `ON CONFLICT (telegram_id) DO NOTHING` в pgsql/database.py),
NOT NULL + server_default на счётчики/флаги, TEXT вместо varchar(255),
double precision вместо real для price. NULL-значения перед SET NOT NULL
бэкоффиллятся дефолтом, данные не удаляются и не перезаписываются.

Revision ID: 0001a
Revises: 0001
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001a"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (column, default_sql_literal)
_NOT_NULL_DEFAULTS = [
    ("money", "0"),
    ("oblaka", "1"),
    ("purchases", "0"),
    ("admin", "0"),
    ("discount", "0"),
    ("referal", "0"),
    ("server", "'no'"),
    ("price", "0"),
    ("use_discount", "'no'"),
    ("inviting_user", "'no'"),
    ("user_invited", "'no'"),
    ("pay_id", "'0'"),
    ("url_pay", "'no'"),
]


def upgrade() -> None:
    # varchar(255) -> text (шире, без риска обрезания существующих значений)
    op.alter_column("users", "username", type_=sa.Text())
    op.alter_column("users", "pay_id", type_=sa.Text())

    # real -> double precision, как ожидает sa.Float() в коде
    op.alter_column("users", "price", type_=sa.Float())

    for column, default in _NOT_NULL_DEFAULTS:
        op.execute(f"UPDATE users SET {column} = {default} WHERE {column} IS NULL")
        op.alter_column("users", column, server_default=sa.text(str(default)), nullable=False)

    # telegram_id — естественный ключ пользователя, безопасного дефолта для NULL нет:
    # если такие строки есть, ALTER упадёт явной ошибкой вместо того, чтобы что-то придумывать.
    op.alter_column("users", "telegram_id", nullable=False)

    # На свежей базе 0001 уже создаёт этот constraint инлайново (UniqueConstraint в create_table) —
    # проверяем, чтобы не словить "constraint already exists" при накатке миграций с нуля.
    inspector = sa.inspect(op.get_bind())
    existing_unique = {uc["name"] for uc in inspector.get_unique_constraints("users")}
    if "uq_users_telegram_id" not in existing_unique:
        op.create_unique_constraint("uq_users_telegram_id", "users", ["telegram_id"])


def downgrade() -> None:
    op.drop_constraint("uq_users_telegram_id", "users", type_="unique")
    op.alter_column("users", "telegram_id", nullable=True)

    for column, _default in _NOT_NULL_DEFAULTS:
        op.alter_column("users", column, server_default=None, nullable=True)

    op.alter_column("users", "price", type_=sa.Float())
    op.alter_column("users", "pay_id", type_=sa.String(255))
    op.alter_column("users", "username", type_=sa.String(255))
