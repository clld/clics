<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>

<h2>${_('Parameter')} ${ctx.name}</h2>

% if ctx.description:
<div class="alert alert-info">${ctx.description}</div>
% endif

% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}

<%def name="sidebar()">
    <div class="well well-small">
        <h5>Colexifications:</h5>
        <table class="table table-condensed">
            <thead>
                <tr>
                    <th>Concept</th>
                    <th style="text-align: right">Links</th>
                </tr>
            </thead>
            <tbody>
                % for e, n in ctx.edges:
                    <tr>
                        <td>${h.link(request, e, label=n.name)}</td>
                        <td class="right">${len(e.colexifications)}</td>
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</%def>
