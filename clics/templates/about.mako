<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<h2>About CLICS</h2>

<p>
    This web site serves as a browseable version of the data described in the paper
</p>

<blockquote>
    Tjuka, Annika; Forkel, Robert; Rzymski, Christoph; and List, Johann-Mattis (forthcoming): Advancing the Database of Cross-Linguistic Colexifications with New Workflows and Data. Proceedings of the 16th International Conference on Computational Semantics (IWCS). Düsseldorf: Association for Computational Linguistics. 1-15. Preprint: https://doi.org/10.48550/arXiv.2503.11377
</blockquote>

<p>
    Learn more about CLICS at
    ${h.external_link('https://github.com/clics/clics', label='github.com/clics/clics')}
</p>
