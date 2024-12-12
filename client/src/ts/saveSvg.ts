import * as d3 from "d3";
import { saveAs } from 'file-saver';

export function download(resizeState) {
    var svgString = getSVGString(d3.select("#svg-graph").node());
    let { width, height } = resizeState.dimensions;
    svgString2Image(svgString, width + 20, height + 20, 'png', save); // passes Blob and filesize String to the callback

    function save(dataBlob, filesize) {
        saveAs(dataBlob, 'corpustrends.png'); // FileSaver.js function
    }
}

export function share(resizeState) {
    var svgString = getSVGString(d3.select("#svg-graph").node());
    let { width, height } = resizeState.dimensions;
    svgString2Image(svgString, width + 20, height + 20, 'png', save); // passes Blob and filesize String to the callback

    function save(dataBlob, filesize) {
        const file = new File([dataBlob], 'corpustrends.png', { type: 'image/png' });
        navigator.share({
            files: [file]
        });
    }
}

function getSVGString(svgNode) {
    svgNode.setAttribute('xlink', 'http://www.w3.org/1999/xlink');
    var cssStyleText = getCSSStyles(svgNode);
    appendCSS(cssStyleText, svgNode);

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
        context.drawImage(image, 0, 0, width, height);

        { // Add watermark
            type CanvasText = {
                text: string;
                fontSize: number;
                color: string;
                marginTop: number;
            }

            const title: CanvasText = { text: "corpustrends.ivdnt.org", fontSize: 20, color: "black", marginTop: 40 }
            const subtitle: CanvasText = { text: "/instituut voor de Nederlandse taal/", fontSize: 15, color: "black", marginTop: 20 }
            const marginRight = 10;

            for (const { text, fontSize, color, marginTop } of [title, subtitle]) {
                context.textAlign = "right";
                context.font = `${fontSize}px Arial`;
                context.fillStyle = color;
                context.fillText(text, width - marginRight, marginTop);
            }
        }

        canvas.toBlob(function (blob) {
            var filesize = Math.round(blob.length / 1024) + ' KB';
            if (callback) callback(blob, filesize);
        });


    };
    image.src = imgsrc;
}
