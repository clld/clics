<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "graphs" %>
<%block name="title">${_('Graphs')}</%block>

<h2>${_('Graphs')}</h2>

${ctx.render()}
