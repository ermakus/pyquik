var data = [];
var plot;

var options = {
        selection: { mode: "x" }
};

var placeholder;

function update() {
    plot.setData( data );
    plot.draw();
}

function tick( bars ) {
    n = 1;
    for( i in data ) {
        data[i].data.push( [bars[0], bars[n]] );
        n++;
    }
    update();
}

function draw(datasets) {
    var i = 0;
    $.each(datasets, function(key, val) {
        val.color = i;
        ++i;
    });
    
    placeholder = $("#workspace");
    placeholder.height( $("body").height() - 150 );

    function plotAccordingToChoices(ranges) {

        choiceContainer.find("input:checked").each(function () {
            var key = $(this).attr("name");
            if (key && datasets[key])
                data.push(datasets[key]);
        });

        if (data.length > 0)
            if( !(ranges && "xaxis" in ranges) )
                plot = $.plot(placeholder, data, options );
            else
                plot = $.plot(placeholder, data,
                          $.extend(true, {}, options, {
                              xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to }
                          }));
     }

    // insert checkboxes 
    var choiceContainer = $("#bottom_bar");
    $.each(datasets, function(key, val) {
        choiceContainer.append('<input type="checkbox" name="' + key +
                               '" checked="checked" id="id' + key + '">' +
                               '<label for="id' + key + '">'
                                + val.label + '</label>&nbsp;');
    });
    choiceContainer.find("input").click(plotAccordingToChoices);
    placeholder.bind("plotselected", function (event, ranges) {
        plotAccordingToChoices(ranges);
    });

    plotAccordingToChoices();
}

