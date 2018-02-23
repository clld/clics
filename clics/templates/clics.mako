<%inherit file="app.mako"/>

##
## define app-level blocks:
##
<%block name="brand">
    <a href="${request.resource_url(request.dataset)}" class="brand">${request.dataset.name}</a>
</%block>

${next.body()}
