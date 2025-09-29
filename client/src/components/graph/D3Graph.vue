<template>
    <div id="svg-container" ref="resizeRef"></div>
    <div id="tooltip"></div>
</template>

<script setup lang="ts">
// Libraries
import * as d3 from "d3"
// Stores
import { useSearchResults } from "@/stores/search/searchResults"
// Util
import useResizeObserver from "@/ts/resizeObserver"
import { IntervalType } from "@/types/searchSettings"
import { searchToString } from "@/types/search"
import { type GraphItem } from "@/types/graph"
import { tooltipHtml } from "@/ts/tooltip"
import { constructSearchLink } from "@/ts/blacklab/blacklab"

// Stores
const { searchResults, lastSearchSettings } = storeToRefs(useSearchResults())

// Computed
const visible = computed<GraphItem[]>(() => searchResults.value.filter((d) => d.searchItem.visible))
const graphTitle = computed(() => {
    if (!lastSearchSettings.value) return ""

    const freqType = lastSearchSettings.value.frequencyType === "abs" ? "Absolute" : "Relatieve"
    const timeBucketSize = lastSearchSettings.value.intervalLength
    const timeBucketType = lastSearchSettings.value.intervalType
    let timeBucketStr
    if (timeBucketType == IntervalType.MONTH) {
        timeBucketStr = timeBucketSize > 1 ? "maanden" : "maand"
    } else if (timeBucketType == IntervalType.YEAR) {
        timeBucketStr = timeBucketSize > 1 ? "jaren" : "jaar"
    } else if (timeBucketType == IntervalType.WEEK) {
        timeBucketStr = timeBucketSize > 1 ? "weken" : "week"
    } else {
        timeBucketStr = timeBucketSize > 1 ? "dagen" : "dag"
    }
    const timeBucket = timeBucketSize > 1 ? `${timeBucketSize} ${timeBucketStr}` : timeBucketStr

    return `${freqType} woordfrequentie per ${timeBucket}`
})

const zoomedIn = ref(false)

// create another ref to observe resizing, since observing SVGs doesn't work!
const { resizeRef, resizeState } = useResizeObserver()
const animationDuration = 500
const maxPoints = 500

defineExpose({ resizeState, resetZoom, zoomedIn })

function dateFormat(date: Date) {
    if (d3.timeMonth(date) < date) {
        return d3.timeFormat("%e %b")(date)
    } else if (d3.timeYear(date) < date) {
        return d3.timeFormat("%b ’%y")(date)
    } else {
        return d3.timeFormat("%Y")(date)
    }
}

onMounted(() => {
    // Define the Dutch locale
    const dutchLocale = {
        dateTime: "%A %e %B %Y %X",
        date: "%d-%m-%Y",
        time: "%H:%M:%S",
        periods: ["AM", "PM"],
        days: ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"],
        shortDays: ["zo", "ma", "di", "wo", "do", "vr", "za"],
        months: [
            "januari",
            "februari",
            "maart",
            "april",
            "mei",
            "juni",
            "juli",
            "augustus",
            "september",
            "oktober",
            "november",
            "december",
        ],
        shortMonths: ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"],
    }

    // Set up the Dutch locale in D3
    d3.timeFormatDefaultLocale(dutchLocale)

    // append the svg object to the body of the page
    const svg = d3
        .select("#svg-container")
        .append("svg")
        .attr("id", "svg-graph")
        .style("font-family", "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif")

    // Add X axis --> it is a date format
    const x = d3.scaleTime()
    const xAxis = svg.append("g").attr("class", "x-axis").style("font-size", "calc(0.5vw + 0.4rem)")

    // Add Y axis
    const y = d3.scaleLinear()
    const yAxis = svg.append("g").attr("class", "y-axis").style("font-size", "calc(0.5vw + 0.4rem)")

    // grid lines
    const yGrid = svg.append("g").attr("class", "yGrid")
    const xGrid = svg.append("g").attr("class", "xGrid")
    let globalGraphRect = undefined

    // y axis label
    svg.append("text")
        .style("text-anchor", "middle")
        .style("fill", "black")
        .attr("class", "y-axis-label")
        .style("font-size", "calc(0.5vw + 0.5rem)")

    // title
    svg.append("text")
        .attr("class", "title")
        .attr("text-anchor", "middle")
        .style("fill", "black")
        .style("font-weight", "bold")
        .style("font-size", "calc(0.5vw + 0.6rem)")

    // Add a clipPath: everything out of this area won't be drawn.
    const clip = svg.append("defs").append("svg:clipPath").attr("id", "clip").attr("class", "clip").append("svg:rect")

    // Add brushing
    const brush = d3.brushX()
    const brushEl = svg.append("g")
    const graph = svg.append("g").attr("class", "graph")

    // Add the legend
    const legend = svg.append("g").attr("class", "legend")

    // Set up the line generator
    const lineGen = d3
        .line()
        .x((d) => x(d.x))
        .y((d) => y(d.y))

    // data
    watchEffect(() => {
        if (!lastSearchSettings.value) return

        // Add Y axis label (rotated 90 vertical)
        const yAxisLabel =
            lastSearchSettings.value.frequencyType === "abs" ? "Absolute frequentie" : "Frequentie per miljoen woorden"
        svg.select(".y-axis-label").text(yAxisLabel)
        svg.select(".title").text(graphTitle.value)

        // clear the svg
        svg.selectAll(".line-group").remove()
        svg.selectAll(".legend-item").remove()

        // Sample the data to maxPoints
        const flat = visible.value.flatMap((d) => d.data[lastSearchSettings.value.frequencyType])
        // const zoomLevel = x.domain()[1] - x.domain()[0];
        // const totalPoints = flat.length;
        // const sampleRate = Math.max(1, Math.floor(totalPoints / maxPoints));
        const sampledData = visible.value
        // .map(series => ({
        //     ...series,
        //     data: {
        //         abs: flat.filter((_, index) => index % sampleRate === 0),
        //         rel: flat.filter((_, index) => index % sampleRate === 0)
        //     }
        // }));

        // first update the axes
        x.domain(d3.extent(flat, (d) => d.x))
        xAxis.call(d3.axisBottom(x).ticks(10))
        // y domain from 0 to max value
        const maxY = d3.max(flat, (d) => d.y) * 1.2
        y.domain([0, maxY])
        yAxis.call(d3.axisLeft(y))

        // add empty g for each dataseries and data-label it
        sampledData.forEach((series) => {
            graph.append("g").attr("data-name", series.uuid).attr("clip-path", "url(#clip)").attr("class", "line-group")
        })

        // Legend
        sampledData.forEach((series, i) => {
            const legendItem = legend
                .append("g")
                .attr("class", "legend-item")
                .attr("transform", `translate(0, ${i * 20})`)
            legendItem
                .append("rect")
                .attr("class", "legend-square")
                .attr("x", 0)
                .attr("y", -8)
                .attr("width", 12)
                .attr("height", 12)
                .style("fill", "#" + series.searchItem.color)
            const chnLink = constructSearchLink(series.searchItem, lastSearchSettings.value)
            legendItem
                .append("a")
                .attr("xlink:href", chnLink)
                .attr("target", "_blank")
                .append("text")
                .text(searchToString(series.searchItem))
                .style("fill", "black")
                .style("font-size", "calc(0.5vw + 0.6rem)")
                .attr("x", 20)
                .attr("y", 3)
        })

        // draw the lines
        sampledData.forEach((series) => {
            svg.select(`.line-group[data-name='${series.uuid}']`)
                .selectAll(".line")
                .data([series.data[lastSearchSettings.value.frequencyType]])
                .enter()
                .append("path")
                .attr("class", "line")
                .attr("d", (d) => lineGen(d))
                .attr("fill", "none")
                .attr("stroke", "#" + series.searchItem.color)
                .attr("stroke-width", 2)
                .style("pointer-events", "none")
        })

        // Draw the dots
        sampledData.forEach((series) => {
            if (series.data[lastSearchSettings.value.frequencyType].length > maxPoints) return
            // link data
            series.data.abs.forEach((d) => {
                d.searchItem = series.searchItem
            })
            series.data.rel.forEach((d) => {
                d.searchItem = series.searchItem
            })

            const dot = svg
                .select(`.line-group[data-name='${series.uuid}']`)
                .selectAll(".dot")
                .data(series.data[lastSearchSettings.value.frequencyType])
                .enter()
                .append("g")
                .attr("class", `dot`)
                .attr("transform", (d) => `translate(${x(d.x)}, ${y(d.y)})`)
            dot.append("circle")
                .attr("r", 4)
                .attr("fill", "#" + series.searchItem.color)
            dot.append("circle").attr("class", "hit-area").attr("r", 25).attr("fill", "transparent")
        })

        // tooltip events
        const tooltip = d3.select("#tooltip")
        const tooltipVisible = false
        let left, top

        function showTooltip(event) {
            if (tooltipVisible) return
            const tooltipWidth = tooltip.node().offsetWidth
            const tooltipHeight = tooltip.node().offsetHeight
            // The dot selected by the mouse
            const dotRect = event.target.getBoundingClientRect()
            dotRect.center = {
                x: dotRect.left + dotRect.width / 2,
                y: dotRect.top + dotRect.height / 2 + window.scrollY,
            }
            const margin = 10

            left = dotRect.center.x - tooltipWidth / 2
            top = dotRect.center.y - tooltipHeight - margin

            // if tooltip is going out of the window, then move it inside
            if (left + tooltipWidth > window.innerWidth) {
                left = window.innerWidth - tooltipWidth // right align to screen edge
            }
            if (left < window.scrollX) {
                left = window.scrollX // left align to screen edge
            }
            if (top < window.scrollY) {
                top = event.pageY + 10 // below the cursor
            }
            tooltip.style("left", left + "px").style("top", top + "px")
        }

        svg.selectAll(".hit-area")
            .on("mouseover", function (event, d) {
                if (tooltipVisible) return
                tooltip.style("visibility", "visible")
                tooltip.html(tooltipHtml(d, lastSearchSettings.value))
            })
            .on("mousemove", function (event, d) {
                showTooltip(event, d)
            })
            .on("mouseout", function () {
                if (tooltipVisible) return
                tooltip.style("visibility", "hidden")
            })
            .on("click", function (event, d) {
                // Needs to be on a timeout to prevent the same click from clicking on the link. (weird...)
                setTimeout(() => {
                    showTooltip(event, d)
                }, 400)
            })

        tooltip
            .on("mouseout", function () {
                tooltip.style("visibility", "hidden")
            })
            .on("mouseover", function () {
                tooltip.style("visibility", "visible")
            })
    })

    // A function that set idleTimeOut to null
    let idleTimeout
    function idled() {
        idleTimeout = null
    }

    // A function that update the chart for given boundaries
    function brushChart(event) {
        // What are the selected boundaries?
        const extent = event.selection

        if (!extent) {
            // If no selection, back to initial coordinate. Otherwise, update X axis domain
            if (!idleTimeout) return (idleTimeout = setTimeout(idled, 350)) // This allows to wait a little bit
            x.domain(
                d3.extent(
                    visible.value.flatMap((d) => d.data[lastSearchSettings.value.frequencyType]),
                    (d) => d.x,
                ),
            )
            zoomedIn.value = false
        } else {
            // A selection was made
            // remove the grey brush area
            brushEl.call(brush.move, null)

            // if the extent is really small, do nothing
            if (extent[0] + 20 > extent[1]) return // safely return, grey brush area is removed above
            // if the extent zooms in further than a week, do nothing
            const zoomLevel = x.domain()[1] - x.domain()[0]
            const maxZoom = 7 * 24 * 60 * 60 * 1000
            if (zoomLevel < maxZoom) return

            // otherwise, update the x domain
            x.domain([x.invert(extent[0]), x.invert(extent[1])])
            zoomedIn.value = true
        }

        // Update axis and line position
        xAxis.transition().duration(animationDuration).call(d3.axisBottom(x).tickFormat(dateFormat).ticks(10))
        const fullHeight = y.domain()[1] - y.domain()[0]
        xGrid
            .transition()
            .duration(animationDuration)
            .call(d3.axisBottom(x).tickFormat(""))
            .selectAll("g.tick line")
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", -globalGraphRect.height)
            .attr("stroke", "#00000011")

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
        visible.value.forEach((series) => {
            svg.select(`.line-group[data-name='${series.uuid}']`)
                .selectAll(".line")
                .data([series.data[lastSearchSettings.value.frequencyType]])
                .transition()
                .duration(animationDuration)
                .attr("d", (d) => lineGen(d))
            svg.select(`.line-group[data-name='${series.uuid}']`)
                .selectAll(".dot")
                .data(series.data[lastSearchSettings.value.frequencyType])
                .transition()
                .duration(animationDuration)
                .attr("transform", (d) => `translate(${x(d.x)}, ${y(d.y)})`)
        })
    }

    // If user double click, reinitialize the chart
    svg.on("dblclick", function () {
        // fake a call to updateChart
        brushChart({ selection: null })
    })

    // responsive resize
    watchEffect(() => {
        // trigger reactivity. Needed as different dataseries have different y axis label sizes.
        visible.value

        // Get the dimensions of the resizeRef div
        const { width: divWidth, height: divHeight } = resizeState.dimensions
        const margin = { top: 10, right: 10, bottom: 10, left: 0, titleBottom: 15, yAxisTitleRight: 10, legendLeft: 10 }
        // This div contains the svg. Fill it up.
        svg.attr("width", divWidth).attr("height", divHeight)

        // title
        const titleY = svg.select(".title").node().getBBox().height + margin.top
        const titleHeight = titleY + margin.titleBottom
        svg.select(".title").attr("transform", `translate(${divWidth / 2}, ${titleY})`)

        // y axis title
        const yAxisTitleX = svg.select(".y-axis-label").node().getBBox().height + margin.left
        const yAxisTitleWidth = yAxisTitleX + margin.yAxisTitleRight
        // compensate for the fact that the y axis label is rendered on the left outside of the main chart <g>
        svg.select(".y-axis-label").attr("transform", `translate(${yAxisTitleX}, ${divHeight / 2}) rotate(-90)`)

        // Set the y axis
        const xAxisHeight = xAxis.node().getBBox().height + margin.bottom
        const yAxisHeight = divHeight - titleHeight - xAxisHeight
        y.range([yAxisHeight, 0])
        yAxis.call(d3.axisLeft(y))
        // The y axis, when rendered, has a certain width. divWidth - yAxisSize will be the width of the chart (and x axis).
        const yAxisWidth = yAxis.node().getBBox().width + yAxisTitleWidth
        // compensate for the fact that the y axis is rendered on the left outside of the main chart <g>
        yAxis.attr("transform", `translate(${yAxisWidth}, ${titleHeight})`)

        // legend
        legend.attr("transform", `translate(${yAxisWidth + margin.legendLeft}, ${titleHeight})`)

        const xAxisWidth = divWidth - yAxisWidth - margin.right

        x.range([0, xAxisWidth])
        xAxis
            .attr("transform", `translate(${yAxisWidth}, ${divHeight - xAxisHeight})`)
            .call(d3.axisBottom(x).tickFormat(dateFormat).ticks(10))

        const graphRect = { width: xAxisWidth, height: yAxisHeight, x: yAxisWidth, y: titleHeight }
        globalGraphRect = graphRect
        const clipOverflow = { x: 2, y: 10 }

        graph.attr("transform", `translate(${graphRect.x}, ${graphRect.y})`)

        clip.attr("width", graphRect.width + 2 * clipOverflow.x)
            .attr("height", graphRect.height + 2 * clipOverflow.y)
            .attr("x", -clipOverflow.x)
            .attr("y", -clipOverflow.y)

        // grid lines
        yGrid
            .call(d3.axisLeft(y).tickFormat(""))
            .attr("transform", `translate(${yAxisWidth}, ${titleHeight})`)
            .selectAll("g.tick line")
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", graphRect.width)
            .attr("y2", 0)
            .attr("stroke", "#00000011")

        xGrid
            .call(d3.axisBottom(x).tickFormat(""))
            .attr("transform", `translate(${yAxisWidth}, ${divHeight - xAxisHeight})`)
            .selectAll("g.tick line")
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", -graphRect.height)
            .attr("stroke", "#00000011")

        brushEl.attr("transform", `translate(${graphRect.x}, ${graphRect.y})`)
        brush
            .extent([
                [0, 0],
                [graphRect.width, graphRect.height],
            ])
            .on("end", brushChart)
        brushEl.call(brush)
        // lines
        svg.selectAll(".line").attr("d", (d) => lineGen(d))
        // dots
        svg.selectAll(".dot").attr("transform", (d) => `translate(${x(d.x)}, ${y(d.y)})`)
    })
})

// methods for external use
function resetZoom() {
    // fake double click
    const event = new MouseEvent("dblclick", { bubbles: true, cancelable: true, view: window })
    document.getElementById("svg-graph").dispatchEvent(event)
    document.getElementById("svg-graph").dispatchEvent(event)
}
</script>

<style lang="scss">
#svg-container {
    user-select: none;
}

.legend-square {
    width: 12px;
    height: 12px;
    display: inline-block;
    margin-right: 5px;
}

.hidden-line {
    text-decoration: line-through;
}

.legend-item {
    user-select: none;
}

.overlay {
    cursor: crosshair;
}

#tooltip {
    position: absolute;
    background-color: white;
    border: 1px solid #ccc;
    padding: 5px;
    border-radius: 3px;
    pointer-events: none;
    visibility: hidden;
    z-index: 2;
    pointer-events: all;

    a {
        color: blue;
    }
}
</style>
