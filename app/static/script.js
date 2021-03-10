function getPosition(element) {
	var rect = element.getBoundingClientRect();
	return { x: rect.left, y: rect.top };
}

var gd = document.getElementById('plot');
var pos = getPosition(gd);

gd.addEventListener("click", function (evt) {
    let xaxis = gd._fullLayout.xaxis;
    let yaxis = gd._fullLayout.yaxis;
    let l = gd._fullLayout.margin.l;
    let t = gd._fullLayout.margin.t;
    
	var xInDataCoord = xaxis.p2c(evt.x - l - pos.x + document.documentElement.scrollLeft);
	var yInDataCoord = yaxis.p2c(evt.y - t - pos.y + document.documentElement.scrollTop);
	
	let type;
	if (document.getElementById('train').checked) type = "train";
	if (document.getElementById('test').checked) type = "test";
	
	if (xInDataCoord > gd.layout.xaxis.range[0] && xInDataCoord < gd.layout.xaxis.range[1]
     && yInDataCoord > gd.layout.yaxis.range[0] && yInDataCoord < gd.layout.yaxis.range[1]) {
    	var point = {x:xInDataCoord, y:yInDataCoord, type:type};
    	
    	if (type == "train") Plotly.extendTraces(gd, {x:[[xInDataCoord]], y:[[yInDataCoord]],}, [0]);
    	if (type == "test") Plotly.extendTraces(gd, {x:[[xInDataCoord]], y:[[yInDataCoord]],}, [1]);
    
    	$.post('/addpoint', {point_data: JSON.stringify(point)});
	}
});

$(document).ready(function() {
	$('.algorithmButton').click(function() {
    	let algorithm_data = {algorithm:this.id, k:document.getElementById("kvalue").value};
        $.post('/algorithmrun', {
            algorithm_data: JSON.stringify(algorithm_data)
        }, function(data) {
            var traceData = jQuery.parseJSON(data);
            Plotly.newPlot(gd, traceData, {});
        });
	});
	
	$('#clearButton').click(function() {
    	$.post('/clearplot', {}, function(data) {
        	var traceData = jQuery.parseJSON(data);
        	Plotly.newPlot(gd, traceData, {});
    	});
    	
	});
	
});