<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

<h2>${_('Language')} ${ctx.name}</h2>

${request.get_datatable('values', h.models.Value, language=ctx).render()}

<%def name="sidebar()">
    <%util:well>
        <h4>Dataset</h4>
        <p>
            ${h.link(request, ctx.contribution)}<br/>
            ${ctx.contribution.doi_badge()|n}
        </p>
        <blockquote>
            ${ctx.contribution.source_citation}
        </blockquote>
    </%util:well>

    ${util.language_meta()}
</%def>
