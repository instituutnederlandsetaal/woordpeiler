// Libraries
import * as d3 from "d3"
// Types
import type { ResizeState } from "@/ts/resizeObserver"
// Utils
import { config } from "@/main"

function getSVGString(width, height, w, h) {
    const svgNode = d3.select("#svg-graph").node()
    let svgString = new XMLSerializer().serializeToString(svgNode)
    const ratio = w / width
    // scaling
    svgString = svgString.replace(
        /<svg[^>]*>/,
        `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="font-size:${ratio}rem !important; font-family:'Helvetica Neue', 'Helvetica', 'Arial', sans-serif !important">`,
    )

    return svgString
}

// Space for title and subtitle
const titleMargin = 50

export function svgString2Image(resizeState: ResizeState, callback: (dataBlob: Blob, filesize: string) => void) {
    // original dimensions
    const { width: orgWidth, height: orgHeight } = resizeState.dimensions
    // scale so width is constant and height in proportion
    const TARGET_WIDTH = 1400
    const scale = TARGET_WIDTH / orgWidth
    const width = orgWidth * scale
    const height = orgHeight * scale
    const svgString = getSVGString(width, height, orgWidth, orgHeight)

    const imgsrc = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgString))) // Convert SVG string to data URL

    const canvas = document.createElement("canvas")
    const context = canvas.getContext("2d") as CanvasRenderingContext2D

    canvas.width = width
    canvas.height = height

    const image = new Image()
    image.onload = function () {
        context.clearRect(0, 0, width, height)
        // White background, otherwise it's transparent
        context.fillStyle = "white"
        context.fillRect(0, 0, width, height)

        {
            // Add watermark
            type CanvasText = {
                text: string
                align: string
                baseline: string
                fontSize: number
                color: string
                x: number
                y: number
            }

            const baseText: CanvasText = {
                baseline: "bottom",
                fontSize: (height / 1080) * 2.2, // 2.2rem at 1080p
                color: "black",
                y: height,
            }

            const date = new Date().toLocaleDateString()

            const title: CanvasText = {
                ...baseText,
                text: `woordpeiler.ivdnt.org ${date}`,
                align: "left",
                x: 5,
                y: height - 10,
            }
            const subtitle: CanvasText = {
                ...baseText,
                text: "/instituut voor de Nederlandse taal/",
                align: "right",
                y: height - 10,
                x: width - 5,
            }
            const largeWatermark: CanvasText = {
                ...baseText,
                text: "/ instituut voor de Nederlandse taal /",
                color: "rgba(0, 0, 0, 0.1)",
                align: "center",
                x: width / 2,
                y: height / 2,
                fontSize: (height / 1080) * 4, // 10rem at 1080p
            }

            // only draw largeWatermark externally
            const textToDraw = [title, subtitle]
            if (!config.internal) {
                textToDraw.push(largeWatermark)
            }

            for (const { text, align, baseline, fontSize, color, x, y } of textToDraw) {
                context.textAlign = align
                context.textBaseline = baseline
                context.font = `${fontSize}rem 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif`
                context.fillStyle = color
                context.fillText(text, x, y)
            }
        }

        // Draw image
        context.drawImage(image, 0, 0, width, height - titleMargin)

        canvas.toBlob(function (blob) {
            const filesize = Math.round(blob.length / 1024) + " KB"
            if (callback) callback(blob, filesize)
        })
    }
    image.src = imgsrc
}
