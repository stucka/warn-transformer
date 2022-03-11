import typing
from datetime import datetime

from ..schema import BaseTransformer


class Transformer(BaseTransformer):
    """Transform Louisiana raw data for consolidation."""

    postal_code = "LA"
    fields = dict(
        company="Company Name",
        location="Location",
        notice_date="Notice Date",
        effective_date="Layoff Date",
        jobs="Employees Affected",
    )
    date_format = ["%m/%d/%Y", "%m/%d/%y"]
    date_corrections = {
        "6/31/09": datetime(2009, 6, 30),
        "N/A": None,
        "5/1820": datetime(2020, 5, 18),
    }
    jobs_corrections = {
        "700 *exact number pending relocation to other departments": 700,
        "50-297": 50,
        "426 426": 426,
        "1 Multi-state notification- Louisiana total =1": 1,
        "48 by 8/28/2015 closure by 12/2015": 48,
        "60-70": 60,
        "8 +1": 9,
        "385 465": 385,
        "114 +112": 226,
        "227 -8": 227,
        "32 +1": 32,
        "167 100": 167,
        "4 +55": 59,
        "150 +50": 200,
        "NA": None,
        "161 +1": 162,
        "23 15 41 4": 23,
        "70 +2": 72,
        "30 +5 +4 +1 +3": 43,
        "420 405 369": 420,
        "n/a": None,
        "74 +1 +21": 96,
        "84 -4 +10": 98,
        "1*": 1,
    }

    def transform_date(self, value: str) -> typing.Optional[str]:
        """Transform a raw date string into a date object.

        Args:
            value (str): The raw date string provided by the source

        Returns: A date object ready for consolidation. Or, if the date string is invalid, a None.
        """
        # Try corrections before we edit the string
        try:
            dt = self.date_corrections[value]
            if dt:
                return str(dt.date())
            else:
                assert dt is None
                return dt
        except KeyError:
            pass

        # A little custom clean up based on the weird stuff from this source
        value = value.replace("starting", "")
        value = value.strip().split(" and ")[0].strip()
        value = value.strip().split(" to ")[0].strip()
        value = value.strip().split(" - ")[0].strip()
        value = value.strip().split(" & ")[0].strip()
        value = value.strip().split(" – ")[0].strip()
        value = value.strip().split("-")[0].strip()
        value = value.strip().split()[0].strip()

        # The same old stuff
        return super().transform_date(value)
