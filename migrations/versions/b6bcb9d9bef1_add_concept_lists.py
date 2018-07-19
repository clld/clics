# coding=utf-8
"""add concept lists

Revision ID: b6bcb9d9bef1
Revises: None
Create Date: 2018-07-19 14:29:46.534279

"""

# revision identifiers, used by Alembic.
revision = 'b6bcb9d9bef1'
down_revision = None

import json
import datetime

from alembic import op
import sqlalchemy as sa


CL_URLS = {
    'lexibank-allenbai': 'http://concepticon.clld.org/contributions/Allen-2007-500',
    'lexibank-bantubvd': 'http://concepticon.clld.org/contributions/TeilDautrey-2008-430',
    'lexibank-beidasinitic': 'http://concepticon.clld.org/contributions/BeijingDaxue-1964-905',
    'lexibank-bowernpny': 'http://concepticon.clld.org/contributions/Bowern-2017-348',
    'lexibank-hubercolumbian': 'http://concepticon.clld.org/contributions/Huber-1992-374',
    'lexibank-ids': 'http://concepticon.clld.org/contributions/Key-2016-1310',
    'lexibank-kraftchadic': 'http://concepticon.clld.org/contributions/Kraft-1981-434',
    'lexibank-northeuralex': 'http://concepticon.clld.org/contributions/Dellert-2017-1016',
    'lexibank-robinsonap': 'http://concepticon.clld.org/contributions/Robinson-2012-398',
    'lexibank-satterthwaitetb': 'http://concepticon.clld.org/contributions/SatterthwaitePhillips-2011-423',
    'lexibank-suntb': 'http://concepticon.clld.org/contributions/Sun-1991-1004',
    'lexibank-tryonsolomon': 'http://concepticon.clld.org/contributions/Tryon-1983-324',
    'lexibank-wold': 'http://concepticon.clld.org/contributions/Haspelmath-2009-1460',
    'lexibank-zgraggenmadang': 'http://concepticon.clld.org/contributions/Zgraggen-1980-380',
}


def upgrade():
    conn = op.get_bind()
    for cid, clurl in CL_URLS.items():
        conn.execute(
            "update contribution set jsondata = %s where id = %s",
            (json.dumps(dict(cl_url=clurl)), cid))


def downgrade():
    pass
