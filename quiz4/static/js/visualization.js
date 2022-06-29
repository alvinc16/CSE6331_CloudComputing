function worldMap(quakeData){
    var svg = d3.select("body")
                .append("svg")
                .attr("width", "100%")
                .attr("height", 800);
    // Append Div for tooltip to SVG
    var div = d3.select("body")
                .append("div")   
                .attr("class", "tooltip")               
                .style("opacity", 0);
    var projection = d3.geoEqualEarth().rotate([90, 0, 0]);
    var path = d3.geoPath().projection(projection);

    var url = "http://enjalot.github.io/wwsd/data/world/world-110m.geojson";

    d3.json(url).then(function(data) {
        var world = data
        var encodedStr = quakeData
        var parser = new DOMParser
        var dom = parser.parseFromString(
            '<!doctype html><body>' + encodedStr,
            'text/html');
        var decodedString = dom.body.textContent.replace(/'/g, '"')
        var quakes = JSON.parse(decodedString)
        
        svg.append("path")
        .attr("d", path(world))
        .attr("fill", "lightgray")
        .attr("stroke", "white");
        
        svg.selectAll("circle")
        .data(quakes)
        .enter()
        .append("circle")
        .attr("r", function(d) {
            return Math.sqrt(d.MAG) * 4;
        })
        .attr("cx", function(d) {
            return projection([d.LONGTITUDE, d.LATITUDE])[0]
        })
        .attr("cy", function(d) {
            return projection([d.LONGTITUDE, d.LATITUDE])[1]
        })
        .attr("fill", "darkgreen")
        .attr("opacity", 0.5)
        .on("mouseover", function(d) {
            div.transition()        
            .duration(200)      
            .style("opacity", .9);      
            div.text(`Time:${d.TIME.slice(0, 10)} |  
                    Place:${d.PLACE} |  
                    Magnitude:${d.MAG.slice(0, 4)}`)
            .style("left", (d3.event.pageX) + "px")     
            .style("top", (d3.event.pageY - 28) + "px");
        })
        // fade out tooltip on mouse out               
        .on("mouseout", function(d) {       
            div.transition()        
                .duration(500)      
                .style("opacity", 0);   
        });
        
        window.setTimeout(function() {
        svg.selectAll("circle")
            .transition().duration(5000)
            .attr("r", function(d) {
            return Math.sqrt(d.MAG) * 4;
            });
        }, 5000);
    });
}

function scatterChart(id, scatterData) {
    // set the dimensions and margins of the graph
    var margin = {top: 20, right: 20, bottom: 50, left: 70},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    var scatter_svg = d3.select(id)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    //Read the data
    var encodedStr = scatterData;
    var parser = new DOMParser;
    var dom = parser.parseFromString(
    '<!doctype html><body>' + encodedStr,
    'text/html');
    var decodedString = dom.body.textContent.replace(/'/g, '"')
    var scatter_data = JSON.parse(decodedString)
    console.log('qqq', scatter_data)
    // Add X axis
    var x = d3.scaleLinear()
              .domain([0, 200])
              .range([ 0, width ]);
    scatter_svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x))
    // Add Y axis
    var y = d3.scaleLinear()
            .domain([0, 100])
            .range([ height, 0]);
    scatter_svg.append("g")
            .call(d3.axisLeft(y))
    // Add dots
    scatter_svg.append('g')
            .selectAll("dot")
            .data(scatter_data)
            .enter()
            .append("circle")
            .attr("cx", function (d) { console.log("X");console.log(d.X); return x(d.X); } )
            .attr("cy", function (d) { console.log("Y");console.log(parseInt(d.Y)); return y(parseInt(d.Y)); } )
            .attr("r", 3)
            .style("fill", "#69b3a2")
    // text label for the x axis
    scatter_svg.append("text")             
    .attr("transform",
            "translate(" + (width/2) + " ," + 
                        (height + margin.top + 20) + ")")
    .style("text-anchor", "middle")
    .text("X");
    // text label for the y axis
    scatter_svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left)
            .attr("x",0 - (height / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .text("Y");

}

function dashboard(id, quakeScale, quakeData=null) {    
    var barColor = 'steelblue';
    function segColor(c){ 
        return { "grape":"#807dba",
                 "fig":"#e08214",
                 "banana":"#41ab5d",
                 "cherry":"#e01714",
                 "apple":"#dde014",
                 "berry":"#41ab6d",
                 "pear":"#a041ab",}[c];}
    
    // function to handle histogram.
    function histoGram(fD){
        var hG={}
        var hGDim = {t: 60, r: 0, b: 30, l: 0};
        hGDim.w = 500 - hGDim.l - hGDim.r, 
        hGDim.h = 300 - hGDim.t - hGDim.b;
            
        //create svg for histogram.
        var hGsvg = d3.select(id).append("svg")
            .attr("width", hGDim.w + hGDim.l + hGDim.r)
            .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
            .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

        // create function for x-axis mapping.
        var x = d3.scaleBand().range([0, hGDim.w], 0.1)
                               .domain(fD.map(function(d) { return d[0]; }));

        // Add x-axis to the histogram svg.
        hGsvg.append("g").attr("class", "x axis")
            .attr("transform", "translate(0," + hGDim.h + ")")
            // .call(d3.svg.axis().scale(x).orient("bottom"));
            .call(d3.axisBottom(x));

        // Create function for y-axis map.
        var y = d3.scaleLinear().range([hGDim.h, 0])
                .domain([0, d3.max(fD, function(d) { return d[1]; })]);

        // Create bars for histogram to contain rectangles and freq labels.
        var bars = hGsvg.selectAll(".bar").data(fD).enter()
                .append("g").attr("class", "bar");
        
        //create the rectangles.
        bars.append("rect")
            .attr("x", function(d) { return x(d[0]); })
            .attr("y", function(d) { return y(d[1]); })
            .attr("width", x.bandwidth())
            .attr("height", function(d) { return hGDim.h - y(d[1]); })
            .attr('fill',barColor)
            .on("mouseover",mouseover)// mouseover is defined below.
            .on("mouseout",mouseout);// mouseout is defined below.
            
        //Create the frequency labels above the rectangles.
        bars.append("text").text(function(d){ return d3.format(",")(d[1])})
            .attr("x", function(d) { return x(d[0])+x.bandwidth()/2; })
            .attr("y", function(d) { return y(d[1])-5; })
            .attr("text-anchor", "middle");
        
        function mouseover(d){  // utility function to be called on mouseover.
        }
        
        function mouseout(d){    // utility function to be called on mouseout.
        }
        
        // create function to update the bars. This will be used by pie-chart.
        hG.update = function(nD, color){
            // update the domain of the y-axis map to reflect change in frequencies.
            y.domain([0, d3.max(nD, function(d) { return d[1]; })]);
            
            // Attach the new data to the bars.
            var bars = hGsvg.selectAll(".bar").data(nD);
            
            // transition the height and color of rectangles.
            bars.select("rect").transition().duration(500)
                .attr("y", function(d) {return y(d[1]); })
                .attr("height", function(d) { return hGDim.h - y(d[1]); })
                .attr("fill", color);

            // transition the frequency labels location and change value.
            bars.select("text").transition().duration(500)
                .text(function(d){ return d3.format(",")(d[1])})
                .attr("y", function(d) {return y(d[1])-5; });            
        }        
        return hG;
    }
    
    // function to handle pieChart.
    function pieChart(pD){
        var pC ={},    pieDim ={w:250, h: 250};
        pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;
                
        // create svg for pie chart.
        var piesvg = d3.select(id).append("svg")
            .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
            .attr("transform", "translate("+pieDim.w/2+","+pieDim.h/2+")");
        
        // create function to draw the arcs of the pie slices.
        var arc = d3.arc().outerRadius(pieDim.r - 10).innerRadius(0);

        // create a function to compute the pie slice angles.
        var pie = d3.pie().sort(null).value(function(d) { return d.freq; });

        // Draw the pie slices.
        piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
            .each(function(d) { this._current = d; })
            .style("fill", function(d) { return segColor(d.data.type); })
            .on("mouseover",mouseover).on("mouseout",mouseout);

        // create function to update pie-chart. This will be used by histogram.
        pC.update = function(nD){
            piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                .attrTween("d", arcTween);
        }        
        // Utility function to be called on mouseover a pie slice.
        function mouseover(d){
            // call the update function of histogram with new data.
            // hG.update(fData.map(function(v){ 
            //     return [v.State,v.freq[d.data.type]];}),segColor(d.data.type));
        }
        //Utility function to be called on mouseout a pie slice.
        function mouseout(d){
            // call the update function of histogram with all data.
            // hG.update(fData.map(function(v){
            //     return [v.State,v.total];}), barColor);
        }
        // Animating the pie-slice requiring a custom function which specifies
        // how the intermediate paths should be drawn.
        function arcTween(a) {
            var i = d3.interpolate(this._current, a);
            this._current = i(0);
            return function(t) { return arc(i(t));    };
        }    
        return pC;
    }

    // function to handle legend.
    function legend(lD){
        var leg = {};
            
        // create table for legend.
        var legend = d3.select(id).append("table").attr('class','legend');
        
        // create one row per segment.
        var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");
            
        // create the first column for each segment.
        tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
            .attr("width", '16').attr("height", '16')
			.attr("fill",function(d){ return segColor(d.type); });
            
        // create the second column for each segment.
        tr.append("td").text(function(d){ return d.type;});

        // create the third column for each segment.
        tr.append("td").attr("class",'legendFreq')
            .text(function(d){ return d3.format(",")(d.freq);});

        // create the fourth column for each segment.
        tr.append("td").attr("class",'legendPerc')
            .text(function(d){ return getLegend(d,lD);});

        // Utility function to be used to update the legend.
        leg.update = function(nD){
            // update the data attached to the row elements.
            var l = legend.select("tbody").selectAll("tr").data(nD);

            // update the frequencies.
            l.select(".legendFreq").text(function(d){ return d3.format(",")(d.freq);});

            // update the percentage column.
            l.select(".legendPerc").text(function(d){ return getLegend(d,nD);});        
        }
        
        function getLegend(d,aD){ // Utility function to compute percentage.
            return d3.format("%")(d.freq/d3.sum(aD.map(function(v){ return v.freq; })));
        }

        return leg;
    }
    
    
    hisArr = Object.keys(quakeScale).map(function(k) {
    return [k, quakeScale[k]]
    })
    pieArr = Object.keys(quakeScale).map(function(k) {
    return {'type': k, 'freq': quakeScale[k]}
    })
    legArr = Object.keys(quakeScale).map(function(k) {
    return {'type': k, 'freq': quakeScale[k]}
    })
    if(quakeData!=null) {
        worldMap(quakeData); //// create the world map
    }
    histoGram(hisArr) // create the histogram.
    pieChart(pieArr) // create the pie-chart.
    legend(legArr)  // create the legend.       
}