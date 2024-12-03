<template>
    <div id="my_dataviz" ref="resizeRef"></div>
    <div id="tooltip"></div>
</template>


<script setup lang="ts">
// Libraries
import { onMounted, watchEffect, ref, computed } from "vue";
import { storeToRefs } from "pinia";
import * as d3 from "d3";
// Stores
import { useSearchResultsStore } from "@/stores/SearchResultsStore";
import { useSearchSettingsStore } from "@/stores/SearchSettingsStore";
// Util
import useResizeObserver from "@/ts/resizeObserver"
import { GraphItem } from "@/types/Search";

// Stores
const { searchSettings } = storeToRefs(useSearchSettingsStore());
const { searchResults } = storeToRefs(useSearchResultsStore());

// Computed
const visible = computed<GraphItem[]>(() => searchResults.value.filter(d => d.searchItem.visible));

// create another ref to observe resizing, since observing SVGs doesn't work!
const { resizeRef, resizeState } = useResizeObserver();
const animationDuration = 500;
const maxPoints = 500;

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


    // append the svg object to the body of the page
    const svg = d3.select("#my_dataviz")
        .append("svg")
        .append("g")

    // Add X axis --> it is a date format
    const x = d3.scaleTime()
    const xAxis = svg.append("g").attr("class", "x-axis")

    // Add Y axis
    const y = d3.scaleLinear()
    const yAxis = svg.append("g").attr("class", "y-axis")

    // Add a clipPath: everything out of this area won't be drawn.
    const clip = svg.append("defs").append("svg:clipPath")
        .attr("id", "clip")
        .attr("class", "clip")
        .append("svg:rect")

    // Add brushing
    const brush = d3.brushX()
    const brushEl = svg.append("g")

    // Add the legend
    // const legend = svg.append("g")
    //     .attr("class", "legend")
    //     .attr("transform", `translate(20, -10)`);


    // Set up the line generator
    const lineGen = d3.line()
        .x(d => x(d.x))
        .y(d => y(d.y));

    // data
    watchEffect(() => {
        // clear the svg
        svg.selectAll(".line-group").remove();
        svg.selectAll(".legend-item").remove();

        // Sample the data to maxPoints
        const flat = visible.value.flatMap(d => d.data);
        // const zoomLevel = x.domain()[1] - x.domain()[0];
        // const totalPoints = flat.length;
        // const sampleRate = Math.max(1, Math.floor(totalPoints / maxPoints));
        const sampledData = visible.value

        // first update the axes
        x.domain(d3.extent(flat, d => d.x));
        xAxis.call(d3.axisBottom(x));
        // y domain from 0 to max value
        y.domain([0, d3.max(flat, d => d.y)]);
        yAxis.call(d3.axisLeft(y));


        // add empty g for each dataseries and data-label it
        sampledData.forEach(series => {
            svg.append("g")
                .attr("data-name", series.uuid)
                .attr("clip-path", "url(#clip)")
                .attr("class", "line-group");
        });

        // Legend
        // sampledData.forEach((series, i) => {
        //     const legendItem = legend.append("g")
        //         .attr("class", "legend-item")
        //         .attr("transform", `translate(${i * 100}, 0)`)
        //         .on("click", function () {
        //             // Toggle visibility of the corresponding line and dots
        //             const line = svg.selectAll(`g[data-name='${series.uuid}']`);
        //             const currentlyVisible = line.style("display") !== "none";
        //             line.style("display", currentlyVisible ? "none" : null);
        //             // Toggle strikethrough style
        //             d3.select(this).select("text").classed("hidden-line", currentlyVisible);

        //         });
        //     legendItem.append("rect")
        //         .attr("class", "legend-square")
        //         .attr("x", 0)
        //         .attr("y", -8)
        //         .attr("width", 12)
        //         .attr("height", 12)
        //         .style("fill", "#" + series.searchItem.color);
        //     legendItem.append("text")
        //         .text(series.searchItem.wordform)
        //         .style("fill", 'black')
        //         .style("font-size", 15)
        //         .attr("x", 20)
        //         .attr("y", 3)
        // });

        // draw the lines
        sampledData.forEach(series => {
            svg.select(`.line-group[data-name='${series.uuid}']`)
                .selectAll('.line')
                .data([series])
                .enter().append("path")
                .attr("class", "line")
                .attr("d", d => lineGen(d.data))
                .attr("fill", "none")
                .attr("stroke", "#" + series.searchItem.color)
                .attr("stroke-width", 2)
                .style("pointer-events", "none");

        });

        // Draw the dots
        sampledData.forEach(series => {
            // link data
            series.data.forEach(d => {
                d.searchItem = series.searchItem;
            });

            const dot = svg.select(`.line-group[data-name='${series.uuid}']`)
                .selectAll('.dot')
                .data(series.data)
                .enter().append("g")
                .attr("class", `dot`)
                .attr("transform", d => `translate(${x(d.x)}, ${y(d.y)})`);
            dot.append("circle")
                .attr("r", 4)
                .attr("fill", "#" + series.searchItem.color)
            dot.append("circle")
                .attr("class", "hit-area")
                .attr("r", 15)
                .attr("fill", "transparent")

        });

        // tooltip events
        const tooltip = d3.select("#tooltip");
        let tooltipVisible = false;
        let left, top;

        svg.selectAll(".hit-area")
            .on("mouseover", function (event, d) {
                if (tooltipVisible) return;
                tooltip.style("visibility", "visible");
                tooltip.html(tooltipHtml(d))
            })
            .on("mousemove", function (event, d) {
                if (tooltipVisible) return;
                let tooltipWidth = tooltip.node().offsetWidth;
                let tooltipHeight = tooltip.node().offsetHeight;
                let targetRect = event.target.getBoundingClientRect();
                let center = {
                    x: targetRect.left + targetRect.width / 2,
                    y: targetRect.top + targetRect.height / 2
                }
                let margin = 10;

                left = center.x - tooltipWidth / 2;
                top = center.y - tooltipHeight - margin;

                // if tooltip is going out of the window, then move it inside
                if (left + tooltipWidth > window.innerWidth) {
                    left = window.innerWidth - tooltipWidth;
                }
                if (top < 0) {
                    top = event.pageY + 10; // below the cursor
                }

                tooltip
                    .style("left", left + "px")
                    .style("top", top + "px");
            })
            .on("mouseout", function (d) {
                if (tooltipVisible) return;
                tooltip.style("visibility", "hidden");
            })


        tooltip.on("mouseout", function (d) {
            tooltip.style("visibility", "hidden");
        }).on("mouseover", function (d) {
            tooltip.style("visibility", "visible");
        });
    })


    // A function that set idleTimeOut to null
    let idleTimeout
    function idled() { idleTimeout = null; }

    // A function that update the chart for given boundaries
    function brushChart(event) {
        // What are the selected boundaries?
        const extent = event.selection

        if (!extent) {
            // If no selection, back to initial coordinate. Otherwise, update X axis domain
            if (!idleTimeout) return idleTimeout = setTimeout(idled, 350); // This allows to wait a little bit
            x.domain(d3.extent(visible.value.flatMap(d => d.data), d => d.x))
        } else {
            // A selection was made
            // remove the grey brush area
            brushEl.call(brush.move, null)

            // if the extent is really small, do nothing
            if (extent[0] + 20 > extent[1]) return // safely return, grey brush area is removed above

            // otherwise, update the x domain
            x.domain([x.invert(extent[0]), x.invert(extent[1])])
        }

        // Update axis and line position
        xAxis.transition().duration(animationDuration).call(d3.axisBottom(x))

        // // Sample the data to maxPoints
        // const startX = x.domain()[0];
        // const endX = x.domain()[1];
        // const flat = visible.value.flatMap(d => d.data).filter(d => d.x >= startX && d.x <= endX);
        // const totalPoints = flat.length;
        // const sampleRate = Math.max(1, Math.floor(totalPoints / maxPoints));
        // const sampledData = visible.value.map(series => ({
        //     ...series,
        //     data: flat.filter((_, index) => index % sampleRate === 0)
        // }));

        // update the lines and dots data
        visible.value.forEach(series => {
            svg.select(`.line-group[data-name='${series.uuid}']`)
                .selectAll('.line')
                .data([series])
                .transition().duration(animationDuration)
                .attr("d", d => lineGen(d.data))
            svg.select(`.line-group[data-name='${series.uuid}']`)
                .selectAll('.dot')
                .data(series.data)
                .transition().duration(animationDuration)
                .attr("transform", d => `translate(${x(d.x)}, ${y(d.y)})`);
        })
    }

    // If user double click, reinitialize the chart
    svg.on("dblclick", function () {
        // fake a call to updateChart
        brushChart({ selection: null })
    });

    // responsive resize
    watchEffect(() => {
        let { width, height } = resizeState.dimensions;
        const svgMargin = { x: 15, y: 0 };
        width -= svgMargin.x * 2;

        svg.attr("width", width - svgMargin.x).attr("height", height).attr("transform", `translate(${svgMargin.x * 2}, 0)`);

        x.range([0, width]);
        xAxis.attr("transform", `translate(0, ${height})`).call(d3.axisBottom(x));

        y.range([height, 0]);
        yAxis.attr("transform", `translate(0, 0)`).call(d3.axisLeft(y));

        const clipMargin = { x: 3, y: 10 };
        clip.attr("width", width + 2 * clipMargin.x).attr("height", height + 2 * clipMargin.y).attr("x", -clipMargin.x).attr("y", -clipMargin.y);
        brush.extent([[0, 0], [width, height]]).on("end", brushChart)
        brushEl.call(brush);
        // lines
        svg.selectAll(".line").attr("d", d => lineGen(d.data));
        // dots
        svg.selectAll(".dot")
            .attr("transform", d => `translate(${x(d.x)}, ${y(d.y)})`);
    });

});


// round e.g. 1.4999 to 1.49 at decimals=2
function truncateRound(value: number, decimals) {
    const scaledFloat = value * Math.pow(10, decimals)
    const integerPart = Math.floor(scaledFloat)
    const truncated = integerPart / Math.pow(10, decimals)
    return truncated
}

function tooltipHtml(d) {
    const date = d3.timeFormat("%Y-%m-%d")(d.x);
    const value = truncateRound(d.y, 2).toLocaleString();
    const href = constructBlLink(d);
    return `${date}<br><b>${value}</b><br/><a target='_blank' href='${href}'>Zoeken in CHN</a>`
}

/** Construct a BlackLab link for the wordform*/
function constructBlLink(d): string {

    const params = {
        patt: constructBLPatt(d.searchItem),
        filter: constructBLFilter(d),
        interface: JSON.stringify({ form: "search", patternMode: "expert" }),
        groupDisplayMode: "relative hits",
        group: "field:titleLevel2:i"
    }
    const base = "http://svotmc10.ivdnt.loc:8080/corpus-frontend/chn-intern/search/hits"

    return `${base}?${new URLSearchParams(params).toString()}`
}

function constructBLPatt(d) {
    const pattTerms = {
        lemma: d.lemma,
        word: d.wordform,
    }
    // Add pos separately because only one can be present
    if (d.pos?.includes("(")) {
        pattTerms["pos_full"] = d.pos
    }
    else {
        pattTerms["pos"] = d.pos
    }

    // Remove falsy values, and blank strings (could be tabs and spaces)
    Object.keys(pattTerms).forEach(
        (key) => (pattTerms[key] == null || pattTerms[key].trim() === "") && delete pattTerms[key]
    )
    const patt = Object.entries(pattTerms).map(([key, value]) => `${key}=l"${value}"`).join("&")
    return `[${patt}]`
}

function constructBLFilter(d) {
    const filters = {
        medium: "newspaper",
        witnessYear_from: d3.timeFormat("%Y")(d.x),
    }
    const timeBucket = searchSettings.value.timeBucketType;

    if (timeBucket != "year") {
        filters["witnessMonth_from"] = parseInt(d3.timeFormat("%m")(d.x))
    }

    if (d.searchItem.newspaper) {
        filters["titleLevel2"] = `"${d.searchItem.newspaper}"`
    }

    return Object.entries(filters).map(([key, value]) => `${key}:${value}`).join(" AND ")
}
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

.overlay {
    cursor: crosshair;
}

.x-axis {
    font-size: calc(0.5vw + 0.3rem)
}

.y-axis {
    font-size: calc(0.5vw + 0.3rem)
}

/* Step 2: Style the tooltip */
#tooltip {
    position: absolute;
    background-color: white;
    border: 1px solid #ccc;
    padding: 5px;
    border-radius: 3px;
    pointer-events: none;
    visibility: hidden;
    z-index: 1000;
    pointer-events: all;

    a {
        color: blue;
    }
}
</style>