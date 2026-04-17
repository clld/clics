<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<h2>CLICS Data</h2>

<p>
    The data served by the CLICS web application was aggregated from
    ${h.external_link('https://github.com/clics/clics4/blob/main/cldf/contributions.csv', label='95 datasets')}
    following the procedure described in the
    <span style="font-family: monospace">${h.external_link('https://github.com/clics/clics4/blob/master/README.md', label='README')}</span>.
</p>
<p>
    The datasets as well as the aggregation software are archived on
    ${h.external_link('https://zenodo.org', label='Zenodo')} for longterm availability and should
    be downloaded
    ${h.external_link('https://zenodo.org/communities/clics/', label='from there')}.
</p>