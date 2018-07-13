<div>
<h5>Definition:</h5>
<p>
    ${ctx.description}
</p>

% if ctx.edges:
    <h5>Colexifications:</h5>
    <table class="table table-condensed table-nonfluid">
        <thead>
        <tr>
            <th>Concept</th>
            <th style="text-align: right">Links</th>
        </tr>
        </thead>
        <tbody>
            % for e, n in ctx.edges:
                <tr>
                    <td>${h.link(request, e, label=n.name)}</td>
                    <td class="right">${len(e.colexifications)}</td>
                </tr>
            % endfor
        </tbody>
    </table>
% endif
</div>