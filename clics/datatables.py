from sqlalchemy.orm import joinedload
from clld.web.datatables.base import LinkCol, LinkToMapCol, Col
from clld.web.datatables.language import Languages
from clld.web.datatables.contribution import Contributions
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import map_marker_img, external_link, linked_references
from clld.db.models.common import Contribution

from clics.models import Doculect, ClicsDataset


class FamilyCol(Col):
    def format(self, item):
        return HTML.div(map_marker_img(self.dt.req, item), item.family_name)


class Doculects(Languages):
    def base_query(self, query):
        return query.join(Contribution).options(joinedload(Doculect.contribution))

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            LinkCol(self, 'contribution', get_object=lambda i: i.contribution, model_col=Contribution.name),
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


class Datasets(Contributions):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self, 'author', model_col=ClicsDataset.author),
            RefsCol(self, 'source'),
            ProviderCol(self, 'provider'),
        ]


def includeme(config):
    config.register_datatable('contributions', Datasets)
    config.register_datatable('languages', Doculects)
