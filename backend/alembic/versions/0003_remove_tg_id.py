from alembic import op
import sqlalchemy as sa


revision = "0003_remove_tg_id"
down_revision = "0002_add_unique_phone_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_users_tg_id", table_name="users")
    op.drop_column("users", "tg_id")


def downgrade() -> None:
    op.add_column("users", sa.Column("tg_id", sa.BigInteger(), nullable=False))
    op.create_index("ix_users_tg_id", "users", ["tg_id"], unique=True)
