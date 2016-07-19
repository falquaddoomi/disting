function buildMatrix(nodeCount, graphID, matrixID) {
    var $matHolder = $(matrixID);
    var $graphHolder = $(graphID);

    var graph = new Springy.Graph();

    var nodes = {};
    for (var i = 1; i <= nodeCount; i++)
        nodes[i] = graph.newNode({label: i});
    graph.nodeCount = nodeCount;
    // destroy and recreate the canvas
    $graphHolder.empty();
    $('<canvas class="graph_canvas" width="400" height="400" style="border: solid 1px gray;" />')
        .appendTo($graphHolder);

    // attach springy to our canvas
    var springy = window.springy = $graphHolder.find(".graph_canvas").springy({
        graph: graph
    });

    // clear the matrix
    $matHolder.empty();

    // ===============================
    // === equation section
    // ===============================

    $('<tr class="inline_header"><td colspan="' + nodeCount + '">Adjacency <a id="adj_tooltip">[?]</a>:</td></tr>')
        .appendTo($matHolder);

    // build the matrix itself
    for (var k in nodes) {
        // make a new row
        var $row = $("<tr class='row' />");

        for (var j in nodes) {
            var $cell = $("<td />");

            // add the cell at this row
            $("<input type='checkbox' name='item_" + k + "-" + j + "' id='item_" + k + "-" + j + "' />")
                .data('to', k)
                .data('from', j)
                .val(1)
                .change(function() {
                    var $mylabel = $("label[for='" + $(this).attr('id') + "']");

                    if ($(this).data('from') == $(this).data('to'))
                        nodes[$(this).data('from')].isEnvEdge = this.checked;

                    if (this.checked) {
                        graph.newEdge(nodes[$(this).data('from')], nodes[$(this).data('to')], {color: '#6A4A3C'});
                        $mylabel.removeClass("unselected");
                    }
                    else {
                        var edges = graph.getEdges(nodes[$(this).data('from')], nodes[$(this).data('to')]);
                        for (i in edges)
                            graph.removeEdge(edges[i]);
                        $mylabel.addClass("unselected");
                    }
                }).appendTo($cell);

            $("<label for='item_" + k + "-" + j + "' />")
                .addClass("unselected")
                .html("a<sub>" + k + "," + j + "</sub>")
                .appendTo($cell);

            if (parseInt(j) < parseInt(nodeCount)-1) {
                $("<span> +</span>")
                    .appendTo($cell);
            }

            $cell.appendTo($row);
        }

        // add that row to the thing
        $row.appendTo($matHolder);
    }

    // ===============================
    // === inputs section
    // ===============================

    $('<tr class="inline_header"><td colspan="' + nodeCount + '">Inputs:</td></tr>')
        .appendTo($matHolder);

    var $input_row = $("<tr class='row' />");

    for (var j in nodes) {
        var $cell = $("<td />");

        // add the cell at this row
        $("<input type='checkbox' name='input_" + j + "' id='input_" + j + "' />")
            .data('from', j)
            .val(1)
            .change(function() {
                var $mylabel = $("label[for='" + $(this).attr('id') + "']");

                // make the node visibly an input node (or not)
                nodes[$(this).data('from')].isInput = this.checked;
                springy.renderer.start();
            }).appendTo($cell);

        $("<label for='input_" + j + "' />")
            .html("b<sub>" + j + "</sub>")
            .appendTo($cell);

        $cell.appendTo($input_row);
    }

    // add that row to the thing
    $input_row.appendTo($matHolder);

    // ===============================
    // === outputs section
    // ===============================


    $('<tr class="inline_header"><td colspan="' + nodeCount + '">Outputs:</td></tr>')
        .appendTo($matHolder);

    var $output_row = $("<tr class='row' />");

    for (var j in nodes) {
        var $cell = $("<td />");

        // add the cell at this row
        $("<input type='checkbox' name='output_" + j + "' id='output_" + j + "' />")
            .data('from', j)
            .val(1)
            .change(function() {
                var $mylabel = $("label[for='" + $(this).attr('id') + "']");

                // make the node visibly an input node (or not)
                nodes[$(this).data('from')].isOutput = this.checked;
                springy.renderer.start();
            }).appendTo($cell);

        $("<label for='output_" + j + "' />")
            .html("c<sub>" + j + "</sub>")
            .appendTo($cell);

        $cell.appendTo($output_row);
    }

    // add that row to the thing
    $output_row.appendTo($matHolder);
}

function updateMatrix(Adj, B, C) {
    // iterate over the rows of the matrix
    $.each(Adj.replace(/(\[|\])/gm, '').split(";"), function(k, row) {
        k += 1;
        $.each(row.trim().split(' '), function(j, col) {
            j += 1;
            $("#item_" + k + "-" + j).prop('checked', (col == 1)).val(col).change();
        });
    });

    // iterate over elements of input (;-delimited)
    $.each(B.replace(/(\[|\])/gm, '').split(";"), function(idx, val) {
        idx += 1;
        $("#input_" + idx).prop('checked', (val == 1)).val(val).change();
    });

    // iterate over elements of output (space-delimited)
    $.each(C.replace(/(\[|\])/gm, '').split(" "), function(idx, val) {
        idx += 1;
        $("#output_" + idx).prop('checked', (val == 1)).val(val).change();
    });
}
