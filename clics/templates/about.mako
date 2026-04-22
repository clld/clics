<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<h2>About CLICS</h2>

<p>
    This web site serves as a browseable version of the data described in the paper
</p>

<blockquote>
    Annika Tjuka, Robert Forkel, Christoph Rzymski, and Johann-Mattis List. 2025. Advancing the Database of Cross-Linguistic Colexifications with New Workflows and Data. In Proceedings of the 16th International Conference on Computational Semantics, pages 1–15, Düsseldorf, Germany. Association for Computational Linguistics.
    <br/>
    ${h.external_link('https://aclanthology.org/2025.iwcs-main.1/')}
</blockquote>

<p>
    Learn more about CLICS at
    ${h.external_link('https://github.com/clics/clics', label='github.com/clics/clics')}
</p>
