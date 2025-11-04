"""Initial migration

Revision ID: 001
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('user', 'operator', 'admin', name='userrole'), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('status', sa.Enum('active', 'suspended', 'banned', name='userstatus'), nullable=False),
        sa.Column('ban_reason', sa.String(length=500), nullable=True),
        sa.Column('ban_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('company', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_id', 'users', ['id'])

    # Create servers table
    op.create_table(
        'servers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('api_url', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=True, server_default='8006'),
        sa.Column('api_token_encrypted', sa.Text(), nullable=False),
        sa.Column('verify_ssl', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('status', sa.Enum('online', 'offline', 'error', 'maintenance', name='serverstatus'), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('total_cpu_cores', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('used_cpu_cores', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_ram_mb', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('used_ram_mb', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_disk_gb', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('used_disk_gb', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('allow_vm_creation', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('datacenter', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_servers_name', 'servers', ['name'])

    # Create vm_templates table
    op.create_table(
        'vm_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cpu_cores', sa.Integer(), nullable=False),
        sa.Column('ram_mb', sa.Integer(), nullable=False),
        sa.Column('disk_gb', sa.Integer(), nullable=False),
        sa.Column('os_type', sa.String(length=50), nullable=False),
        sa.Column('os_name', sa.String(length=100), nullable=False),
        sa.Column('proxmox_template_id', sa.Integer(), nullable=True),
        sa.Column('cloud_init_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('cloud_init_config', sa.Text(), nullable=True),
        sa.Column('cost_per_hour', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('min_cpu', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('max_cpu', sa.Integer(), nullable=True, server_default='8'),
        sa.Column('min_ram_mb', sa.Integer(), nullable=True, server_default='512'),
        sa.Column('max_ram_mb', sa.Integer(), nullable=True, server_default='32768'),
        sa.Column('min_disk_gb', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('max_disk_gb', sa.Integer(), nullable=True, server_default='500'),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_vm_templates_name', 'vm_templates', ['name'])

    # Create user_vms table
    op.create_table(
        'user_vms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('server_id', sa.Integer(), nullable=False),
        sa.Column('proxmox_vm_id', sa.Integer(), nullable=True),
        sa.Column('node_name', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('hostname', sa.String(length=100), nullable=True),
        sa.Column('cpu_cores', sa.Integer(), nullable=False),
        sa.Column('ram_mb', sa.Integer(), nullable=False),
        sa.Column('disk_gb', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('mac_address', sa.String(length=17), nullable=True),
        sa.Column('state', sa.Enum('creating', 'running', 'stopped', 'suspended', 'error', 'deleting', 'deleted', name='vmstate'), nullable=False),
        sa.Column('last_billed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_cost', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['vm_templates.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_vms_state', 'user_vms', ['state'])
    op.create_index('ix_user_vms_user_id', 'user_vms', ['user_id'])

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('type', sa.Enum('credit', 'debit', 'admin_adjust', 'refund', 'payment', name='transactiontype'), nullable=False),
        sa.Column('vm_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('payment_id', sa.String(length=255), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('balance_after', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vm_id'], ['user_vms.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'])
    op.create_index('ix_transactions_payment_id', 'transactions', ['payment_id'])
    op.create_index('ix_transactions_type', 'transactions', ['type'])
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])

    # Create logs table
    op.create_table(
        'logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_logs_action', 'logs', ['action'])
    op.create_index('ix_logs_created_at', 'logs', ['created_at'])
    op.create_index('ix_logs_user_id', 'logs', ['user_id'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='taskstatus'), nullable=False),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('progress_message', sa.String(length=500), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_celery_task_id', 'tasks', ['celery_task_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_type', 'tasks', ['type'])


def downgrade() -> None:
    op.drop_table('tasks')
    op.drop_table('logs')
    op.drop_table('transactions')
    op.drop_table('user_vms')
    op.drop_table('vm_templates')
    op.drop_table('servers')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS vmstate')
    op.execute('DROP TYPE IF EXISTS serverstatus')
    op.execute('DROP TYPE IF EXISTS userstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
