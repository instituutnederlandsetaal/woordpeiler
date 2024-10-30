<template>
    <div id="my_dataviz" ref="resizeRef">
    </div>
</template>
<script setup lang="ts">
import { onMounted, ref, watchEffect, watch } from "vue";
// import * as d3 from "d3";
import useResizeObserver from "@/ts/resizeObserver";
import { useGraphStore } from "@/store/GraphStore"

const GraphStore = useGraphStore()

const props = defineProps(["data"]);
// create ref to pass to D3 for DOM manipulation
const svgRef = ref(null);

// create another ref to observe resizing, since observing SVGs doesn't work!
const { resizeRef, resizeState } = useResizeObserver();
const animationDuration = 500;

onMounted(() => {

    // Define the Dutch locale
    const dutchLocale = {
        "dateTime": "%A %e %B %Y %X",
        "date": "%d-%m-%Y",
        "time": "%H:%M:%S",
        "periods": ["AM", "PM"],
        "days": ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"],
        "shortDays": ["zo", "ma", "di", "wo", "do", "vr", "za"],
        "months": ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
        "shortMonths": ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
    };

    // Set up the Dutch locale in D3
    d3.timeFormatDefaultLocale(dutchLocale);

    // pass ref with DOM element to D3, when mounted (DOM available)
    // set the dimensions and margins of the graph
    // const margin = { top: 10, right: 30, bottom: 30, left: 60 },
    //     width = 460 - margin.left - margin.right,
    //     height = 400 - margin.top - margin.bottom;
    const tmp = resizeState.dimensions;

    const svg = d3.select("#my_dataviz")
        .append("svg")
        .attr("width", tmp.width)
        .attr("height", tmp.height)
        .append("g")


    const { width, height } = resizeState.dimensions;
    // append the svg object to the body of the page


    if (!props?.data?.length) {
        return;
    }

    // Now I can use this dataset:


    // Add X axis --> it is a date format
    const x = d3.scaleTime()
        .domain(d3.extent(props.data.flatMap(d => d.data), d => d.x))
        .range([0, width]);
    const xAxis = svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x));

    // Add Y axis
    const y = d3.scaleLinear()
        .domain([0, d3.max(props.data.flatMap(d => d.data), d => d.y)])
        .range([height, 0]);
    const yAxis = svg.append("g")
        .call(d3.axisLeft(y));

    // Add a clipPath: everything out of this area won't be drawn.
    const clip = svg.append("defs").append("svg:clipPath")
        .attr("id", "clip")
        .append("svg:rect")
        .attr("width", width)
        .attr("height", height)
        .attr("x", 0)
        .attr("y", 0);

    // Add brushing
    const brush = d3.brushX()                   // Add the brush feature using the d3.brush function
        //.extent([[0, 0], [width, height]])  // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
        .on("end", updateChart)               // Each time the brush selection changes, trigger the 'updateChart' function

    // Create the line variable: where both the line and the brush take place
    const line = svg.append('g')
        .attr("clip-path", "url(#clip)")

    // Set up the line generator
    const lineGen = d3.line()
        .x(d => x(d.x))
        .y(d => y(d.y));

    const lines = svg.selectAll(".line")
        .data(props.data)
        .enter().append("path")
        .attr("class", "line")
        .attr("clip-path", "url(#clip)")
        .attr("d", d => lineGen(d.data))
        .attr("stroke", d => d.color)
        .attr("fill", "none")
        .attr("data-name", d => d.name);

    // Draw the dots
    props.data.forEach(series => {
        svg.selectAll(`.dot-${series.name}`)
            .data(series.data)
            .enter().append("circle")
            .attr("class", `dot dot-${series.name}`)
            .attr("clip-path", "url(#clip)")
            .attr("cx", d => x(d.x))
            .attr("cy", d => y(d.y))
            .attr("r", 4)
            .attr("fill", series.color);
    });

    // Add the legend
    const legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", `translate(20, -10)`);

    props.data.forEach((series, i) => {
        const legendItem = legend.append("g")
            .attr("class", "legend-item")
            .attr("transform", `translate(${i * 100}, 0)`)
            .on("click", function () {
                // Toggle visibility of the corresponding line and dots
                const line = svg.selectAll(`path[data-name='${series.name}']`);
                const dots = svg.selectAll(`.dot-${series.name}`);
                const currentlyVisible = line.style("display") !== "none";
                line.style("display", currentlyVisible ? "none" : null);
                dots.style("display", currentlyVisible ? "none" : null);
                // Toggle strikethrough style
                d3.select(this).select("text").classed("hidden-line", currentlyVisible);
            });

        legendItem.append("rect")
            .attr("class", "legend-square")
            .attr("x", 0)
            .attr("y", -8)
            .attr("width", 12)
            .attr("height", 12)
            .style("fill", series.color);

        legendItem.append("text")
            .text(series.name)
            .style("fill", 'black')
            .style("font-size", 15)
            .attr("x", 20)
            .attr("y", 3)
    });

    // // Add the line
    // line.append("path")
    //     .datum(props.data)
    //     .attr("class", "line")  // I add the class line to be able to modify this line later on.
    //     .attr("fill", "none")
    //     .attr("stroke", "steelblue")
    //     .attr("stroke-width", 1.5)
    //     .attr("d", d3.line()
    //         .x(function (d) { return x(d.x) })
    //         .y(function (d) { return y(d.y) })
    //     )

    // line
    //     .append("g")
    //     .attr("class", "dots")
    //     .selectAll("dot")
    //     .data(props.data)
    //     .enter()
    //     .append("circle")
    //     .attr("cx", function (d) { return x(d.x) })
    //     .attr("cy", function (d) { return y(d.y) })
    //     .attr("r", 3)
    //     .attr("fill", "#69b3a2")

    // Add the brushing
    svg
        .append("g")
        .attr("class", "brush")
        .call(brush);

    // A function that set idleTimeOut to null
    let idleTimeout
    function idled() { idleTimeout = null; }

    // A function that update the chart for given boundaries
    function updateChart(event) {

        // What are the selected boundaries?
        const extent = event.selection

        // If no selection, back to initial coordinate. Otherwise, update X axis domain
        if (!extent) {
            if (!idleTimeout) return idleTimeout = setTimeout(idled, 350); // This allows to wait a little bit
            x.domain(d3.extent(props.data.flatMap(d => d.data), d => d.x))
        } else {
            x.domain([x.invert(extent[0]), x.invert(extent[1])])
            svg.select(".brush").call(brush.move, null) // This remove the grey brush area as soon as the selection has been done
        }

        // Update axis and line position
        xAxis.transition().duration(animationDuration).call(d3.axisBottom(x))
        // actually we should do this for all lines
        svg.selectAll(".line")
            .data(props.data)
            .transition()
            .duration(animationDuration)
            .attr("d", d => lineGen(d.data))
        // and dots
        props.data.forEach(series => {
            svg.selectAll(`.dot-${series.name}`)
                .data(series.data)
                .transition()
                .duration(animationDuration)
                .attr("cx", d => x(d.x))
                .attr("cy", d => y(d.y))
        });


    }

    // If user double click, reinitialize the chart
    svg.on("dblclick", function () {
        // fake a call to updateChart
        updateChart({ selection: null })
    });

    // responsive resize
    watchEffect(() => {

        const { width, height } = resizeState.dimensions;

        svg.attr("width", width).attr("height", height);

        x.range([0, width]);
        xAxis.attr("transform", `translate(0, ${height})`).call(d3.axisBottom(x));

        y.range([height, 0]);
        yAxis.call(d3.axisLeft(y));

        clip.attr("width", width).attr("height", height);
        // brush.extent([[0, 0], [width, height]]);

        line.select(".line").attr("d", d3.line()
            .x(function (d) { return x(d.x) })
            .y(function (d) { return y(d.y) })
        );
    });

});




</script>

<style lang="scss">
.legend-square {
    width: 12px;
    height: 12px;
    display: inline-block;
    margin-right: 5px;
}

.legend-item {
    cursor: pointer;
}

.hidden-line {
    text-decoration: line-through;
}

.legend-text {
    font-size: 12px;
    color: black;
}
</style>