"""empty message

Revision ID: 79de1676ee1d
Revises: 
Create Date: 2018-10-08 23:43:57.191590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79de1676ee1d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('songs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('spotify_uri', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('album', sa.String(), nullable=True),
    sa.Column('artists', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('spotify_uri')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('spotify_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('spotify_id')
    )
    op.create_table('playlists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('playlist_id', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('p_type', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('playlist_id')
    )
    op.create_table('tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(), nullable=True),
    sa.Column('refresh_token', sa.String(), nullable=True),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('belongs_to',
    sa.Column('song_id', sa.Integer(), nullable=False),
    sa.Column('playlist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['playlist_id'], ['playlists.id'], ),
    sa.ForeignKeyConstraint(['song_id'], ['songs.id'], ),
    sa.PrimaryKeyConstraint('song_id', 'playlist_id')
    )
    op.create_table('follow_playlists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('following', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['playlists.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fresh_playlists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stale_period_days', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['playlists.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fresh_playlists')
    op.drop_table('follow_playlists')
    op.drop_table('belongs_to')
    op.drop_table('tokens')
    op.drop_table('playlists')
    op.drop_table('users')
    op.drop_table('songs')
    # ### end Alembic commands ###
