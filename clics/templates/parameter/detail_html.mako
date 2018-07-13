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
        <h4>Colexified concepts:</h4>
        <table class="table table-condensed table-nonfluid">
            <thead>
                <tr>
                    <th style="text-align: right">Links</th>
                    <th>Concept</th>
                </tr>
            </thead>
            <tbody>
                % for e, n in ctx.edges:
                    <tr>
                        <td class="right">${len(e.colexifications)}</td>
                        <td>${h.link(request, e, label=n.name)}</td>
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</%def>
