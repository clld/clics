from sqlalchemy.orm import joinedload
from pyramid.config import Configurator

from clld.interfaces import IMapMarker, IValue, IValueSet, ILanguage, ICtxFactoryQuery
from clld.web.icon import MapMarker
from clldutils import svg
from clld.web.app import CtxFactoryQuery
from clld.db.models import common
from clld.web.adapters.rdf import RdfIndex
from clld.lib.rdf import convert, FORMATS

# we must make sure custom models are known at database initialization!
from clics import models
from clics.interfaces import IEdge, IGraph


_ = lambda s: s
_('Parameter')
_('Parameters')
_('Language')
_('Languages')
_('Contribution')
_('Contributions')
_('Edge')
_('Edges')


class ClicsCtxFactoryQuery(CtxFactoryQuery):
    def refined_query(self, query, model, req):
        """To be overridden.

        Derived classes may override this method to add model-specific query
        refinements of their own.
        """
        if model == common.Contribution:
            query = query.options(
                joinedload(models.ClicsDataset.doculects),
                joinedload(common.Contribution.data),
            )
        return query


class ClicsMapMarker(MapMarker):
    def __call__(self, ctx, req):
        color = None
        if IValue.providedBy(ctx):
            color = ctx.valueset.language.color
        if IValueSet.providedBy(ctx):
            color = ctx.language.color
        if ILanguage.providedBy(ctx):
            color = ctx.color

        if color:
            return svg.data_url(svg.icon('c' + color[1:]))

        return super(ClicsMapMarker, self).__call__(ctx, req)


class ClicsRdfIndex(RdfIndex):
    def render(self, ctx, req):
        # For performance reasons we have to disable the rdf index.
        return convert(super(RdfIndex, self).render([], req), 'xml', self.rdflibname)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.register_resource('graph', models.Graph, IGraph, with_index=True)
    config.register_resource('edge', models.Edge, IEdge, with_index=True)
    config.registry.registerUtility(ClicsMapMarker(), IMapMarker)
    rdf_xml = FORMATS['xml']

    config.registry.registerUtility(ClicsCtxFactoryQuery(), ICtxFactoryQuery)
    config.register_adapters([
        (
            IValue,
            ClicsRdfIndex,
            rdf_xml.mimetype,
            rdf_xml.extension,
            'index_rdf.mako',
            {'rdflibname': rdf_xml.name})])
    return config.make_wsgi_app()
