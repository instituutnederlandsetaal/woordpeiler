import * as d3 from "d3";
import { saveAs } from 'file-saver';

// Space for title and subtitle
const titleMargin = 18

export function download(resizeState) {
    var svgString = getSVGString(d3.select("#svg-graph").node());
    let { width, height } = resizeState.dimensions;
    svgString2Image(svgString, width, height + titleMargin, 'png', save); // passes Blob and filesize String to the callback

    function save(dataBlob, filesize) {
        saveAs(dataBlob, 'woordpeiler.png'); // FileSaver.js function
    }
}

export function share(resizeState) {
    const dummyFile = new File([new Blob([], { type: 'text/png' })], 'woordpeiler.png', { type: 'image/png' })
    // can we share a image/png?
    if (!navigator.canShare || !navigator.canShare({ files: [dummyFile] })) {
        // fallback to url share
        const url = window.location.href;
        navigator.share({
            title: "Woordpeiler",
            text: `Bekijk deze grafiek van Woordpeiler op ${url}`,
            // url: url
        });
    }

    // share the image
    var svgString = getSVGString(d3.select("#svg-graph").node());
    let { width, height } = resizeState.dimensions;
    svgString2Image(svgString, width + 20, height + 20, 'png', save); // passes Blob and filesize String to the callback

    function save(dataBlob, filesize) {
        const file = new File([dataBlob], 'woordpeiler.png', { type: 'image/png' });
        navigator.share({
            files: [file]
        });
    }
}

function getSVGString(svgNode) {
    svgNode.setAttribute('xlink', 'http://www.w3.org/1999/xlink');
    // var cssStyleText = getCSSStyles(svgNode);
    // appendCSS(cssStyleText, svgNode);

    var serializer = new XMLSerializer();
    var svgString = serializer.serializeToString(svgNode);
    svgString = svgString.replace(/(\w+)?:?xlink=/g, 'xmlns:xlink='); // Fix root xlink without namespace
    svgString = svgString.replace(/NS\d+:href/g, 'xlink:href'); // Safari NS namespace fix

    return svgString;

    function getCSSStyles(parentElement) {
        var selectorTextArr = [];

        // Add Parent element Id and Classes to the list
        selectorTextArr.push('#' + parentElement.id);
        for (var c = 0; c < parentElement.classList.length; c++)
            if (!contains('.' + parentElement.classList[c], selectorTextArr))
                selectorTextArr.push('.' + parentElement.classList[c]);

        // Add Children element Ids and Classes to the list
        var nodes = parentElement.getElementsByTagName("*");
        for (var i = 0; i < nodes.length; i++) {
            var id = nodes[i].id;
            if (!contains('#' + id, selectorTextArr))
                selectorTextArr.push('#' + id);

            var classes = nodes[i].classList;
            for (var c = 0; c < classes.length; c++)
                if (!contains('.' + classes[c], selectorTextArr))
                    selectorTextArr.push('.' + classes[c]);
        }

        // Extract CSS Rules
        var extractedCSSText = "";
        for (var i = 0; i < document.styleSheets.length; i++) {
            var s = document.styleSheets[i];

            try {
                if (!s.cssRules) continue;
            } catch (e) {
                if (e.name !== 'SecurityError') throw e; // for Firefox
                continue;
            }

            var cssRules = s.cssRules;
            for (var r = 0; r < cssRules.length; r++) {
                if (contains(cssRules[r].selectorText, selectorTextArr))
                    extractedCSSText += cssRules[r].cssText;
            }
        }


        return extractedCSSText;

        function contains(str, arr) {
            return arr.indexOf(str) === -1 ? false : true;
        }

    }

    function appendCSS(cssText, element) {
        var styleElement = document.createElement("style");
        styleElement.setAttribute("type", "text/css");
        styleElement.innerHTML = cssText;
        var refNode = element.hasChildNodes() ? element.children[0] : null;
        element.insertBefore(styleElement, refNode);
    }
}


function svgString2Image(svgString, width, height, format, callback) {
    var format = format ? format : 'png';

    var imgsrc = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString))); // Convert SVG string to data URL

    var canvas = document.createElement("canvas");
    var context = canvas.getContext("2d") as CanvasRenderingContext2D;

    canvas.width = width;
    canvas.height = height;

    var image = new Image();
    image.onload = function () {
        context.clearRect(0, 0, width, height);
        // White background, otherwise it's transparent
        context.fillStyle = "white";
        context.fillRect(0, 0, width, height);
        context.drawImage(image, 0, 0, width, height - titleMargin);

        { // Add watermark
            type CanvasText = {
                text: string;
                align: string;
                baseline: string;
                fontSize: number;
                color: string;
                x: number;
                y: number;
            }

            const title: CanvasText = {
                text: "woordpeiler.ivdnt.org",
                align: "left",
                baseline: "bottom",
                fontSize: titleMargin - 4,
                color: "black",
                x: 5,
                y: height,
            }
            const subtitle: CanvasText = {
                text: "/instituut voor de Nederlandse taal/",
                align: "right",
                baseline: "bottom",
                fontSize: titleMargin - 4,
                color: "black",
                x: width - 5,
                y: height,
            }

            for (const { text, align, baseline, fontSize, color, x, y } of [title, subtitle]) {
                context.textAlign = align;
                context.textBaseline = baseline;
                context.font = `calc(0.5vw + 0.6rem) 'Helvetica Neue', Helvetica, Arial, sans-serif`;
                context.fillStyle = color;
                context.fillText(text, x, y);
            }
        }

        canvas.toBlob(function (blob) {
            var filesize = Math.round(blob.length / 1024) + ' KB';
            if (callback) callback(blob, filesize);
        });
    };
    image.src = imgsrc;
}
