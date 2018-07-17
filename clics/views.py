from pyramid.view import view_config

from clld.db.meta import DBSession
from clld.db.models.common import Parameter, Contribution

from clics.models import Graph


@view_config(renderer='about.mako')
def about(req):

    # dataset:
    # glosses, concepticon, varieties, glottocodes, families
    sql = """
    select
        vs.contribution_pk,
        count(distinct f.source_gloss) as gloss
    from
        valueset as vs,
        value as v,
        form as f
    where
        v.pk = f.pk and v.valueset_pk = vs.pk
    group by
        vs.contribution_pk
    """
    datasets = []
    for cpk, g in DBSession.execute(sql):
        datasets.append([Contribution.get(cpk), g])

    sql = """
    select
        e.hi_concept_pk,
        e.lo_concept_pk,
        count(distinct v.family_name) as fc,
        count(distinct co.language_pk) as lc,
        count(co.pk) as wc
    from
        colexification as co, edge as e, doculect as v
    where
        e.pk = co.edge_pk and co.language_pk = v.pk
    group by
        e.hi_concept_pk, e.lo_concept_pk
    order by fc desc, lc desc, wc desc limit 10
    """
    top_ten = []
    for hipk, lopk, fc, vc, cc in DBSession.execute(sql):
        top_ten.append([Parameter.get(hipk), Parameter.get(lopk), fc, vc, cc])

    return {
        'top_ten': top_ten,
        'datasets': datasets,
        'wheel': Graph.get('subgraph_710'),
        'say': Graph.get('infomap_2_SPEAK')
    }
