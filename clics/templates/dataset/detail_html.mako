<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <%util:well title="Cite">
        ${h.newline2br(h.text_citation(request, ctx))|n}
        ${h.cite_button(request, ctx)}
    </%util:well>
</%def>

<h2>${ctx.description}</h2>

<p class="lead">
    CLICS is an online database of synchronic lexical associations ("colexifications")
    in currently
    <a href="${request.route_url('languages')}">${count_langs} language varieties</a>
    of the world. Large databases offering lexical
    information on the world's languages are already readily available for research in
    different online sources. However, the information on tendencies of meaning
    associations they enshrine is not easily extractable from these sources themselves.
    This is why CLICS was created. It is designed to serve as a data source for work in
    lexical typology, diachronic semantics, and research in cognitive science that focuses
    on natural language semantics from the viewpoint of cross-linguistic diversity.
    Furthermore, CLICS can be used as a helpful tool to assess the plausibility of
    semantic connections between possible cognates in the establishment of genetic
    relations between languages.
</p>
