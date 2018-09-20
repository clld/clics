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
    <img src="${req.static_url('clics:static/clics.svg')}" width="100" style="float: left; margin-right: 10px; margin-bottom: 5px; margin-left: 5px;">
    ${req.dataset.name} is an online database of colexifications (polysemiesor homophonies)
    in currently
    <a href="${request.route_url('languages')}">${count_langs} language varieties</a>
    of the world.
</p>
<p>
The original Database of Cross-Linguistic Colexifications (CLICS), has
established a computer-assisted framework for the interactive
representation of cross-linguistic colexification patterns. In its
current form, it has proven to be a useful tool for various kinds of
investigation into cross-linguistic semantic associations, ranging from
studies on semantic change, patterns of conceptualization, and
linguistic paleontology. But CLICS has also been criticized for obvious
shortcomings. Building on recent standardization efforts reflected in
the CLDF initiative and novel approaches for fast, efficient, and
reliable data aggregation, ${req.dataset.name} is a new database of cross-linguistic
colexifications, which supersedes the original CLICS database in terms
of coverage and offers a much more principled procedure for the
creation, curation and aggregation of datasets.
</p>
