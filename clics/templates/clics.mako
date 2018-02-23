<%inherit file="app.mako"/>

##
## define app-level blocks:
##
<%block name="brand">
    <a href="${request.resource_url(request.dataset)}" class="brand">
        <img src="${request.static_url('clics:static/favicon.png')}" height="20" width="20" style="margin-top: -5px; margin-left: -20px;"/>
        ${request.dataset.name}
    </a>
</%block>

${next.body()}
