"""init permissions

Revision ID: 3551992da1e1
Revises:
Create Date: 2026-07-13 00:00:00

"""

from typing import Sequence, Union

from alembic import op

revision: str = "3551992da1e1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE
        ON TABLES
        TO db_batch_usr
        """
    )
    op.execute(
        """
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT USAGE, SELECT
        ON SEQUENCES
        TO db_batch_usr
        """
    )
    op.execute(
        """
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT
        ON TABLES
        TO db_webapp_usr
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        REVOKE SELECT, INSERT, UPDATE, DELETE
        ON TABLES
        FROM db_batch_usr
        """
    )
    op.execute(
        """
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        REVOKE USAGE, SELECT
        ON SEQUENCES
        FROM db_batch_usr
        """
    )
    op.execute(
        """
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        REVOKE SELECT
        ON TABLES
        FROM db_webapp_usr
        """
    )
