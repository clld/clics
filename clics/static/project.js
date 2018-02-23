CLICS = {
    "langByInfo": {}
};

CLICS.Graph = function (url, world_json) {
    var opacity = 100;
    var coords = [];
    var projection = d3.geo.equirectangular().center([65, 25]).translate([210, 53]).scale(48);
    var path = d3.geo.path().projection(projection);
    var g = d3.select("#map").append("svg:svg").attr("width", 300).attr("height", 200).append("g");
    var mapPoly = g.append('g').attr('class', 'mapPoly'); // for the map
    var allCircles = g.append('g').attr('class', 'allCircles'); // all locations
    var nodeCircles = g.append('g').attr('class', 'nodeCircles'); // for the

    displayMap();

    d3.json(url, function (data) {
        var i, j, node;
        var nodesById = {};
        var weights = [];
        var nodeByLink = {};
        var links = [];
        data.languages.forEach(function (a) {
            coords.push([a.lon, a.lat]);
            CLICS.langByInfo[a.id] = a;
        });
        allCircles.selectAll("circle")
            .data(coords)
            .enter()
            .append("circle")
            .attr("class", "alllocation")
            .attr("cx", function (d) {return projection([d[0], d[1]])[0];})
            .attr('cy', function (d) {return projection([d[0], d[1]])[1];})
            .attr("r", function (d) {return 3;})
            .style("stroke", "white")
            .style("stroke-width", 0.5)
            .style("fill", '#888');

        for (i = 0; i < data.nodes.length; i++) {
            nodesById[data.nodes[i].ID] = i;
        }
        console.log('nodesById', nodesById);
        // store all weights and nodes by links
        for (i = 0; i < data.adjacency.length; i++) {
            for (j = 0; j < data.adjacency[i].length; j++) {
                weights.push(data.adjacency[i][j].FamilyWeight);
                if (nodeByLink[i]) {
                    nodeByLink[i].push(nodesById[data.adjacency[i][j].id]);
                }
                else {
                    nodeByLink[i] = [nodesById[data.adjacency[i][j].id]];
                }
            }
        }
        console.log('nodeByLink', nodeByLink);

        // weight scale from 0...max(weights) to 0...1
        var scale = d3.scale.linear().domain([0, d3.max(weights)]).range([0, 1]);

        // longitudinal scale
        var longsScale = d3.scale.linear().domain([-180, 180]).range([0, 1]);

        // latitudinal scale
        var latsScale = d3.scale.linear().domain([-90, 90]).range([0, 1]);

        // l*a*b* scale
        var labScale = d3.scale.linear().domain([-1, 1]).range([-128, 127]);

        //
        var lscale = d3.scale.linear().domain([0, d3.max(weights)]).range([1, 100]);

        // store node and link information for the force directed graph
        var nodes = [];
        var labelAnchors = [];
        var labelAnchorLinks = [];

        for (i = 0; i < data.nodes.length; i++) {
            node = {
                label: data.nodes[i].Gloss,
                OutEdge: data.nodes[i].OutEdge
            };
            nodes.push(node);
            labelAnchors.push({node: node});
            labelAnchors.push({node: node});
        }
        console.log('nodes', nodes);
        // the actual nodes
        for (i = 0; i < data.adjacency.length; i++) {
            for (j = 0; j < data.adjacency[i].length; j++) {
                links.push({
                    source: nodesById[data.adjacency[i][j].id],
                    target: i,
                    eid: data.adjacency[i][j].eid,
                    weight: scale(data.adjacency[i][j].FamilyWeight),
                    words: data.adjacency[i][j].words,
                    edge_width: 0.25 * data.adjacency[i][j].FamilyWeight // addon JML
                });
            }
        }
        console.log('links', links);
        // the label nodes with weight 1 connected to the actual nodes
        for (i = 0; i < nodes.length; i++) {
            labelAnchorLinks.push({source: i * 2, target: i * 2 + 1, weight: 1});
        }
        // make force directed graph layout draggable
        var node_drag = d3.behavior.drag()
            .on("dragstart", dragstart)
            .on("drag", dragmove)
            .on("dragend", dragend);

        function dragstart(d, i) {
            force.stop() // stops the force auto positioning before you start dragging
        }

        function dragmove(d, i) {
            d.px += d3.event.dx;
            d.py += d3.event.dy;
            d.x += d3.event.dx;
            d.y += d3.event.dy;
            tick(); // this is the key to make it work together with updating both px,py,x,y on d !
        }

        function dragend(d, i) {
            d.fixed = true; // of course set the node to fixed so the force doesn't include the
            // node in its auto positioning stuff
            tick();
            force.resume();
        }

        // enable panning and zooming
        function redraw() {
            vis.attr("transform",
                "translate(" + d3.event.translate + ")"
                + " scale(" + d3.event.scale + ")");
        }

        // plot the graph on an SVG
        var w = 700, h = 600, pad = 0;

        var vis = d3.select("#vis")
            .append("svg:svg")
            .attr("width", '100%')
            .attr("height", 500)
            .on('click', function () {
                d3.select('#info').classed('hidden', true);
                d3.selectAll('.link').style('stroke', '#CCC');
            })
            .append('svg:g')
            .call(d3.behavior.zoom().on("zoom", redraw))
            .append('svg:g');

        // force layout for actual nodes
        var force = d3.layout.force()
            .size([w - pad, h - pad])
            .nodes(nodes)
            .links(links)
            .gravity(1)
            .linkDistance(50)
            .charge(-3000)
            .linkStrength(function (x) {
                return x.weight * 10
            });

        force.start();

        var force2 = d3.layout.force()
            .nodes(labelAnchors)
            .links(labelAnchorLinks)
            .gravity(0)
            .linkDistance(0)
            .linkStrength(8)
            .charge(-100)
            .size([w - pad, h - pad]);

        force2.start();

        var link = vis.selectAll("line.link")
            .data(links).enter()
            .append("svg:line")
            .attr("class", function (d, i) {
                var weight = parseInt(d.weight * 10);
                var weightOutput = [];
                for (i = 0; i <= weight; i++) {
                    weightOutput.push('weight_' + i);
                }

                return "link link_" + d.source.index
                    + "-" + d.target.index + ' link_'
                    + d.target.index + "-" + d.source.index
                    + " " + weightOutput.join(" ") + " " + weight;

            })
            .style("stroke", "#CCC")
            .style('stroke-width', function (d) {
                return d.edge_width;
            })
            .style('cursor', 'pointer')
            .on('mouseover', function (d, i) {
                var cid_form_lid, _i;
                d3.selectAll('.link').style('stroke', '#CCC').style('stroke-opacity', opacity / 100);
                d3.select(this).style('stroke', 'OliveDrab').style('stroke-opacity', 1);
                d3.select("#info")
                    .html(function () {
                        var infolist = [];
                        for (_i = 0; _i < d.words.length; _i++) {
                            cid_form_lid = d.words[_i];
                            infolist.push([
                                CLICS.langByInfo[cid_form_lid[2]].family,
                                cid_form_lid[1],
                                cid_form_lid[0],
                                '?' + cid_form_lid[0],
                                CLICS.langByInfo[cid_form_lid[2]].name,
                                CLICS.langByInfo[cid_form_lid[2]].lon,
                                CLICS.langByInfo[cid_form_lid[2]].lat,
                                cid_form_lid[2]
                            ])
                        }

                        infolist.sort(function (a, b) {
                            if (a[0] > b[0]) {return 1;}
                            if (a[0] < b[0]) {return -1;}
                            else {if (a[4] > b[4]) {return 1;} else {return -1;}}
                        });

                        d3.selectAll(".langlocation").remove();
                        nodeCircles.selectAll("circle")
                            .data(infolist)
                            .enter()
                            .append("circle")
                            .attr("class", "langlocation")
                            .attr("cx", function (d) {return projection([d[5], d[6]])[0];})
                            .attr('cy', function (d) {return projection([d[5], d[6]])[1];})
                            .attr("r", function (d) {return 3;})
                            .style("stroke", "white")
                            .style("stroke-width", 0.5)
                            .style("fill", 'FireBrick');

                        var infolistoutput = [];
                        infolist.forEach(function (c) {
                            var lang = CLICS.langByInfo[c[7]];
                            infolistoutput.push(
                                "<td><a href=\"" + CLLD.route_url('language', {'id': c[7]}) + "\">" + c[4] + "</a></td>" +
                                "<td style=\"background-color:" + lang.color + "; color:" + lang.fontcolor + ";\">" + c[0] + "</td>" +
                                "<td>" + c[1] + "</td>");
                        });
                        var link_label = d.words.length === 1 ? 'colexification' : 'colexifications';
                        return "<h5>" + d.words.length + " " + link_label +
                            " for <a href=\"" + CLLD.route_url('edge', {'id': d.eid}) + "\">&quot;" +
                            d.source.label + "&quot; and &quot;"
                            + d.target.label +
                            "&quot;</a></h5>" +
                            "<table class=\"table table-condensed\"><tr><th>Language</th><th>Family</th>" +
                            "<th>Form</th></tr><tr>" +
                            infolistoutput.join('</tr><tr>') + "</tr></table>";
                    });
                d3.select('#info').classed('hidden', false)
            })
            .on('mouseout', function (d, i) {
                //d3.select(this).style('stroke','#CCC');
            })
        ;

        // node behavior
        node = vis.selectAll("g.node")
            .data(force.nodes())
            .enter()
            .append("svg:g")
            .attr("class", "node");

        node.append("svg:circle")
            .attr("r", 5)
            .style("fill", "#555")
            .style("stroke", "#FFF")
            .style("stroke-width", 3)
            .style('cursor', 'move')
            .on('dragend', function (d) {
                d.fixed = true;
            });
        node.call(node_drag);

        var anchorLink = vis.selectAll("line.anchorLink").data(labelAnchorLinks);

        var anchorNode = vis.selectAll("g.anchorNode")
            .data(force2.nodes())
            .enter()
            .append("svg:g")
            .attr("class", function (d, i) {
                return "anchorNode_" + d.node.index;
            });

        anchorNode.append("svg:circle").attr("r", 0).style("fill", "#FFF");

        anchorNode.append("svg:text")
            .attr('class', function (d, i) {
                return "aNode aNode_" + d.node.index;
            })
            .text(function (d, i) {
                return i % 2 === 0 ? "" : d.node.label;
            })
            .style("fill", "#555")
            .style("font-weight", function (d, i) {
                //console.log(d);
                // make concepts with outer edges bold
                if (d.node.OutEdge.length > 0) {
                    return "bold";
                }
                else {
                    return "normal";
                }

                //return "underline";
            })
            .style("font-family", "Arial")
            .style("font-size", 12)
            .style('cursor', function (d, i) {
                d.node.OutEdge.length > 0 ? cursorvalue = "pointer" : cursorvalue = "arrow";
                return cursorvalue;
            })
            .on('mouseover', function (d, i) {
                //console.log(d);

                d3.selectAll('.link').style('stroke', '#CCC').style('stroke-opacity', opacity / 100);
                d3.select(this).style('fill', 'DarkBlue').style('stroke-opacity', 1);
                nodeByLink[d.node.index].forEach(function (a) {
                    //console.log("effects ",a);
                    d3.selectAll('.aNode_' + a)
                        .style('fill', 'FireBrick').style('stroke-opacity', 1);
                    d3.selectAll('.link_' + a + "-" + d.node.index)
                        .style('stroke', 'OliveDrab').style('stroke-opacity', 1);
                });

                /* info table arrangement for outer links */
                if (d.node.OutEdge.length > 0) {
                    d3.select("#info")
                        .html(function () {
                            //console.log(d);
                            if (d.node.OutEdge.length == 1) {
                                var link_label = "<b>1 strong link ";
                            }
                            else {
                                var link_label = '<b>' + d.node.OutEdge.length + " links ";
                            }
                            var outstring = link_label + 'from &quot;' + d.node.label + '&quot; to other concepts:</b><br>';
                            outstring += '<table class=\"infotable\"><tr><th>No.</th><th>Concept</th><th>Community</th><th>Families</th></tr>';
                            for (var j = 0; j < d.node.OutEdge.length; j++) {
                                outstring += '<tr>';
                                outstring += '<td></td>';
                                outstring += '<td class="infotable"><a href="http://concepticon.clld.org/parameters/' + d.node.OutEdge[j][4] + '">' + d.node.OutEdge[j][1] + '</a></td>';
                                outstring += '<td class="infotable"><a href="?' + d.node.OutEdge[j][0] + '">' + d.node.OutEdge[j][3] + '<a></td>';
                                outstring += '<td class="infotable">' + d.node.OutEdge[j][2] + '</td>';
                                outstring += '</tr>';

                            }
                            return outstring + '</table>';
                        });
                    d3.select('#info').classed('hidden', false);
                }
            })
            .on('mouseout', function (d, i) {
                d3.selectAll('.aNode')
                    .style('fill', '#555')
                    .style('stroke-opacity', opacity / 100)
                ;
                d3.selectAll('.link')
                    .style('stroke', '#CCC')
                    .style('stroke-opacity', opacity / 100)
                ;
            })
            .append('title')
            .text(function (d, i) {
                var outstring = '';
                for (var j = 0; j < d.node.OutEdge.length; j++) {
                    outstring += d.node.OutEdge[j][0] + '\n';
                }
                return outstring;
            });

        var updateLink = function () {
            this.attr("x1", function (d) {
                return d.source.x;
            }).attr("y1", function (d) {
                return d.source.y;
            }).attr("x2", function (d) {
                return d.target.x;
            }).attr("y2", function (d) {
                return d.target.y;
            });
        };

        var updateNode = function () {
            this.attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
        };

        function tick() {
            force2.start();
            node.call(updateNode);

            anchorNode.each(function (d, i) {
                var b, diffX, diffY, dist, shiftX, shiftY;
                if (i % 2 === 0) {
                    d.x = d.node.x;
                    d.y = d.node.y;
                } else {
                    //var b = this.childNodes[1].getBBox();
                    // changed from above due to Firefox bug
                    // (https://bugzilla.mozilla.org/show_bug.cgi?id=612118)
                    b = this.childNodes[1].getBoundingClientRect();
                    diffX = d.x - d.node.x;
                    diffY = d.y - d.node.y;
                    dist = Math.sqrt(diffX * diffX + diffY * diffY);
                    shiftX = b.width * (diffX - dist) / (dist * 2);
                    shiftX = Math.max(-b.width, Math.min(0, shiftX));
                    shiftY = 5;
                    this.childNodes[1].setAttribute("transform", "translate(" + shiftX + "," + shiftY + ")");
                }
            });
            anchorNode.call(updateNode);
            link.call(updateLink);
            anchorLink.call(updateLink);
        }

        // taken from http://davidad.net/colorviz/
        // convert into lab color
        function cl2pix(c, l) {
            var TAU = 6.283185307179586476925287; // also known as "two pi"
            var L = l * 0.61 + 0.09; // L of L*a*b*
            var angle = TAU / 6.0 - c * TAU;
            var r = l * 0.311 + 0.125; //~chroma
            var a = Math.sin(angle) * r;
            var b = Math.cos(angle) * r;
            return [L, a, b];
        }

        // taken from http://www.jasondavies.com/coffee-wheel/
        function brightness(rgb) {
            return rgb.r * .299 + rgb.g * .587 + rgb.b * .114;
        }

        force.on('tick', tick);
    });

    // code taken from http://d3export.cancan.cshl.edu/
    function submit_download_form() {
        // Get the d3js SVG element
        var tmp = document.getElementById("vis");
        var svg = tmp.getElementsByTagName("svg")[0];
        // Extract the data as SVG text string
        var svg_xml = (new XMLSerializer).serializeToString(svg);

        // Submit the <FORM> to the server.
        // The result will be an attachment file to download.
        var form = document.getElementById("svgform");
        form['data'].value = svg_xml;
        form.submit();
    }

    function displayMap() {
        d3.json(world_json, function (error, topology) {
            var countrydata = topojson.object(topology,
                topology.objects.countries).geometries;
            mapPoly.selectAll("path")
                .data(topojson.object(topology, topology.objects.countries)
                    .geometries)
                .enter()
                .append("path")
                .attr("d", path)
                .style("fill", "#c0c0c0")
                .style('stroke', 'white')
                .style('stroke-width', function (d) {
                    return 0;
                })
            ;
        });
    }
};
