# standard
from math import trunc

from server.query.frequency_query import FrequencyQuery

# local
from server.query.query_builder import BaseCursor


class SvgQuery:
    def __init__(self, freq: FrequencyQuery) -> None:
        self.freq = freq

    async def execute(self, cursor: BaseCursor) -> str:
        # get the word as a regular FrequencyQuery
        data = await self.freq.build(cursor).execute_fetchall()
        SIZE = 1000
        STROKE = SIZE / 200

        flat_line = f"<svg xmlns='http://www.w3.org/2000/svg' preserveAspectRatio='none' viewBox='0 0 {SIZE} {SIZE}'><polyline stroke-width='{STROKE}' points='0,{SIZE} {SIZE},{SIZE}'/></svg>"

        if len(data) == 0:
            # no data
            return flat_line

        # extremes for normalization
        max_freq = max([d[2] for d in data])
        min_time = data[0][0]
        max_time = data[-1][0] - min_time

        if max_freq == 0:
            # flat line
            return flat_line

        # construct polyline points
        points = ""
        for [time, _, freq] in data:
            # normalize
            new_freq = 1 - (freq / max_freq)
            new_time = (time - min_time) / max_time
            # truncate
            new_freq = trunc(new_freq * SIZE)
            new_time = trunc(new_time * SIZE)
            # add to points string
            points += f"{new_time},{new_freq} "

        # create <svg> and <polyline>
        return f"<svg xmlns='http://www.w3.org/2000/svg' preserveAspectRatio='none' viewBox='0 0 {SIZE} {SIZE}'><polyline stroke-width='{STROKE}' points='{points}'/></svg>"
