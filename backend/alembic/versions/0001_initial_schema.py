"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-05-29 23:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Create hotels table
    op.create_table(
        'hotels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=120), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('amenities', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hotels_city'), 'hotels', ['city'], unique=False)
    op.create_index(op.f('ix_hotels_id'), 'hotels', ['id'], unique=False)
    op.create_index(op.f('ix_hotels_name'), 'hotels', ['name'], unique=False)

    # 3. Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hotel_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=80), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('availability', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rooms_hotel_id'), 'rooms', ['hotel_id'], unique=False)
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)

    # 4. Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('hotel_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('check_in', sa.Date(), nullable=True),
        sa.Column('check_out', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('HOLD', 'CONFIRMED', 'CANCELLED', name='bookingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_hotel_id'), 'bookings', ['hotel_id'], unique=False)
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_user_id'), 'bookings', ['user_id'], unique=False)

    # 5. Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_session_id'), 'conversations', ['session_id'], unique=True)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # 6. Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    # 7. Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('hotel_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('ai_draft_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_hotel_id'), 'reviews', ['hotel_id'], unique=False)
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    op.create_index(op.f('ix_reviews_user_id'), 'reviews', ['user_id'], unique=False)

    # 8. Create hitl_tickets table
    op.create_table(
        'hitl_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=60), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'EDITED', name='hitlstatus'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='hitlpriority'), nullable=False),
        sa.Column('ai_draft', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('booking_amount', sa.Float(), nullable=True),
        sa.Column('fraud_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hitl_tickets_id'), 'hitl_tickets', ['id'], unique=False)
    op.create_index(op.f('ix_hitl_tickets_status'), 'hitl_tickets', ['status'], unique=False)
    op.create_index(op.f('ix_hitl_tickets_type'), 'hitl_tickets', ['type'], unique=False)

    # 9. Create pricing_snapshots table
    op.create_table(
        'pricing_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hotel_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pricing_snapshots_hotel_id'), 'pricing_snapshots', ['hotel_id'], unique=False)
    op.create_index(op.f('ix_pricing_snapshots_id'), 'pricing_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_pricing_snapshots_timestamp'), 'pricing_snapshots', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_pricing_snapshots_timestamp'), table_name='pricing_snapshots')
    op.drop_index(op.f('ix_pricing_snapshots_id'), table_name='pricing_snapshots')
    op.drop_index(op.f('ix_pricing_snapshots_hotel_id'), table_name='pricing_snapshots')
    op.drop_table('pricing_snapshots')

    op.drop_index(op.f('ix_hitl_tickets_type'), table_name='hitl_tickets')
    op.drop_index(op.f('ix_hitl_tickets_status'), table_name='hitl_tickets')
    op.drop_index(op.f('ix_hitl_tickets_id'), table_name='hitl_tickets')
    op.drop_table('hitl_tickets')

    op.drop_index(op.f('ix_reviews_user_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_hotel_id'), table_name='reviews')
    op.drop_table('reviews')

    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')

    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_session_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')

    op.drop_index(op.f('ix_bookings_user_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_hotel_id'), table_name='bookings')
    op.drop_table('bookings')

    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_hotel_id'), table_name='rooms')
    op.drop_table('rooms')

    op.drop_index(op.f('ix_hotels_name'), table_name='hotels')
    op.drop_index(op.f('ix_hotels_id'), table_name='hotels')
    op.drop_index(op.f('ix_hotels_city'), table_name='hotels')
    op.drop_table('hotels')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
