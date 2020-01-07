<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "edges" %>
<%block name="title">${_('Edge')} ${ctx.name}</%block>

<%def name="sidebar()">
    <%util:well title="Graphs">
        <p>
            This edge appears in cluster
        </p>
        <ul class="unstyled">
            % for g in ctx.graphs:
                % if g.type != 'subgraph':
                    <li>${h.link(request, g)}</li>
                % endif
            % endfor
        </ul>
        <p>and subgraphs</p>
        <ul>
            % for g in ctx.graphs:
                % if g.type == 'subgraph':
                    <li>${h.link(request, g)}</li>
                % endif
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
        <th>Gloss for ${h.link(request, ctx.lo_concept)}</th>
        <th>Form for ${h.link(request, ctx.hi_concept)}</th>
        <th>Gloss for ${h.link(request, ctx.hi_concept)}</th>
    </%def>
    <td>${h.link(request, item.language)}</td>
    <td style="background-color: ${item.language.color}; color: ${item.language.fontcolor}">${item.language.family_name}</td>
    <td><i>${item.lo_word.source_form}</i></td>
    <td>${item.lo_word.source_gloss}</td>
    <td><i>${item.hi_word.source_form}</i></td>
    <td>${item.hi_word.source_gloss}</td>
</%util:table>


