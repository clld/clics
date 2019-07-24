from sqlalchemy.orm import joinedload
from pyramid.config import Configurator

from clld.interfaces import IMapMarker, IValue, IValueSet, ILanguage, ICtxFactoryQuery
from clld.web.icon import MapMarker
from clldutils import svg
from clld.web.app import CtxFactoryQuery
from clld.db.models import common

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





def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.register_resource('graph', models.Graph, IGraph, with_index=True)
    config.register_resource('edge', models.Edge, IEdge, with_index=True)
    config.registry.registerUtility(ClicsMapMarker(), IMapMarker)
    config.registry.registerUtility(ClicsCtxFactoryQuery(), ICtxFactoryQuery)
    return config.make_wsgi_app()
