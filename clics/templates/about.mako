<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<h2>About CLICS</h2>

<p>
    This web site serves as a browseable of the data and methods described in the paper
</p>

<blockquote>
    J.-M. List et al. (forthcoming): CLICS 2:
    An improved database of cross-linguistic colexifications assembling lexical data with the help of cross-linguistic data formats.
    Linguistic Typology.
    <a href="https://doi.org/10.1515/lingty-2018-0010">DOI: 10.1515/lingty-2018-0010</a>
</blockquote>

<p>
    Page 11 of the paper lists summary statistics about the source datasets which are aggregated for
    CLICS 2. This table is reproduced dynamically below - and will thus be updated with new releases
    of the data.
</p>

<div style="margin-bottom: 1em">
<table class="table table-condensed table-nonfluid table-striped">
    <caption><strong>Table 1:</strong> Overview of datasets (page 11).</caption>
    <thead>
    <tr>
        <th>ID</th>
        <th>Dataset</th>
        <th>Concept list</th>
        <th>Glosses</th>
        <th>Concepticon</th>
        <th>Varieties</th>
        <th>Glottocodes</th>
        <th>Families</th>
    </tr>
    </thead>
    <tbody>
        % for ds, g in datasets:
            <tr>
                <td>${h.link(request, ds, label=ds.id.replace('lexibank-', ''))}</td>
                <td>${h.link(request, ds)}</td>
                <td>${ds.conceptlist_link(request)|n}</td>
                <td class="right">${g}</td>
                <td class="right">${ds.count_concepts}</td>
                <td class="right">${ds.count_varieties}</td>
                <td class="right">${ds.count_glottocodes}</td>
                <td class="right">${ds.count_families}</td>
            </tr>
        % endfor
    </tbody>
</table>
</div>

<p>
    Page 12 of the paper lists the top-ten most often colexified pairs of concepts. Again, we reproduce
    this table dynamically below, with concept labels linking to the details page of the respective
    concept and counts linking to the details page on the respective colexifications.
</p>

<div style="margin-bottom: 1em">
<table class="table table-condensed table-nonfluid table-striped">
    <caption><strong>Table 2:</strong> The ten most frequently recurring colexifications encountered in our database (page 12).</caption>
    <thead>
        <tr>
            <th>ID A</th>
            <th>Concept A</th>
            <th>ID B</th>
            <th>Concept B</th>
            <th>Families</th>
            <th>Languages</th>
            <th>Words</th>
        </tr>
    </thead>
    <tbody>
    % for ca, cb, fc, lc, wc in top_ten:
        <tr>
            <td>${h.link(request, ca, label=ca.id)}</td>
            <td>${h.link(request, ca)}</td>
            <td>${h.link(request, cb, label=cb.id)}</td>
            <td>${h.link(request, cb)}</td>
            <td class="right"><a href="${request.route_url('edge', id='{0}-{1}'.format(cb.id, ca.id))}">${fc}</a></td>
            <td class="right"><a href="${request.route_url('edge', id='{0}-{1}'.format(cb.id, ca.id))}">${lc}</a></td>
            <td class="right"><a href="${request.route_url('edge', id='{0}-{1}'.format(cb.id, ca.id))}">${wc}</a></td>
        </tr>
    % endfor
    </tbody>
</table>
</div>

<p>
    Page 16 shows a figure displaying the biggest cluster computed with the infomap algorithm in the
    network of all colexifications. This cluster can be inspected on this site as well at
    ${h.link(request, say)}
</p>

<p>
    Page 18 shows a figure displaying the subgraph of the
    network of all colexifications centered at <b>WHEEL</b>.
    This subgraph can be inspected on this site as well at
    ${h.link(request, wheel)}
</p>

## page 16: cluster SAY: http://localhost:6543/graphs/infomap_2_SPEAK

## page 18: subgraph WHEEL: http://localhost:6543/graphs/subgraph_710
