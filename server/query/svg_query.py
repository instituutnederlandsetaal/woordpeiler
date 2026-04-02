from math import trunc
from xml.etree import ElementTree as ET

from server.query.frequency_query import FrequencyQuery
from server.query.query_builder import BaseCursor


class SvgQuery:
    def __init__(
        self,
        freq: FrequencyQuery,
        color: str = "FFF064",
        width: int = 960,
        height: int = 720,
    ) -> None:
        self.freq = freq
        self.color = color
        self.width = width
        self.height = height
        self.margin_x = self.width * 0.075
        self.stroke_width = self.height / 180
        self.title_y = self.height * 0.15
        self.hr_y = self.height * 0.19
        self.subtitle_y = self.height * 0.25
        self.graph_y = self.height * 0.3
        self.title_font = self.height / 12
        self.subtitle_font = self.height / 24

    def _get_flat_line(self) -> ET.Element:
        el = ET.Element("polyline")
        el.set("stroke-width", str(self.stroke_width))
        el.set("points", f"0,{self.height} {self.width},{self.height}")
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

    def _get_title(self) -> ET.Element:
        return ET.XML(f"<title>Woordpeiler - {self.freq.wordform}</title>")

    def _get_colored_rect(self) -> ET.Element:
        return ET.XML(f"<rect width='100%' height='100%' fill='#{self.color}'/>")

    def _get_hr_line(self) -> ET.Element:
        return ET.XML(
            f"<line y1='{self.hr_y}' x1='{self.margin_x}' y2='{self.hr_y}' x2='{self.width - self.margin_x}' stroke='black' stroke-width='{self.stroke_width / 2}'/>",
        )

    def _get_svg(self) -> ET.Element:
        svg = ET.Element("svg")
        svg.set("xmlns", "http://www.w3.org/2000/svg")
        svg.set("viewBox", f"0 0 {self.width} {self.height}")
        return svg

    def _get_header(self) -> ET.Element:
        return ET.XML(
            f"<text x='{self.margin_x}' y='{self.title_y}' font-family='Schoolboek, Helvetica Neue, Helvetica, Arial, sans-serif' font-size='{self.title_font}'>{self.freq.wordform}</text>",
        )

    def _get_subtitle(self) -> ET.Element:
        return ET.XML(
            f"<text x='{self.margin_x}' y='{self.subtitle_y}' font-family='Schoolboek, Helvetica Neue, Helvetica, Arial, sans-serif' font-size='{self.subtitle_font}'>sinds {self.freq.start.year}</text>",
        )

    async def _get_graph(self, cursor: BaseCursor) -> ET.Element:
        polyline = await self._get_polyline(cursor)
        polyline.set("fill", "none")
        polyline.set("stroke", "black")
        polyline.set("transform", "scale(0.85,0.65)")
        g = ET.Element("g")
        g.set("transform", f"translate({self.margin_x},{self.graph_y})")
        g.append(polyline)
        return g

    async def plain_svg(self, cursor: BaseCursor) -> str:
        polyline = await self._get_polyline(cursor)
        svg = ET.Element("svg")
        svg.set("xmlns", "http://www.w3.org/2000/svg")
        svg.set("preserveAspectRatio", "none")
        svg.set("viewBox", f"0 0 {self.width} {self.height}")
        svg.append(polyline)
        return ET.tostring(svg, encoding="unicode")

    async def styled_svg(self, cursor: BaseCursor) -> str:
        svg = self._get_svg()
        # <title> should be first for SVG 1.1 compatibility
        svg.append(self._get_title())
        # Order matters: from background (rect) to foreground
        svg.append(self._get_colored_rect())
        svg.append(self._get_header())
        svg.append(self._get_hr_line())
        svg.append(self._get_subtitle())
        svg.append(await self._get_graph(cursor))
        return ET.tostring(svg, encoding="unicode")
