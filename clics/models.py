from zope.interface import implementer
from sqlalchemy import (
    Column,
    Unicode,
    Integer,
    ForeignKey,
    UniqueConstraint,
    or_,
    and_,
)
from sqlalchemy.orm import relationship, joinedload_all, aliased, joinedload, backref

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin, PolymorphicBaseMixin, DBSession
from clld.db.models.common import Language, IdNameDescriptionMixin, Parameter, Value, Contribution
from clld.lib.color import is_bright
from clld.web.util.htmllib import HTML

from clics.interfaces import IEdge, IGraph


@implementer(interfaces.IValue)
class Form(CustomModelMixin, Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    source_form = Column(Unicode)
    source_gloss = Column(Unicode)


@implementer(interfaces.IContribution)
class ClicsDataset(CustomModelMixin, Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    doi = Column(Unicode)
    source_citation = Column(Unicode)
    count_varieties = Column(Integer)
    count_concepts = Column(Integer)
    count_glottocodes = Column(Integer)
    count_families = Column(Integer)

    def conceptlist_link(self, req):
        if 'cl_url' in self.jsondata:
            return HTML.a(
                HTML.img(
                    src=req.static_url('clics:static/concepticon.png'),
                    width='20'),
                title='concept list at Concepticon',
                href=self.jsondata['cl_url'])
        return ''

    def doi_badge(self):
        if self.doi:
            return HTML.a(
                HTML.img(
                    src="https://zenodo.org/badge/DOI/{0}.svg".format(self.doi),
                    style="max-width: none !important;",
                    alt="DOI: {0}".format(self.doi)),
                href="https://doi.org/{0}".format(self.doi),
                title="DOI: {0}".format(self.doi))
        return ''


@implementer(interfaces.ILanguage)
class Doculect(CustomModelMixin, Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    family_name = Column(Unicode)
    family_glottocode = Column(Unicode)
    glottocode = Column(Unicode)
    macroarea = Column(Unicode)
    color = Column(Unicode)
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship(Contribution, backref='doculects')
    count_concepts = Column(Integer)

    @staticmethod
    def refine_factory_query(query):
        return query.options(joinedload(Doculect.contribution))

    @property
    def fontcolor(self):
        return '#000' if is_bright(self.color) else '#eee'


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    category = Column(Unicode)
    semanticfield = Column(Unicode)
    count_varieties = Column(Integer)
    count_colexifications = Column(Integer)

    @staticmethod
    def refine_factory_query(query):
        return query.options(
            joinedload_all(Concept.lo_edges, Edge.colexifications),
            joinedload_all(Concept.hi_edges, Edge.colexifications),
        )

    @property
    def cluster(self):
        return DBSession.query(Graph).join(GraphConcept)\
        .filter(GraphConcept.concept_pk == self.pk)\
        .filter(Graph.type == 'cluster')\
        .first()

    @property
    def edges(self):
        return sorted(
            [(e, e.lo_concept) for e in self.lo_edges] +
            [(e, e.hi_concept) for e in self.hi_edges],
            key=lambda e: len(e[0].colexifications),
            reverse=True)

    @property
    def neighbors(self):
        return [x.lo_concept for x in self.lo_edges] + \
               [x.hi_concept for x in self.hi_edges]

    def iter_out_edges(self, graph):
        for e, n in self.edges:
            if n not in graph.concepts:
                yield e, n

    def __json__(self, req):
        return {
            "Category": self.category,
            "Gloss": self.name,
            "ID": self.id,
            "OutEdge": [],
        }


def join(iter):
    return ';'.join(list(iter))


@implementer(IEdge)
class Edge(Base, PolymorphicBaseMixin, IdNameDescriptionMixin):
    __table_args__ = (UniqueConstraint('lo_concept_pk', 'hi_concept_pk'),)

    lo_concept_pk = Column(Integer, ForeignKey('parameter.pk'))
    hi_concept_pk = Column(Integer, ForeignKey('parameter.pk'))

    lo_concept = relationship(
        Parameter, primaryjoin=lo_concept_pk == Parameter.pk, backref='hi_edges')
    hi_concept = relationship(
        Parameter, primaryjoin=hi_concept_pk == Parameter.pk, backref='lo_edges')

    @property
    def graphs(self):
        lc = aliased(GraphConcept)
        hc = aliased(GraphConcept)
        return DBSession.query(Graph).join(lc).join(hc) \
            .filter(self.lo_concept_pk == hc.concept_pk) \
            .filter(self.hi_concept_pk == lc.concept_pk) \
            .distinct()

    def adjacency(self, req, n):
        words, languages = [], set()
        for c in self.colexifications:
            words.append((c.id, c.name, c.language.id))
            languages.add(c.language)
        families = set(l.family_name for l in languages)
        return languages, {
            "eid": self.id,
            "FamilyWeight": len(families),
            "LanguageWeight": len(languages),
            "WordWeight": len(words),
            "id": n.id,
            "words": words,
        }


@implementer(IGraph)
class Graph(Base, PolymorphicBaseMixin, IdNameDescriptionMixin):
    type = Column(Unicode)  # subgraph, infomap, ...
    count_concepts = Column(Integer)
    count_edges = Column(Integer)
    concept_pk = Column(Integer, ForeignKey('concept.pk'))
    concept = relationship(Concept, backref=backref('subgraph', uselist=False))

    @staticmethod
    def refine_factory_query(query):
        return query.options(joinedload_all(Graph.concept_assocs, GraphConcept.concept))

    @property
    def concepts(self):
        return sorted([ca.concept for ca in self.concept_assocs], key=lambda c: int(c.id))

    @property
    def edges(self):
        cpks = [ca.concept_pk for ca in self.concept_assocs]
        return DBSession.query(Edge) \
            .filter(Edge.lo_concept_pk.in_(cpks)) \
            .filter(Edge.hi_concept_pk.in_(cpks))

    def edge(self, n1, n2):
        return DBSession.query(Edge) \
            .filter(or_(
            and_(Edge.lo_concept == n1, Edge.hi_concept == n2),
            and_(Edge.lo_concept == n2, Edge.hi_concept == n1))) \
            .options(joinedload_all(Edge.colexifications, Colexification.language)) \
            .one()

    def __json__(self, req):
        languages = set()
        adjacency = []
        nodes = []
        for n1 in self.concepts:
            row = []
            for n2 in n1.neighbors:
                if n2 in self.concepts:
                    l, a = self.edge(n1, n2).adjacency(req, n2)
                    languages = languages.union(l)
                    row.append(a)
            adjacency.append(row)
            json = n1.__json__(req)
            for e, n in n1.iter_out_edges(self):
                json['OutEdge'].append([e.id, n.name])
            nodes.append(json)
        return {
            "adjacency": adjacency,
            "directed": False,
            "graph": [],
            "multigraph": False,
            "nodes": nodes,
            "languages": [
                {
                    "glottocode": l.glottocode,
                    "color": l.color,
                    "fontcolor": l.fontcolor,
                    "name": l.name,
                    "id": l.id,
                    "family": l.family_name,
                    "area": l.macroarea,
                    "lat": l.latitude,
                    "lon": l.longitude
                } for l in languages
            ]
        }


class GraphConcept(Base):
    __table_args__ = (UniqueConstraint('graph_pk', 'concept_pk'),)

    graph_pk = Column(Integer, ForeignKey('graph.pk'))
    graph = relationship(Graph, backref='concept_assocs')

    concept_pk = Column(Integer, ForeignKey('concept.pk'))
    concept = relationship(Concept, backref='graph_assocs')


class Colexification(Base, IdNameDescriptionMixin):
    __table_args__ = (UniqueConstraint('lo_word_pk', 'hi_word_pk'),)

    language_pk = Column(Integer, ForeignKey('language.pk'))
    edge_pk = Column(Integer, ForeignKey('edge.pk'))
    lo_word_pk = Column(Integer, ForeignKey('value.pk'))
    hi_word_pk = Column(Integer, ForeignKey('value.pk'))

    language = relationship(Language)
    edge = relationship(Edge, backref='colexifications')
    lo_word = relationship(Value, primaryjoin=lo_word_pk == Value.pk)
    hi_word = relationship(Value, primaryjoin=hi_word_pk == Value.pk)
