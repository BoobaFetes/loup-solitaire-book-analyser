"""create db probe table

Revision ID: 002
Revises: 001
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "db_probe",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("message", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("db_probe")
