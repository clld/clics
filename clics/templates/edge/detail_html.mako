<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "edges" %>
<%block name="title">${_('Edge')} ${ctx.name}</%block>

<%def name="sidebar()">
    <%util:well title="Graphs">
        <ul class="unstyled">
            % for g in ctx.graphs:
                <li>${h.link(request, g)}</li>
            % endfor
        </ul>
    </%util:well>
</%def>

<h2>Colexifications for ${ctx.name}</h2>

<%util:table items="${ctx.colexifications}" args="item" class_="table-striped">
    <%def name="head()">
        <th>Language</th>
        <th>Family</th>
        <th>Form for ${h.link(request, ctx.lo_concept)}</th>
        <th>Form for ${h.link(request, ctx.hi_concept)}</th>
    </%def>
    <td>${h.link(request, item.language)}</td>
    <td style="background-color: ${item.language.color}; color: ${item.language.fontcolor}">${item.language.family_name}</td>
    <td>${h.link(request, item.lo_word)}</td>
    <td>${h.link(request, item.hi_word)}</td>
</%util:table>


