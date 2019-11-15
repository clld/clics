from clld.db.meta import DBSession
from clld.db.models.common import Language, Parameter

from clics.models import GraphConcept, Graph, Concept


def dataset_detail_html(context=None, request=None, **kw):
    return dict(
        graph=DBSession.query(Graph).join(GraphConcept).join(Concept)
            .filter(Parameter.name=='FEATHER').filter(Graph.type=='subgraph').first(),
        count_langs=DBSession.query(Language).count())
