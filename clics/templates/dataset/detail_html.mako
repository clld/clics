<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%block name="head">
    <link rel="stylesheet" href="${req.static_url('clics:static/our.css')}" type="text/css" media="screen">
    <script type="text/javascript" src="//d3js.org/d3.v3.min.js"></script>
    <script type="text/javascript" src="${req.static_url('clics:static/topojson.js')}"></script>
</%block>

<%def name="sidebar()">
    <%util:well title="Cite">
        Rzymski, Christoph and Tresoldi, Tiago et al. 2019.
        The Database of Cross-Linguistic Colexifications, reproducible analysis of cross- linguistic polysemies.
        <a href="https://doi.org/10.17613/5awv-6w15">DOI: 10.17613/5awv-6w15</a>
    </%util:well>
    <div id="map" style="visibility: hidden"></div>
    <div id="info" class="" style="visibility: hidden"></div>
</%def>

<h2>${ctx.description}</h2>

<p class="lead">
    <img src="${req.static_url('clics:static/clics.svg')}" width="100"
         style="float: left; margin-right: 10px; margin-bottom: 5px; margin-left: 5px;">
    ${req.dataset.name} is an online database of colexifications (polysemies or homophonies)
    in currently
    <a href="${request.route_url('languages')}">${count_langs} language varieties</a>
    of the world.
</p>
<p>
    The original Database of Cross-Linguistic Colexifications (CLICS), has
    established a computer-assisted framework for the interactive
    representation of cross-linguistic colexification patterns.
    It has proven to be a useful tool for various kinds of
    investigation into cross-linguistic semantic associations, ranging from
    studies on semantic change, patterns of conceptualization, and
    linguistic paleontology. But CLICS has also been criticized for obvious
    shortcomings. Building on standardization efforts reflected in
    the CLDF initiative and novel approaches for fast, efficient, and
    reliable data aggregation, CLICS² expanded the original CLICS database.
    CLICS³ - the third installment of CLICS - exploits the framework pioneered in CLICS²
    to more than double the amount of data aggregated in the database.
</p>

<div id="visualization" style="padding-top: 0; margin-top: 0px;">
    <div id="vis" style="padding-top: 0;"></div>
</div>

<%block name="javascript">
    $(function() {
    CLICS.Graph('${req.resource_url(graph)}.json', '${req.static_url("clics:static/world-110m.json")}', {"height": 250});
    });
</%block>
