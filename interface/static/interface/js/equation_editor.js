function buildMatrix(nodeCount, graphID, matrixID) {
    var $matHolder = $(matrixID);
    var $graphHolder = $(graphID);

    var graph = new Springy.Graph();

    var nodes = {};
    for (var i = 0; i < nodeCount; i++)
        nodes[i] = graph.newNode({label: i});

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

    // label for the equation section
    $('<tr class="inline_header"><td colspan="' + nodeCount + '">Adjacency</td></tr>')
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
                .change(function() {
                    var $mylabel = $("label[for='" + $(this).attr('id') + "']");
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

    // label for the inputs section
    $('<tr class="inline_header"><td colspan="' + nodeCount + '">Inputs</td></tr>')
        .appendTo($matHolder);

    var $input_row = $("<tr class='row' />");

    for (var j in nodes) {
        var $cell = $("<td />");

        // add the cell at this row
        $("<input type='checkbox' name='input_" + j + "' id='input_" + j + "' />")
            .data('to', k)
            .data('from', j)
            .change(function() {
                var $mylabel = $("label[for='" + $(this).attr('id') + "']");
                if (this.checked) {
                }
                else {
                }
            }).appendTo($cell);

        $("<label for='input_" + j + "' />")
            .html("a<sub>" + k + "," + j + "</sub>")
            .appendTo($cell);

        if (parseInt(j) < parseInt(nodeCount)-1) {
            $("<span>, </span>")
                .appendTo($cell);
        }

        $cell.appendTo($input_row);
    }

    // add that row to the thing
    $input_row.appendTo($matHolder);

    // label for the outputs section
    $('<tr class="inline_header"><td colspan="' + nodeCount + '">Outputs</td></tr>')
        .appendTo($matHolder);
}