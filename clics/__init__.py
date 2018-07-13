from pyramid.config import Configurator

from clld.interfaces import IMapMarker, IValue, IValueSet, ILanguage
from clld.web.icon import MapMarker
from clld.lib import svg
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
    return config.make_wsgi_app()
