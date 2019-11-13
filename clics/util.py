from clld.db.meta import DBSession
from clld.db.models.common import Language


def dataset_detail_html(context=None, request=None, **kw):
    return dict(count_langs=DBSession.query(Language).count())
