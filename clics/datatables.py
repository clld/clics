from clld.db.models.common import Contribution, Parameter
from clld.db.util import get_distinct_values
from clld.web.datatables.base import LinkCol, LinkToMapCol, Col, DataTable, \
    DetailsRowLinkCol
from clld.web.datatables.contribution import Contributions
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.util import concepticon
from clld.web.util.helpers import map_marker_img, external_link, \
    linked_references, link
from clld.web.util.htmllib import HTML
from sqlalchemy.orm import joinedload

from clics.models import Doculect, ClicsDataset, Graph, Concept, Form


class FamilyCol(Col):
    def format(self, item):
        return HTML.div(map_marker_img(self.dt.req, item), item.family_name)


class Doculects(Languages):
    def base_query(self, query):
        return query.join(Contribution).options(joinedload(Doculect.contribution))

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self, 'concepts', model_col=Doculect.count_concepts, sTitle='# concepts', input_size='mini'),
            LinkCol(
                self,
                'contribution',
                get_object=lambda i: i.contribution,
                choices=get_distinct_values(Contribution.name),
                model_col=Contribution.name),
            FamilyCol(self, 'family_name', model_col=Doculect.family_name, sTitle='Family'),
            LinkToMapCol(self, 'm'),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
        ]


class ProviderCol(Col):
    __kw__ = dict(bSortable=False, bSearchable=False)

    def format(self, item):
        if item.provider_url:
            return external_link(item.provider_url, label=item.provider)
        if item.provider:
            return item.provider
        return ''


class RefsCol(Col):

    """Column listing linked sources."""

    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return linked_references(self.dt.req, item)


class DoiCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return item.doi_badge()


class ConceptListCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return item.conceptlist_link(self.dt.req)


class Datasets(Contributions):
    def col_defs(self):
        return [
            DoiCol(self, 'DOI'),
            LinkCol(self, 'name'),
            Col(self, 'count_varieties', model_col=ClicsDataset.count_varieties, sTitle='# varieties', input_size='mini'),
            Col(self, 'count_concepts', model_col=ClicsDataset.count_concepts, sTitle='# concepts', input_size='mini'),
            ConceptListCol(self, 'concept_list', sTitle='Concept list'),
            Col(self, 'source_citation', model_col=ClicsDataset.source_citation),
        ]


class Graphs(DataTable):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self, 'type', choices=get_distinct_values(Graph.type)),
            Col(self, 'count_concepts', sTitle='# nodes', input_size='mini'),
            Col(self, 'count_edges', sTitle='# edges', input_size='mini'),
        ]

    def get_options(self):
        opts = super(Graphs, self).get_options()
        opts['aaSorting'] = [[2, 'desc'], [3, 'desc']]
        return opts


class ClusterCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        g = item.cluster
        if g:
            return link(self.dt.req, g)


class SubgraphCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        g = item.subgraph
        if g:
            return link(self.dt.req, g)


class ConcepticonCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return concepticon.link(self.dt.req, item.id)


class Concepts(Parameters):
    def col_defs(self):
        return [
            DetailsRowLinkCol(self, '#'),
            LinkCol(self, 'name'),
            ConcepticonCol(self, '#', sTitle=''),
            Col(self, 'count_varieties', model_col=Concept.count_varieties, sTitle='# varieties'),
            Col(self, 'count_colexifications', model_col=Concept.count_colexifications, sTitle='# colexifications'),
            ClusterCol(self, 'cluster'),
            SubgraphCol(self, 'subgraph'),
        ]


class Forms(Values):
    def col_defs(self):
        res = [Col(self, 'name', sTitle='CLICS Form')]
        if self.language:
            res.append(LinkCol(self,
                'parameter',
                sTitle='Concept',
                model_col=Parameter.name,
                get_object=lambda i: i.valueset.parameter)
            )
        return res + [
            Col(self, 'source_form', sTitle='Form in source', model_col=Form.source_form),
            Col(self, 'source_gloss', sTitle='Gloss in source', model_col=Form.source_gloss),
        ]


def includeme(config):
    config.register_datatable('contributions', Datasets)
    config.register_datatable('languages', Doculects)
    config.register_datatable('values', Forms)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('graphs', Graphs)
