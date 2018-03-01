from __future__ import unicode_literals
import sys
from itertools import chain

from sqlalchemy import func, desc
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.color import qualitative_colors
from clld.scripts.util import initializedb, Data, bibtex2source
from clld.lib.bibtex import Database

from clldutils.jsonlib import load
from clldutils.path import as_unicode
from csvw.dsv import reader
from pyconcepticon.api import Concepticon

import clics
from clics import models


def ids(wid1, wid2, wid2pid):
    pid1, pid2 = wid2pid[wid1], wid2pid[wid2]
    assert pid1 != pid2
    if int(pid1) > int(pid2):
        pid1, pid2 = pid2, pid1
        wid1, wid2 = wid2, wid1
    return wid1, wid2, pid1, pid2


def main(args):
    data = Data()
    concepticon = Concepticon()

    dataset = common.Dataset(
        id=clics.__name__,
        name="CLICS",
        description="Database of Cross-Linguistic Colexifications",
        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="http://www.shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        domain='clics.clld.org',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})

    for i, (id_, name) in enumerate([
        ('listmattis', 'Johann-Mattis List'),
        ('forkelrobert', 'Robert Forkel'),
    ]):
        ed = data.add(common.Contributor, id_, id=id_, name=name)
        common.Editor(dataset=dataset, contributor=ed, ord=i + 1)
    DBSession.add(dataset)

    for rec in Database.from_file(args.data_file('cldf', 'sources.bib'), lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    colexifications = list(reader(args.data_file('colexifications.csv'), dicts=True))
    wids = set(chain(*[[c['word_a'], c['word_b']] for c in colexifications]))
    wid2pid = {}
    dss = {d['ID']: d for d in reader(args.data_file('cldf', 'datasets.csv'), dicts=True)}

    # load the lexical data
    for d in args.data_file('cldf').iterdir():
        ds = dss.get(as_unicode(d.name))
        if not ds:
            continue
        print(ds['ID'])
        contrib = models.ClicsDataset(
            id=ds['ID'],
            name=ds['ID'],
            description=ds['Note'],
            author=ds['Author'],
            provider=ds['Provider'],
            provider_url=ds['ProviderUrl'])

        for src in ds['Source'].split(','):
            common.ContributionReference(contribution=contrib, source=data['Source'][src])

        for k, v in load(d / 'md.json').items():
            if k.startswith('_'):
                continue
            lang = models.Doculect(
                id=v['identifier'],
                name=v['name'],
                contribution=contrib,
                family_name=v['name'] if v['family'] == v['glottocode'] else v['family'],
                glottocode=v['glottocode'],
                macroarea=v['macroarea'][0] if v['macroarea'] else None,
                latitude=v['latitude'],
                longitude=v['longitude'])

            for form in reader(d / '{0}.csv'.format(k), dicts=True):
                if form['Source_ID'] not in wids:
                    continue
                pid = form['Parameter_ID']
                param = data['Concept'].get(pid)
                if not param:
                    param = data.add(
                        models.Concept,
                        pid,
                        id=pid,
                        name=concepticon.conceptsets[pid].gloss,
                        description=concepticon.conceptsets[pid].definition,
                        semanticfield=concepticon.conceptsets[pid].semanticfield,
                        category=concepticon.conceptsets[pid].ontological_category,
                    )
                vsid = '{0}-{1}'.format(lang.id, pid)
                vs = data['ValueSet'].get(vsid)
                if not vs:
                    vs = data.add(
                        common.ValueSet,
                        vsid,
                        id=vsid,
                        language=lang,
                        contribution=contrib,
                        parameter=param)
                data.add(
                    common.Value,
                    form['Source_ID'],
                    valueset=vs,
                    id=form['Source_ID'],
                    name=form['Clics_Value'],
                    description=form['Value'])
                wid2pid[form['Source_ID']] = pid

    # enrich with classification data from glottolog

    # load the graphs
    for c in colexifications:
        try:
            lo_wid, hi_wid, lo_cid, hi_cid = ids(c['word_a'], c['word_b'], wid2pid)
        except KeyError:
            continue
        eid = '{0}-{1}'.format(lo_cid, hi_cid)
        edge = data['Edge'].get(eid)
        if not edge:
            lc = data['Concept'][lo_cid]
            hc = data['Concept'][hi_cid]
            edge = data.add(
                models.Edge,
                eid,
                id=eid,
                name='"{0}" and "{1}"'.format(lc.name, hc.name),
                lo_concept=lc,
                hi_concept=hc)
        DBSession.add(models.Colexification(
            id='{0}__{1}'.format(lo_wid, hi_wid),
            name=c['clics_value'],
            language=data['Value'][lo_wid].valueset.language,
            edge=edge,
            lo_word=data['Value'][lo_wid],
            hi_word=data['Value'][hi_wid]))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    params = {p.id: p for p in DBSession.query(common.Parameter)}
    seen = set()
    for g in reader(args.data_file('graphs.csv'), dicts=True):
        nodes = g['nodes'].split('/')
        if len(nodes) < 2:
            continue
        ghash = (frozenset(nodes), g['type'])
        if ghash in seen:
            continue
        seen.add(ghash)
        graph = models.Graph(
            id=g['id'],
            name=g['id'].split('_', 1)[1] + ' [%s]' % g['type'],
            type=g['type'])
        for node in nodes:
            models.GraphConcept(graph=graph, concept=params[node])
        DBSession.add(graph)

    count = func.count(models.Doculect.pk).label('c')
    families = [
        r[0] for r in DBSession
        .query(models.Doculect.family_name, count)
        .group_by(models.Doculect.family_name)
        .order_by(desc(count))]
    families = dict(zip(families, qualitative_colors(len(families))))
    for l in DBSession.query(models.Doculect):
        l.color = families[l.family_name]


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
