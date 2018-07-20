<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<h2>CLICS Data</h2>

<p>
    The data served by the CLICS web application was aggregated from
    ${h.external_link('https://zenodo.org/communities/clics/search?page=1&size=20&keywords=clics2', label='15 datasets')}
    using the
    <span style="font-family: monospace">${h.external_link('https://pypi.org/project/pyclics', label='pyclics')}</span>
    Python package, following the procedure described in the package's
    <span style="font-family: monospace">${h.external_link('https://github.com/clics/clics2/blob/master/README.md', label='README')}</span>.
</p>
<p>
    The datasets as well as the aggregation software are archived on
    ${h.external_link('https://zenodo.org', label='ZENODO')} for longterm availability and should
    be downloaded
    ${h.external_link('https://zenodo.org/communities/clics/search?page=1&size=20&keywords=clics2', label='from there')}.
</p>
<p>
    As long as the
    ${h.external_link('https://pypi.org', label='Python Package Index (PyPI)')}} and
    ${h.external_link('https://github.com', label='GitHub')} are around, though,
    installing the software from PiPI and retrieving the datasets from GitHub - as described
    ${h.external_link('https://github.com/clics/clics2/blob/master/README.md', label='here')}
    may be more convenient.
</p>