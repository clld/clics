<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<h2>About CLICS</h2>

<p>
    This web site serves as a browseable of the data described in the paper
</p>

<blockquote>
    Rzymski, Tresoldi, et al. (2019):
    The Database of Cross-Linguistic Colexifications, reproducible analysis of cross- linguistic polysemies.
    <a href="https://doi.org/10.1038/s41597-019-0341-x">DOI: 10.1038/s41597-019-0341-x</a>
</blockquote>

<p>
    Learn more about CLICS at
    ${h.external_link('https://github.com/clics/clics', label='github.com/clics/clics')}
</p>
