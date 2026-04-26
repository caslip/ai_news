"""Migration 003: Merge monitor_configs into sources table

Revision ID: 003_merge_monitor_configs
Revises: 002_alter_monitor_configs
Create Date: 2026-04-25

将 keyword（关键词监控）和 account（账号监控）的配置从 monitor_configs 表
迁移到 sources 表，添加 monitor_type 和 user_id 字段。

迁移完成后：
- sources 表新增 user_id 字段（允许 null，兼容旧的系统信源）
- sources 表新增 monitor_type 字段（'keyword' | 'account' | null）
- sources 表的 type 字段含义不变（'rss' | 'twitter' | 'github' | 'nitter'）
- type='keyword' 表示关键词监控配置，type='account' 表示账号监控配置
- monitor_configs 表被删除
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_merge_monitor_configs'
down_revision: Union[str, None] = '002_alter_monitor_configs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Step 1: 添加新字段到 sources 表
    if not _column_exists(conn, 'sources', 'user_id'):
        op.add_column('sources', sa.Column('user_id', sa.String(36), nullable=True))
        op.create_index('ix_sources_user', 'sources', ['user_id'])

    if not _column_exists(conn, 'sources', 'monitor_type'):
        op.add_column('sources', sa.Column('monitor_type', sa.String(20), nullable=True))
        op.create_index('ix_sources_monitor_type', 'sources', ['monitor_type'])

    # Step 2: 迁移 keyword 配置 -> type='keyword'
    op.execute(sa.text("""
        INSERT INTO sources (id, name, type, config, is_active, user_id, monitor_type, created_at, updated_at)
        SELECT
            id,
            name,
            'keyword',
            json('{"keyword": "' || value || '", "params": ' || COALESCE(params, '{}') || '}'),
            is_active,
            user_id,
            'keyword',
            created_at,
            updated_at
        FROM monitor_configs
        WHERE config_type = 'keyword'
    """))

    # Step 3: 迁移 account 配置 -> type='account'
    op.execute(sa.text("""
        INSERT INTO sources (id, name, type, config, is_active, user_id, monitor_type, created_at, updated_at)
        SELECT
            id,
            name,
            'account',
            json('{"account": "' || value || '", "params": ' || COALESCE(params, '{}') || '}'),
            is_active,
            user_id,
            'account',
            created_at,
            updated_at
        FROM monitor_configs
        WHERE config_type = 'account'
    """))

    # Step 4: 删除 monitor_configs 表
    op.drop_table('monitor_configs')


def downgrade() -> None:
    # Recreate monitor_configs table
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

    conn = op.get_bind()

    # 恢复 keyword 配置
    op.execute(sa.text("""
        INSERT INTO monitor_configs (id, user_id, config_type, name, value, is_active, params, created_at, updated_at)
        SELECT
            id,
            user_id,
            'keyword',
            name,
            json_extract(config, '$.keyword'),
            is_active,
            json_extract(config, '$.params'),
            created_at,
            updated_at
        FROM sources
        WHERE type = 'keyword' AND monitor_type = 'keyword'
    """))

    # 恢复 account 配置
    op.execute(sa.text("""
        INSERT INTO monitor_configs (id, user_id, config_type, name, value, is_active, params, created_at, updated_at)
        SELECT
            id,
            user_id,
            'account',
            name,
            json_extract(config, '$.account'),
            is_active,
            json_extract(config, '$.params'),
            created_at,
            updated_at
        FROM sources
        WHERE type = 'account' AND monitor_type = 'account'
    """))

    # 恢复旧 sources 行（user_id 为 null 的）
    op.execute(sa.text("""
        DELETE FROM sources WHERE type = 'keyword' OR type = 'account'
    """))

    # 清理新增的列
    op.drop_column('sources', 'monitor_type')
    op.drop_column('sources', 'user_id')


def _column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(sa.text(f"PRAGMA table_info({table})"))
    columns = [row[1] for row in result.fetchall()]
    return column in columns
