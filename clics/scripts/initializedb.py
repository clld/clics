import re
import collections
import itertools
from collections import Counter

from tqdm import tqdm
import transaction
from sqlalchemy.orm import joinedload
from clld.db.meta import DBSession
from clld.db.models import common
from clld.cliutil import Data

from clldutils.color import qualitative_colors
from clldutils.misc import slug
from clldutils.jsonlib import load
from pycldf import Dataset

from pyclics.zenodo import iter_records
from pyclics.util import iter_subgraphs

import clics
from clics import models

import clld.__main__

CL_PATTERN = re.compile(r'concepticon\.clld\.org/contributions/(?P<id>.+)')


def ids(wid1, wid2, wid2pid):
    p1, p2 = wid2pid[wid1], wid2pid[wid2]
    assert p1 != p2
    if int(p1.id) > int(p2.id):
        p1, p2 = p2, p1
        wid1, wid2 = wid2, wid1
    return wid1, wid2, p1, p2


def _iter_conceptlist_ids(md_path):
    md = load(md_path)
    for cl in md.get('dc:format', []):
        m = CL_PATTERN.search(cl)
        if m:
            yield m.group('id')


def main(args):
    data = Data()
    wl = Dataset.from_metadata(args.cldf.directory / 'Wordlist-metadata.json')
    ds = args.cldf
    # Load concepticon data:
    concepticon = Dataset.from_metadata('/home/robert/projects/concepticon/concepticon-cldf/cldf/Wordlist-metadata.json')

    dataset = common.Dataset(
        id=clics.__name__,
        name="CLICS⁴",
        description="Database of Cross-Linguistic Colexifications",
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        license="https://creativecommons.org/licenses/by/4.0/",
        domain='clics.clld.org',
        contact='clics@eva.mpg.de',
        jsondata={
            'doi': '10.5281/zenodo.16900180',
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})

    for i, (id_, name) in enumerate([
        ('tjuka', 'Annika Tjuka'),
        ('forkel', 'Robert Forkel'),
        ('rzymski', 'Christoph Rzymski'),
        ('list', 'Johann-Mattis List'),
    ]):
        ed = data.add(common.Contributor, id_, id=id_, name=name)
        common.Editor(dataset=dataset, contributor=ed, ord=i + 1)
    DBSession.add(dataset)

    for contrib in ds.objects('ContributionTable'):
        md = ds.directory.parent / 'raw' / contrib.id / 'cldf' / 'cldf-metadata.json'
        assert md.exists()
        data.add(
            models.ClicsDataset,
            contrib.id,
            id=contrib.id,
            name=contrib.cldf.description,
            doi=contrib.data['DOI'],
            source_citation=contrib.data['Citation'],
            jsondata={'conceptlists': list(_iter_conceptlist_ids(md))},
        )

    concept_definitions = {}
    for c in concepticon.objects('ParameterTable'):
        concept_definitions[c.id] = c.cldf.description
        data.add(
            models.Concept,
            c.id,
            id=c.id,
            name=c.cldf.name,
            description=c.cldf.description,
            category=c.data['Ontological_Category'],
            semanticfield=c.data['Semantic_Field'])

    DBSession.flush()
    datasets = {k: obj.pk for k, obj in data['ClicsDataset'].items()}
    concepts = {k: obj.pk for k, obj in data['Concept'].items()}
    concept_names = {k: obj.name for k, obj in data['Concept'].items()}
    concepts_by_name = {obj.name: obj.pk for k, obj in data['Concept'].items()}
    conceptid_by_name = {obj.name: obj.id for k, obj in data['Concept'].items()}
    transaction.commit()

    forms_by_variety = collections.defaultdict(list)
    for row in wl.iter_rows('FormTable'):
        forms_by_variety[row['Language_ID']].append(row)
    pid2cid = {}
    for row in wl.iter_rows('ParameterTable'):
        pid2cid[row['ID']] = row['Concepticon_ID']

    wid2cid = {}
    varieties = args.cldf.objects('LanguageTable')
    families = Counter(v.data['Family_Name'] for v in varieties)
    families = dict(zip([r[0] for r in families.most_common()], qualitative_colors(len(families))))
    for variety in tqdm(varieties, total=len(varieties)):
        #ID,Name,Macroarea,Latitude,Longitude,Glottocode,ISO639P3code,Glottolog_Name,Family,Concept_Count,Form_Count,
        # Contribution_ID,Family_Name

        transaction.begin()
        data = Data()
        #dspk = datasets[variety.source]
        v = models.Doculect(
            id=variety.id,
            name=variety.cldf.name,
            color=families[variety.data['Family_Name']],
            family_name=variety.data['Family_Name'],
            glottocode=variety.cldf.glottocode,
            macroarea=variety.cldf.macroarea,
            latitude=variety.cldf.latitude,
            longitude=variety.cldf.longitude,
            contribution_pk=datasets[variety.cldf.contributionReference])

        for form in forms_by_variety[variety.id]:
            #OrderedDict({
            # 'ID': '1-world-1', 'Language_ID': '1', 'Parameter_ID': 'world',
            # 'Form': 'wereld', 'Segments': ['ʋ', 'eː', 'r', 'ə', 'l', 't'],
            # 'Comment': None, 'Source': ['wold'], 'Value': 'wereld', 'Local_ID': 'wold-Dutch-1-1-1',
            # 'Graphemes': None, 'Profile': None, 'Cognacy': None, 'Loan': None, 'ConceptInSource': None})
            key = (variety.id, pid2cid[form['Parameter_ID']])
            vs = data['ValueSet'].get(key)
            if not vs:
                vs = data.add(
                    common.ValueSet,
                    key,
                    id='{0}-{1}'.format(*key),
                    language=v,
                    contribution_pk=datasets[variety.cldf.contributionReference],
                    parameter_pk=concepts[pid2cid[form['Parameter_ID']]])
            value = models.Form(
                id=form['ID'],
                valueset=vs,
                name=form['Form'],
                source_form=form['Value'],
                source_gloss=form['ConceptInSource'] or concept_names[pid2cid[form['Parameter_ID']]],
            )
            wid2cid[value.id] = vs.parameter_pk

        DBSession.add(v)
        transaction.commit()

    c_by_pk, c_by_id, c_by_name = {}, {}, {}
    for c in DBSession.query(models.Concept):
        c_by_id[c.id] = c
        c_by_pk[c.pk] = c
        c_by_name[slug(c.name)] = c
    for k in wid2cid:
        wid2cid[k] = c_by_pk[wid2cid[k]]
    values = {v.id: v.pk for v in DBSession.query(common.Value)}
    varieties = {v.id: v.pk for v in DBSession.query(models.Doculect)}

    data = Data()
    # args.cldf.iter_rows('ParameterTable')
    #ID,Name,Description,ColumnSpec,Source_Concept,Target_Concept,Form_Count,Variety_Count,Language_Count,Family_Count,Variety_Weight,Language_Weight,Family_Weight,Forms,Varieties,Languages,Families
    #OrderedDict({'ID': '1', 'Name': 'WORLD/DONKEY', 'Description': 'Colexification of WORLD and DONKEY.',
    # 'ColumnSpec': None, 'Source_Concept': 'WORLD', 'Target_Concept': 'DONKEY',
    # 'Form_Count': 1, 'Variety_Count': 1, 'Language_Count': 1, 'Family_Count': 1,
    # 'Variety_Weight': 0.0, 'Language_Weight': 0.0, 'Family_Weight': 0.0,
    # 'Forms': ['clics4-10-world-2', '/', 'clics4-10-donkey-1'], 'Varieties': ['clics4-10'],
    # 'Languages': ['thai1261'], 'Families': ['taik1256']})

    #g = api.load_graph('network', threshold=3, edgefilter='families')
    #for nodeA, nodeB, data_ in tqdm(g.edges(data=True), desc='loading colexifications'):
    #    for word in data_['wofam'].split(';'):

    for row in args.cldf.iter_rows('ParameterTable'):
            #w1, w2, entry, lid, fam, ovalA, ovalB = word.split('/')
            #lo_wid, hi_wid, lo_c, hi_c = ids(w1, w2, wid2cid)
            eid = '{0}-{1}'.format(
                conceptid_by_name[row['Source_Concept']], conceptid_by_name[row['Target_Concept']])
            edge = data['Edge'].get(eid)
            if not edge:
                edge = data.add(
                    models.Edge,
                    eid,
                    id=eid,
                    name='"{0}" and "{1}"'.format(row['Source_Concept'], row['Target_Concept']),
                    lo_concept_pk=concepts_by_name[row['Source_Concept']],
                    hi_concept_pk=concepts_by_name[row['Target_Concept']])
            for wp in row['Forms']:
                lo_wid, _, hi_wid = wp.replace('clics4-', '').partition('/')
                lid = []
                for k, v in zip(lo_wid.split('-'), hi_wid.split('-')):
                    if k == v:
                        lid.append(k)
                    else:
                        break
                DBSession.add(models.Colexification(
                    id='{0}__{1}'.format(lo_wid, hi_wid),
                    name=wp,
                    language_pk=varieties['-'.join(lid)],  # the common prefix of lo_wid and hi_wid
                    edge=edge,
                    lo_word_pk=values[lo_wid],
                    hi_word_pk=values[hi_wid]))

    DBSession.flush()
    edges = set((e.lo_concept.id, e.hi_concept.id) for e in data['Edge'].values())

    def make_graph(id_, name, nodes, concept=None):
        nodeset = set(nodes)
        if len(nodeset) > 1:
            graph = models.Graph(
                id=id_,
                name=name,
                concept_pk=concept.pk if concept else None,
                count_concepts=len(nodeset),
                count_edges=sum(1 for e in edges if nodeset.issuperset(e)))
            for node in nodeset:
                models.GraphConcept(graph=graph, concept_pk=c_by_name[node].pk)
            DBSession.add(graph)

    for community, rows in itertools.groupby(
        sorted(args.cldf.iter_rows('concepts.csv'), key=lambda r: r['Community']),
        lambda r: r['Community'],
    ):
        rows = list(rows)
        # Community
        # Central_Concept
        make_graph(
            rows[0]['CentralConcept'],
            rows[0]['CentralConcept'],
            [r['ID'] for r in rows])

    return


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

    lang_counts = {
        r[0]: (r[1], r[2]) for r in DBSession.execute("""\
select
    vs.contribution_pk, count(distinct l.glottocode), count(distinct l.family_name)
from
    valueset as vs, doculect as l
where
    vs.language_pk = l.pk
group by
    vs.contribution_pk""")}
    concept_counts = {
        r[0]: r[1] for r in DBSession.execute(
        "select contribution_pk, count(distinct parameter_pk) from valueset group by contribution_pk")}
    for ds in DBSession.query(models.ClicsDataset).options(joinedload(models.ClicsDataset.doculects)):
        ds.count_varieties = len(ds.doculects)
        ds.count_concepts = concept_counts[ds.pk]
        ds.count_glottocodes, ds.count_families = lang_counts[ds.pk]
