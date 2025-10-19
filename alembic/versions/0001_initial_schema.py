"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

risklevel = postgresql.ENUM('baixo', 'moderado', 'alto', name='risklevel')

def upgrade() -> None:
    # Create ENUM type first
    risklevel.create(op.get_bind(), checkfirst=True)

    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('risk_profile', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('cryptos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cryptos_id'), 'cryptos', ['id'], unique=False)
    op.create_index(op.f('ix_cryptos_symbol'), 'cryptos', ['symbol'], unique=True)

    op.create_table('recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('crypto_id', sa.Integer(), nullable=True),
        sa.Column('risk_level', risklevel, nullable=True),
        sa.Column('recommended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['crypto_id'], ['cryptos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendations_id'), 'recommendations', ['id'], unique=False)

    op.create_table('questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)

    op.create_table('question_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('value', sa.String(length=50), nullable=True),
        sa.Column('label', sa.String(length=255), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_options_id'), 'question_options', ['id'], unique=False)
    op.create_index(op.f('ix_question_options_value'), 'question_options', ['value'], unique=False)

    op.create_table('questionnaire_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('total_score', sa.Integer(), nullable=True),
        sa.Column('max_score', sa.Integer(), nullable=True),
        sa.Column('risk_level', risklevel, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questionnaire_submissions_id'), 'questionnaire_submissions', ['id'], unique=False)

    op.create_table('user_answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('option_id', sa.Integer(), nullable=True),
        sa.Column('selected_value', sa.String(length=50), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['option_id'], ['question_options.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submission_id'], ['questionnaire_submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_answers_id'), 'user_answers', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_answers_id'), table_name='user_answers')
    op.drop_table('user_answers')
    op.drop_index(op.f('ix_questionnaire_submissions_id'), table_name='questionnaire_submissions')
    op.drop_table('questionnaire_submissions')
    op.drop_index(op.f('ix_question_options_value'), table_name='question_options')
    op.drop_index(op.f('ix_question_options_id'), table_name='question_options')
    op.drop_table('question_options')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    op.drop_index(op.f('ix_recommendations_id'), table_name='recommendations')
    op.drop_table('recommendations')
    op.drop_index(op.f('ix_cryptos_symbol'), table_name='cryptos')
    op.drop_index(op.f('ix_cryptos_id'), table_name='cryptos')
    op.drop_table('cryptos')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    # drop ENUM at the end
    bind = op.get_bind()
    risklevel.drop(bind, checkfirst=True)
