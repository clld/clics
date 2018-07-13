from __future__ import unicode_literals
import sys
from itertools import chain, groupby
from collections import Counter

from tqdm import tqdm
import transaction
from sqlalchemy.orm import joinedload
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.color import qualitative_colors
from clld.scripts.util import initializedb, Data, bibtex2source

from clldutils.jsonlib import load
from clldutils.path import Path
from pyconcepticon.api import Concepticon

try:
    from pyclics.api import Clics
except ImportError:
    Clics = None

import clics
from clics import models
from clics.scripts.util import iter_dois


def ids(wid1, wid2, wid2pid):
    p1, p2 = wid2pid[wid1], wid2pid[wid2]
    assert p1 != p2
    if int(p1.id) > int(p2.id):
        p1, p2 = p2, p1
        wid1, wid2 = wid2, wid1
    return wid1, wid2, p1, p2


def main(args):
    data = Data()
    api = Clics(Path(clics.__file__).parent.parent.parent / 'clics2')
    concepticon = Concepticon(
        Path(clics.__file__).parent.parent.parent.parent / 'concepticon' / 'concepticon-data')
    concept_definitions = {k: v.definition for k, v in concepticon.conceptsets.items()}

    dataset = common.Dataset(
        id=clics.__name__,
        name="CLICS",
        description="Database of Cross-Linguistic Colexifications",
        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="http://www.shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        domain='clics.clld.org',
        contact='clics@shh.mpg.de',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})

    for i, (id_, name) in enumerate([
        ('list', 'Johann-Mattis List'),
        ('greenhill', 'Simon Greenhill'),
        ('anderson', 'Cormac Anderson'),
        ('mayer', 'Thomas Mayer'),
        ('tresoldi', 'Tiago Tresoldi'),
        ('forkel', 'Robert Forkel'),
    ]):
        ed = data.add(common.Contributor, id_, id=id_, name=name)
        common.Editor(dataset=dataset, contributor=ed, ord=i + 1)
    DBSession.add(dataset)

    dois = dict(iter_dois())
    for dsid, meta in groupby(
            api.db.fetchall("select dataset_id, key, value from datasetmeta order by dataset_id"),
            lambda r: r[0]):
        meta = {r[1]: r[2] for r in meta}
        data.add(
            models.ClicsDataset,
            dsid,
            id=dsid,
            name=meta['dc:title'],
            doi=dois.get(dsid),
            source_citation=meta['dc:bibliographicCitation'])

    for c in sorted(api.db.iter_concepts(), key=lambda c_: int(c_.id)):
        data.add(
            models.Concept,
            c.id,
            id=c.id,
            name=c.gloss,
            description=concept_definitions[c.id],
            category=c.ontological_category,
            semanticfield=c.semantic_field)

    DBSession.flush()
    datasets = {k: obj.pk for k, obj in data['ClicsDataset'].items()}
    concepts = {k: obj.pk for k, obj in data['Concept'].items()}
    transaction.commit()

    wid2cid = {}
    varieties = api.db.varieties
    families = Counter(v.family for v in varieties)
    families = dict(zip([r[0] for r in families.most_common()], qualitative_colors(len(families))))
    for variety, forms in tqdm(api.db.iter_wordlists(varieties), total=len(varieties)):
        transaction.begin()
        data = Data()
        dspk = datasets[variety.source]
        v = models.Doculect(
            id=variety.gid,
            name=variety.name,
            color=families[variety.family],
            family_name=variety.family,
            glottocode=variety.glottocode,
            macroarea=variety.macroarea,
            latitude=variety.latitude,
            longitude=variety.longitude,
            contribution_pk=dspk)

        for form in forms:
            vs = data['ValueSet'].get((variety.id, form.concepticon_id))
            if not vs:
                vs = data.add(
                    common.ValueSet,
                    (variety.id, form.concepticon_id),
                    id='{0}-{1}'.format(variety.gid, form.concepticon_id),
                    language=v,
                    contribution_pk=dspk,
                    parameter_pk=concepts[form.concepticon_id])
            value = models.Form(
                id=form.gid,
                valueset=vs,
                name=form.clics_form,
                source_form=form.form,
                source_gloss=form.gloss)
            wid2cid[value.id] = vs.parameter_pk

        DBSession.add(v)
        transaction.commit()

    c_by_pk, c_by_id = {}, {}
    for c in DBSession.query(models.Concept):
        c_by_id[c.id] = c
        c_by_pk[c.pk] = c
    for k in wid2cid:
        wid2cid[k] = c_by_pk[wid2cid[k]]
    values = {v.id: v.pk for v in DBSession.query(common.Value)}
    varieties = {v.id: v.pk for v in DBSession.query(models.Doculect)}

    data = Data()
    g = api.load_graph('network', threshold=3, edgefilter='families')
    for nodeA, nodeB, data_ in tqdm(g.edges(data=True), desc='loading colexifications'):
        for word in data_['wofam'].split(';'):
            w1, w2, entry, lid, fam, ovalA, ovalB = word.split('/')
            lo_wid, hi_wid, lo_c, hi_c = ids(w1, w2, wid2cid)
            eid = '{0}-{1}'.format(lo_c.id, hi_c.id)
            edge = data['Edge'].get(eid)
            if not edge:
                edge = data.add(
                    models.Edge,
                    eid,
                    id=eid,
                    name='"{0}" and "{1}"'.format(lo_c.name, hi_c.name),
                    lo_concept=lo_c,
                    hi_concept=hi_c)
            DBSession.add(models.Colexification(
                id='{0}__{1}'.format(lo_wid, hi_wid),
                name=entry,
                language_pk=varieties[lid],
                edge=edge,
                lo_word_pk=values[lo_wid],
                hi_word_pk=values[hi_wid]))

    edges = set((e.lo_concept.id, e.hi_concept.id) for e in data['Edge'].values())

    def make_graph(id_, name, type_, nodes, concept=None):
        nodeset = set(nodes)
        if len(nodeset) > 1:
            graph = models.Graph(
                id=id_,
                name=name,
                type=type_,
                concept_pk=concept.pk if concept else None,
                count_concepts=len(nodeset),
                count_edges=sum(1 for e in edges if nodeset.issuperset(e)))
            for node in nodeset:
                models.GraphConcept(graph=graph, concept=c_by_id[node])
            DBSession.add(graph)

    for fname in tqdm(api.path('app', 'cluster').glob('*.json'), desc='loading cluster graphs'):
        make_graph(
            fname.stem,
            fname.stem.split('_', 2)[2],
            'cluster',
            [n['ID'] for n in load(fname)['nodes']])

    graph = api.load_graph('subgraph', threshold=3, edgefilter='families')
    for node, data in tqdm(graph.nodes(data=True), desc='loading subgraphs'):
        make_graph(
            'subgraph_{0}'.format(node),
            '{0}'.format(data['Gloss']),
            'subgraph',
            data['subgraph'],
            concept=c_by_id[node])

    return

    for rec in Database.from_file(args.data_file('cldf', 'sources.bib'), lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    for src in ds['Source'].split(','):
        common.ContributionReference(contribution=contrib, source=data['Source'][src])


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    for concept in DBSession.query(common.Parameter).options(joinedload(common.Parameter.valuesets)):
        concept.count_varieties = len(concept.valuesets)
        concept.count_colexifications = len(concept.edges)

    for v in DBSession.query(common.Language).options(joinedload(common.Language.valuesets)):
        v.count_concepts = len(v.valuesets)

    concept_counts = {
        r[0]: r[1] for r in DBSession.execute(
        "select contribution_pk, count(distinct parameter_pk) from valueset group by contribution_pk")}
    for ds in DBSession.query(models.ClicsDataset).options(joinedload(models.ClicsDataset.doculects)):
        ds.count_varieties = len(ds.doculects)
        ds.count_concepts = concept_counts[ds.pk]


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
