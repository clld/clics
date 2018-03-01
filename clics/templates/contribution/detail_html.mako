<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
    <%util:well title="Source">
        <ul class="unstyled">
            % for ref in ctx.references:
                <li>${h.link(request, ref.source)}</li>
            % endfor
        </ul>
    </%util:well>
</%def>

<h2>${_('Contribution')} ${ctx.name}</h2>

<p>${ctx.description}</p>


<%util:table items="${ctx.doculects}" args="item" class_="table-striped">
    <%def name="head()">
        <th>Variety</th>
        <th>Family</th>
    </%def>
    <td>${h.link(request, item)}</td>
    <td style="background-color: ${item.color}; color: ${item.fontcolor}">${item.family_name}</td>
</%util:table>
