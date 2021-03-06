<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<h2>CLICS Data</h2>

<p>
    The data served by the CLICS web application was aggregated from
    ${h.external_link('https://github.com/clics/clics3/blob/master/datasets.md', label='30 datasets')}
    using the
    <span style="font-family: monospace">${h.external_link('https://pypi.org/project/pyclics', label='pyclics')}</span>
    Python package, following the procedure described in the
    <span style="font-family: monospace">${h.external_link('https://github.com/clics/clics3/blob/master/README.md', label='README')}</span>.
</p>
<p>
    The datasets as well as the aggregation software are archived on
    ${h.external_link('https://zenodo.org', label='Zenodo')} for longterm availability and should
    be downloaded
    ${h.external_link('https://zenodo.org/communities/clics/', label='from there')}.
</p>
<p>
    As long as the
    ${h.external_link('https://pypi.org', label='Python Package Index (PyPI)')} and
    ${h.external_link('https://github.com', label='GitHub')} are around, though,
    installing the software from PyPI and retrieving the datasets from GitHub - as described
    ${h.external_link('https://github.com/clics/clics3', label='here')}
    may be more convenient.
</p>