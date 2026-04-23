"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('nickname', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('oauth_provider', sa.String(20), nullable=True),
        sa.Column('oauth_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_superuser', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_oauth', 'users', ['oauth_provider', 'oauth_id'])

    # Create sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),  # rss, twitter, github
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('last_fetched_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_sources_user', 'sources', ['user_id'])
    op.create_index('ix_sources_type', 'sources', ['type'])
    op.create_index('ix_sources_active', 'sources', ['is_active'])

    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('sources.id'), nullable=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('url', sa.String(500), nullable=False, unique=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('author', sa.String(255), nullable=True),
        sa.Column('author_followers', sa.Integer(), default=0),
        sa.Column('author_url', sa.String(500), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('hot_score', sa.Float(), default=0.0),
        sa.Column('is_low_fan_viral', sa.Boolean(), default=False),
        sa.Column('engagement', postgresql.JSONB(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('is_analyzed', sa.Boolean(), default=False),
        sa.Column('is_bookmarked', sa.Boolean(), default=False),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_articles_source', 'articles', ['source_id'])
    op.create_index('ix_articles_user', 'articles', ['user_id'])
    op.create_index('ix_articles_hot_score', 'articles', ['hot_score'])
    op.create_index('ix_articles_is_low_fan_viral', 'articles', ['is_low_fan_viral'])
    op.create_index('ix_articles_published_at', 'articles', ['published_at'])
    op.create_index('ix_articles_content_hash', 'articles', ['content_hash'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_tags_user', 'tags', ['user_id'])
    op.create_index('ix_tags_user_name', 'tags', ['user_id', 'name'], unique=True)

    # Create bookmarks table
    op.create_table(
        'bookmarks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('article_id', sa.String(36), sa.ForeignKey('articles.id'), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_bookmarks_user', 'bookmarks', ['user_id'])
    op.create_index('ix_bookmarks_article', 'bookmarks', ['article_id'])
    op.create_index('ix_bookmarks_user_article', 'bookmarks', ['user_id', 'article_id'], unique=True)

    # Create strategies table
    op.create_table(
        'strategies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=False),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('params', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_strategies_user', 'strategies', ['user_id'])
    op.create_index('ix_strategies_active', 'strategies', ['is_active'])

    # Create monitor_configs table
    op.create_table(
        'monitor_configs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('config_type', sa.String(20), nullable=False),  # keyword, account
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('value', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('params', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_monitor_user', 'monitor_configs', ['user_id'])
    op.create_index('ix_monitor_type', 'monitor_configs', ['config_type'])
    op.create_index('ix_monitor_active', 'monitor_configs', ['is_active'])

    # Create article_tags association table
    op.create_table(
        'article_tags',
        sa.Column('article_id', sa.String(36), sa.ForeignKey('articles.id'), primary_key=True),
        sa.Column('tag_id', sa.String(36), sa.ForeignKey('tags.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Create bookmark_tags association table
    op.create_table(
        'bookmark_tags',
        sa.Column('bookmark_id', sa.String(36), sa.ForeignKey('bookmarks.id'), primary_key=True),
        sa.Column('tag_id', sa.String(36), sa.ForeignKey('tags.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('bookmark_tags')
    op.drop_table('article_tags')
    op.drop_table('monitor_configs')
    op.drop_table('strategies')
    op.drop_table('bookmarks')
    op.drop_table('tags')
    op.drop_table('articles')
    op.drop_table('sources')
    op.drop_table('users')
