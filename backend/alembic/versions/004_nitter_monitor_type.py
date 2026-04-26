"""Set monitor_type='nitter' for existing Nitter sources

Revision ID: 004_nitter_monitor_type
Revises: 003_merge_monitor_configs
Create Date: 2026-04-26

将为所有 type='nitter' 的信源设置 monitor_type='nitter'，
使其能在 X 监控页面统一管理和显示。
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_nitter_monitor_type'
down_revision: Union[str, None] = '003_merge_monitor_configs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 为所有 type='nitter' 的信源设置 monitor_type='nitter'
    op.execute(sa.text("""
        UPDATE sources
        SET monitor_type = 'nitter'
        WHERE type = 'nitter' AND monitor_type IS NULL
    """))


def downgrade() -> None:
    # 不需要回滚，因为这是可选的补充字段
    pass
