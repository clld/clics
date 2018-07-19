<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
    <%util:well title="Cite as">
    <div>
        ${ctx.doi_badge()|n}
    </div>
    </%util:well>
    <%util:well title="Source dataset">
        <blockquote>
            ${ctx.source_citation}
        </blockquote>
        ##<ul class="unstyled">
        ##    % for ref in ctx.references:
        ##        <li>${h.link(request, ref.source)}</li>
        ##    % endfor
        ##</ul>
    </%util:well>
        % if 'cl_url' in ctx.jsondata:
            <%util:well title="Concept list">
                <p>
                    The concept list for this dataset is available at Concepticon as
                    <a href="${ctx.jsondata['cl_url']}">${ctx.jsondata['cl_url'].split('/')[-1]}</a>
                </p>
            </%util:well>
        % endif
</%def>

<h2>${_('Contribution')} ${ctx.name}</h2>


<%util:table items="${ctx.doculects}" args="item" class_="table-striped">
    <%def name="head()">
        <th>Variety</th>
        <th>Family</th>
        <th># Concepts</th>
    </%def>
    <td>${h.link(request, item)}</td>
    <td style="background-color: ${item.color}; color: ${item.fontcolor}">${item.family_name}</td>
    <td class="right">${item.count_concepts}</td>
</%util:table>
