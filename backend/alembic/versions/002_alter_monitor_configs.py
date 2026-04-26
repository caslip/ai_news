"""Alter monitor_configs table to new schema

Revision ID: 002_alter_monitor_configs
Revises: 001_initial
Create Date: 2026-04-23

This migration alters the monitor_configs table to support the new
keyword/account monitoring schema with config_type, name, value, params columns.
Idempotent and SQLite-compatible.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '002_alter_monitor_configs'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Check if monitor_configs table exists
    result = conn.execute(sa.text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='monitor_configs'"
    ))
    table_exists = result.fetchone() is not None

    if not table_exists:
        # Fresh database - create table with new schema
        op.create_table(
            'monitor_configs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('config_type', sa.String(50), nullable=False, server_default='keyword'),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('value', sa.String(500), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
            sa.Column('params', sa.JSON(), server_default='{}', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        )
        op.create_index('ix_monitor_configs_user', 'monitor_configs', ['user_id'])
        op.create_index('ix_monitor_configs_type', 'monitor_configs', ['config_type'])
        return

    # Existing table - get columns
    result = conn.execute(sa.text("PRAGMA table_info(monitor_configs)"))
    columns = {row[1]: row for row in result.fetchall()}
    existing_col_names = set(columns.keys())

    has_old_schema = 'keywords' in existing_col_names or 'twitter_accounts' in existing_col_names

    if has_old_schema:
        # Add new columns (SQLite allows adding nullable columns)
        if 'config_type' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('config_type', sa.String(50), nullable=True))
        if 'name' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('name', sa.String(255), nullable=True))
        if 'value' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('value', sa.String(500), nullable=True))
        if 'params' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('params', sa.JSON(), nullable=True))

        # Migrate data: keywords JSON array -> keyword configs
        op.execute(sa.text("""
            UPDATE monitor_configs
            SET config_type = 'keyword',
                name = json_extract(keywords, '$[0]'),
                value = json_extract(keywords, '$[0]'),
                params = keywords,
                updated_at = CURRENT_TIMESTAMP
            WHERE keywords IS NOT NULL
              AND json_valid(keywords) = 1
              AND json_array_length(keywords) > 0
              AND config_type IS NULL
        """))

        # Migrate data: twitter_accounts JSON array -> account configs
        op.execute(sa.text("""
            UPDATE monitor_configs
            SET config_type = 'account',
                name = '@' || json_extract(twitter_accounts, '$[0]'),
                value = json_extract(twitter_accounts, '$[0]'),
                params = twitter_accounts,
                updated_at = CURRENT_TIMESTAMP
            WHERE twitter_accounts IS NOT NULL
              AND json_valid(twitter_accounts) = 1
              AND json_array_length(twitter_accounts) > 0
              AND config_type IS NULL
        """))

        # Default for rows with empty/null arrays
        op.execute(sa.text("""
            UPDATE monitor_configs
            SET config_type = 'keyword',
                name = COALESCE(name, 'unnamed'),
                value = COALESCE(value, 'unnamed'),
                params = COALESCE(params, '{}')
            WHERE config_type IS NULL
        """))

        # Drop old columns
        op.drop_column('monitor_configs', 'keywords')
        op.drop_column('monitor_configs', 'twitter_accounts')

        # Recreate table with NOT NULL constraints (SQLite doesn't support ALTER COLUMN SET NOT NULL)
        # We do this by: rename old table, create new table, copy data
        op.execute(sa.text("ALTER TABLE monitor_configs RENAME TO monitor_configs_old"))

        op.create_table(
            'monitor_configs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('config_type', sa.String(50), nullable=False, server_default='keyword'),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('value', sa.String(500), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
            sa.Column('params', sa.JSON(), server_default='{}', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        )

        # Copy data back
        op.execute(sa.text("""
            INSERT INTO monitor_configs (id, user_id, config_type, name, value, is_active, params, created_at, updated_at)
            SELECT id, user_id,
                   COALESCE(config_type, 'keyword'),
                   COALESCE(name, 'unnamed'),
                   COALESCE(value, 'unnamed'),
                   COALESCE(is_active, 1),
                   COALESCE(params, '{}'),
                   COALESCE(created_at, CURRENT_TIMESTAMP),
                   COALESCE(updated_at, CURRENT_TIMESTAMP)
            FROM monitor_configs_old
        """))

        op.execute(sa.text("DROP TABLE monitor_configs_old"))

        # Recreate indexes
        op.create_index('ix_monitor_configs_user', 'monitor_configs', ['user_id'])
        op.create_index('ix_monitor_configs_type', 'monitor_configs', ['config_type'])

    else:
        # New schema already present - just ensure columns exist
        if 'config_type' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('config_type', sa.String(50), nullable=False, server_default='keyword'))
        if 'name' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('name', sa.String(255), nullable=False))
        if 'value' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('value', sa.String(500), nullable=False))
        if 'params' not in existing_col_names:
            op.add_column('monitor_configs', sa.Column('params', sa.JSON(), nullable=False))

        # Recreate table with constraints
        op.execute(sa.text("ALTER TABLE monitor_configs RENAME TO monitor_configs_old"))

        op.create_table(
            'monitor_configs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('config_type', sa.String(50), nullable=False, server_default='keyword'),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('value', sa.String(500), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
            sa.Column('params', sa.JSON(), server_default='{}', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        )

        op.execute(sa.text("""
            INSERT INTO monitor_configs (id, user_id, config_type, name, value, is_active, params, created_at, updated_at)
            SELECT id, user_id,
                   COALESCE(config_type, 'keyword'),
                   COALESCE(name, 'unnamed'),
                   COALESCE(value, 'unnamed'),
                   COALESCE(is_active, 1),
                   COALESCE(params, '{}'),
                   COALESCE(created_at, CURRENT_TIMESTAMP),
                   COALESCE(updated_at, CURRENT_TIMESTAMP)
            FROM monitor_configs_old
        """))

        op.execute(sa.text("DROP TABLE monitor_configs_old"))
        op.create_index('ix_monitor_configs_user', 'monitor_configs', ['user_id'])
        op.create_index('ix_monitor_configs_type', 'monitor_configs', ['config_type'])


def downgrade() -> None:
    """Downgrade is not supported for this migration as it involves data transformation."""
    pass
