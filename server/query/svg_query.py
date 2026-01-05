# standard
from math import trunc
from xml.etree import ElementTree as ET

# local
from server.query.frequency_query import FrequencyQuery
from server.query.query_builder import BaseCursor


class SvgQuery:

    def __init__(
        self,
        freq: FrequencyQuery,
        bg_color: str = "FFF064",
        width: int = 1000,
        height: int = 1000,
    ) -> None:
        self.freq = freq
        self.bg_color = bg_color
        self.width = width
        self.height = height
        self.stroke_width = height * 0.005
        self.margin = height * 0.05
        self.title_font = height * 0.064
        self.subtitle_font = height * 0.028
        self.title_height = height * 0.075
        self.subtitle_height = height * 0.05
        self.margin_hr = height * 0.025

    def _get_flat_line(self) -> ET.Element:
        el = ET.Element("polyline")
        el.set("stroke-width", str(self.stroke_width))
        el.set("points", f"0,{self.height} {self.height},{self.height}")
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
            new_freq = trunc(new_freq * self.height)
            new_time = trunc(new_time * self.width)
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
        svg.set("viewBox", f"0 0 {self.width} {self.height}")
        svg.append(polyline)
        return ET.tostring(svg, encoding="unicode")

    async def styled_svg(self, cursor: BaseCursor) -> str:
        polyline = await self._get_polyline(cursor)
        polyline.set("fill", "none")
        polyline.set("stroke", "#000000")
        line_y_scale = 1 - (
            (
                self.title_height
                + self.margin_hr * 2
                + self.margin
                + self.subtitle_height
            )
            / self.height
        )
        line_x_scale = 1 - ((self.margin * 2) / self.width)
        polyline.set("transform", f"scale({line_x_scale},{line_y_scale})")
        # create a yellow square with a title and the polyline
        rect = ET.Element("rect")
        rect.set("width", "100%")
        rect.set("height", "100%")
        rect.set("fill", f"#{self.bg_color}")

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
        header.set("font-size", f"{self.title_font}px")
        header.text = self.freq.wordform

        # add a <hr> like line below the header
        hr = ET.Element("line")
        hr_x = self.title_height + self.margin_hr
        hr.set("x1", str(self.margin))
        hr.set("y1", str(hr_x))
        hr.set("x2", str(self.width - self.margin))
        hr.set("y2", str(hr_x))
        hr.set("stroke", "#000000")
        hr.set("stroke-width", str(self.stroke_width / 2))

        # add subtitle below the hr
        subtitle = ET.Element("text")
        subtitle.set("x", str(self.margin))
        subtitle.set("y", str(hr_x + self.subtitle_height))
        subtitle.set("fill", "#000000")
        subtitle.set(
            "font-family", "Schoolboek, Helvetica Neue, Helvetica, Arial, sans-serif"
        )
        subtitle.set("font-size", f"{self.subtitle_font}px")
        subtitle.text = f"sinds {self.freq.start.year}"

        svg = ET.Element("svg")
        svg.set("xmlns", "http://www.w3.org/2000/svg")
        svg.set("viewBox", f"0 0 {self.width} {self.height}")
        svg.append(
            title
        )  # Note: title should be first child for compatibility with SVG 1.1
        svg.append(rect)
        svg.append(header)
        svg.append(hr)
        svg.append(subtitle)
        # create some margin
        g = ET.Element("g")
        g_y = self.title_height + (self.margin_hr * 2) + self.subtitle_height
        g.set("transform", f"translate({self.margin},{g_y})")
        g.append(polyline)
        svg.append(g)

        return ET.tostring(svg, encoding="unicode")
