const getOrCreateTooltip = (chart) => {
    let tooltipEl = chart.canvas.parentNode.querySelector('div');

    if (!tooltipEl) {
        tooltipEl = document.createElement('div');
        tooltipEl.style.background = 'rgba(0, 0, 0, 0.7)';
        tooltipEl.style.borderRadius = '3px';
        tooltipEl.style.color = 'white';
        tooltipEl.style.opacity = 1;
        tooltipEl.style.pointerEvents = 'all !important';
        tooltipEl.style.position = 'absolute';
        tooltipEl.style.transform = 'translate(-50%, 0)';
        tooltipEl.style.transition = 'all .1s ease';

        tooltipEl.className = 'tooltip';

        const table = document.createElement('table');
        table.style.margin = '0px';

        tooltipEl.appendChild(table);
        chart.canvas.parentNode.appendChild(tooltipEl);
    }

    return tooltipEl;
};

export const externalTooltipHandler = (context) => {
    // Tooltip Element
    const { chart, tooltip } = context;
    const tooltipEl = getOrCreateTooltip(chart);

    // if (!tooltipEl) {
    //     tooltipEl = document.createElement('div');
    //     tooltipEl.id = 'chartjs-tooltip';
    //     tooltipEl.innerHTML = `<table></table>`;
    //     document.body.appendChild(tooltipEl);

    //     // tooltipEl.addEventListener('mouseleave', () => {
    //     //     tooltipEl.style.opacity = 0;
    //     // });
    //     tooltipEl.addEventListener('mouseenter', () => {
    //         tooltipEl.style.opacity = 1;
    //     });
    // }
    tooltipEl.addEventListener('mouseout', () => {
        tooltipEl.style.opacity = 0
    })

    tooltipEl.addEventListener('mouseover', () => {

        tooltipEl.style.opacity = 0.7
    })

    // Hide if no tooltip
    // if (tooltip.opacity === 0) {
    //     tooltipEl.style.opacity = 0;
    //     return;
    // }

    // Set Text
    if (tooltip.body) {
        const titleLines = tooltip.title || [];
        const bodyLines = tooltip.body.map(b => b.lines);

        const tableHead = document.createElement('thead');
        let aTitle = null
        titleLines.forEach(title => {
            aTitle = title
            const tr = document.createElement('tr');
            tr.style.borderWidth = 0;

            const th = document.createElement('th');
            th.style.borderWidth = 0;
            const text = document.createTextNode(title);

            th.appendChild(text);
            tr.appendChild(th);
            tableHead.appendChild(tr);
        });

        const tableBody = document.createElement('tbody');
        bodyLines.forEach((body, i) => {
            const colors = tooltip.labelColors[i];

            const span = document.createElement('span');
            span.style.background = colors.backgroundColor;
            span.style.borderColor = colors.borderColor;
            span.style.borderWidth = '2px';
            span.style.marginRight = '10px';
            span.style.height = '10px';
            span.style.width = '10px';
            span.style.display = 'inline-block';

            const tr = document.createElement('tr');
            tr.style.backgroundColor = 'inherit';
            tr.style.borderWidth = 0;

            const td = document.createElement('td');
            td.style.borderWidth = 0;

            const link = document.createElement("a")
            const word = body.toString().split(":")[0]
            const dateSplit = aTitle.split("-")
            const date = dateSplit[2] + dateSplit[1] + dateSplit[0]
            link.href = "https://portal.clarin.ivdnt.org/corpus-frontend-chn/chn-extern/search/hits?patt=" + encodeURIComponent(`[word="${word}"]`) + "&filter=" + encodeURIComponent(`medium:newspaper AND witnessYear_from:${dateSplit[2]} AND witnessMonth_from:${dateSplit[1]} AND witnessDay_from:${dateSplit[0]}`)
            link.target = "_blank"
            link.innerHTML = body

            td.appendChild(span);
            td.appendChild(link);
            tr.appendChild(td);
            tableBody.appendChild(tr);
        });

        const tableRoot = tooltipEl.querySelector('table');

        // Remove old children
        while (tableRoot.firstChild) {
            tableRoot.firstChild.remove();
        }

        // Add new children
        tableRoot.appendChild(tableHead);
        tableRoot.appendChild(tableBody);
    }

    const { offsetLeft: positionX, offsetTop: positionY } = chart.canvas;

    // Display, position, and set s+tyles for font
    tooltipEl.style.opacity = 1;
    tooltipEl.style.left = positionX + tooltip.caretX + 'px';
    tooltipEl.style.top = positionY + tooltip.caretY + 'px';
    tooltipEl.style.font = tooltip.options.bodyFont.string;
    tooltipEl.style.padding = tooltip.options.padding + 'px ' + tooltip.options.padding + 'px';
};