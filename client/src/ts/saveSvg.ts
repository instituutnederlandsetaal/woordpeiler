import * as d3 from "d3";
import { saveAs } from 'file-saver';

// Space for title and subtitle
const titleMargin = 30

export function download(resizeState) {
    const { width, height } = resizeState.dimensions;
    // scale so width is constant and height in proportion
    const scale = 1400 / width;
    const imgwidth = width * scale;
    const imgheight = height * scale;
    var svgString = getSVGString(d3.select("#svg-graph").node(), imgwidth, imgheight, width, height);
    svgString2Image(svgString, imgwidth, imgheight, 'png', save); // passes Blob and filesize String to the callback

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

function getSVGString(svgNode, width, height, w, h) {
    var svgString = new XMLSerializer().serializeToString(svgNode);
    const ratio = w / width;
    // scaling
    svgString = svgString.replace(/<svg[^>]*>/, `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="font-size:${ratio}rem !important;font-family:'Helvetica Neue', 'Helvetica', 'Arial', sans-serif !important;">`);

    return svgString;
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
                context.font = `26px 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif`;
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
