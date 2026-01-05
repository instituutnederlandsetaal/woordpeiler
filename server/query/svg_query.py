# standard
from math import trunc
from xml.etree import ElementTree as ET

# local
from server.query.frequency_query import FrequencyQuery
from server.query.query_builder import BaseCursor


class SvgQuery:
    size = 1000
    stroke_width = size * 0.02
    margin = size * 0.05
    title_height = size * 0.1
    # subtitle_height = size / 150
    margin_hr = size * 0.025

    def __init__(self, freq: FrequencyQuery) -> None:
        self.freq = freq

    def _get_flat_line(self) -> ET.Element:
        el = ET.Element("polyline")
        el.set("stroke-width", str(self.stroke_width))
        el.set("points", f"0,{self.size} {self.size},{self.size}")
        return el

    async def _get_polyline(self, cursor: BaseCursor) -> ET.Element:
        # get the word as a regular FrequencyQuery
        data = await self.freq.build(cursor).execute_fetchall()

        if len(data) == 0:
            # no data
            return self._get_flat_line()

        # extremes for normalization
        max_freq = max([d[2] for d in data])
        min_time = data[0][0]
        max_time = data[-1][0] - min_time

        if max_freq == 0:
            # flat line
            return self._get_flat_line()

        el = ET.Element("polyline")
        el.set("stroke-width", str(self.stroke_width))
        # construct polyline points
        points = ""
        for [time, _, freq] in data:
            # normalize
            new_freq = 1 - (freq / max_freq)
            new_time = (time - min_time) / max_time
            # truncate
            new_freq = trunc(new_freq * self.size)
            new_time = trunc(new_time * self.size)
            # add to points string
            points += f"{new_time},{new_freq} "
        el.set("points", points.strip())

        # create <svg> and <polyline>
        return el

    async def plain_svg(self, cursor: BaseCursor) -> str:
        polyline = await self._get_polyline(cursor)
        svg = ET.Element("svg")
        svg.set("xmlns", "http://www.w3.org/2000/svg")
        svg.set("preserveAspectRatio", "none")
        svg.set("viewBox", f"0 0 {self.size} {self.size}")
        svg.append(polyline)
        return ET.tostring(svg, encoding="unicode")

    async def styled_svg(self, cursor: BaseCursor) -> str:
        polyline = await self._get_polyline(cursor)
        polyline.set("fill", "none")
        polyline.set("stroke", "#000000")
        line_y_scale = 1 - (
            (self.title_height + self.margin_hr * 2 + self.margin) / self.size
        )
        line_x_scale = 1 - ((self.margin * 2) / self.size)
        polyline.set("transform", f"scale({line_x_scale},{line_y_scale})")
        # create a yellow square with a title and the polyline
        rect = ET.Element("rect")
        rect.set("width", str(self.size))
        rect.set("height", str(self.size))
        rect.set("fill", "#FFF064")

        title = ET.Element("title")
        title.text = f"Woordpeiler - {self.freq.wordform}"

        # Add a header above the graph
        header = ET.Element("text")
        header.set("x", str(self.margin))
        header.set("y", str(self.title_height))
        header.set("fill", "#000000")
        header.set(
            "font-family", "Schoolboek, Helvetica Neue, Helvetica, Arial, sans-serif"
        )
        header.set("font-size", "64px")
        header.text = self.freq.wordform

        # add a <hr> like line below the header
        hr = ET.Element("line")
        hr_x = self.title_height + self.margin_hr
        hr.set("x1", str(self.margin))
        hr.set("y1", str(hr_x))
        hr.set("x2", str(self.size - self.margin))
        hr.set("y2", str(hr_x))
        hr.set("stroke", "#000000")
        hr.set("stroke-width", "3")

        svg = ET.Element("svg")
        svg.set("xmlns", "http://www.w3.org/2000/svg")
        svg.set("viewBox", f"0 0 {self.size} {self.size}")
        svg.append(
            title
        )  # Note: title should be first child for compatibility with SVG 1.1
        svg.append(rect)
        svg.append(header)
        svg.append(hr)
        # create some margin
        g = ET.Element("g")
        g_y = self.title_height + (self.margin_hr * 2)
        g.set("transform", f"translate({self.margin},{g_y})")
        g.append(polyline)
        svg.append(g)

        return ET.tostring(svg, encoding="unicode")
