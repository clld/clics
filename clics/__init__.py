from pyramid.config import Configurator

# we must make sure custom models are known at database initialization!
from clics import models
from clics.interfaces import IEdge, IGraph


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.register_resource('graph', models.Graph, IGraph, with_index=True)
    config.register_resource('edge', models.Edge, IEdge, with_index=True)
    return config.make_wsgi_app()
