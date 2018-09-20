# coding=utf-8
"""clics2

Revision ID: 1994db11b384
Revises: b6bcb9d9bef1
Create Date: 2018-09-20 14:53:36.111532

"""
from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '1994db11b384'
down_revision = 'b6bcb9d9bef1'

import datetime

from alembic import op
import sqlalchemy as sa



def upgrade():
    op.get_bind().execute("update dataset set name = %s", ('CLICS²',))


def downgrade():
    pass

