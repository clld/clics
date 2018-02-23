<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "graphs" %>
<%block name="title">${_('Graph')} ${ctx.name}</%block>

<%block name="head">
    <link rel="stylesheet" href="${req.static_url('clics:static/our.css')}" type="text/css" media="screen">
    <script type="text/javascript" src="//d3js.org/d3.v3.min.js"></script>
    <script type="text/javascript" src="${req.static_url('clics:static/topojson.js')}"></script>
    ##<script src="${req.static_url('clics:static/visualize.js')}" type="text/javascript"></script>
</%block>

<%def name="sidebar()">
    <div class="well well-small">
        <div id="map"></div>
    </div>
    <div id="info" class=""></div>
</%def>


<h2>${_('Graph')} ${ctx.name}</h2>

##<ul>
##    % for c in ctx.concepts:
##        <li>
##            ${h.link(req, c)}
##        </li>
##    % endfor
##</ul>

##${request.get_datatable('values', h.models.Value, language=ctx).render()}

<div id="visualization">
    <div id="vis"></div>
</div>

<%block name="javascript">
    $(function() {
        CLICS.Graph('${req.resource_url(ctx)}.json', '${req.static_url("clics:static/world-110m.json")}');
    });
</%block>
