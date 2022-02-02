import csv
from datetime import datetime

from marshmallow import Schema, fields

from . import utils


class WarnNoticeSchema(Schema):
    """An standardized instance of a WARN Act Notice."""

    postal_code = fields.Str(max_length=2, required=True)
    company = fields.Str(required=True)
    date = fields.Date(allow_none=True)
    jobs = fields.Int(required=True, allow_none=True)


class BaseTransformer:
    """Transform a state's raw data for consolidation."""

    date_format = (
        "%m/%d/%Y"  # The default date format. It will need to be customized by source.
    )

    def __init__(self):
        """Intialize a new instance."""
        self.raw_data = self.get_raw_data()

    def get_raw_data(self):
        """Get the raw data from our scraper for this source.

        Returns a list of dictionaries.
        """
        # Get downloaded file
        raw_path = utils.OUTPUT_DIR / "raw" / f"{self.postal_code.lower()}.csv"
        # Open the csv
        with open(raw_path) as fh:
            reader = csv.DictReader(fh)
            # Return it as a list
            return list(reader)

    def transform(self):
        """Transform prepared rows into a form that's ready for consolidation."""
        row_list = self.prep_row_list(self.raw_data)
        return [self.transform_row(r) for r in row_list]

    def prep_row_list(self, row_list):
        """Make necessary transformations to the raw row list prior to transformation.

        Useful for filtering out empty rows.
        """
        prepped_list = []
        for row in row_list:
            # Skip empty rows
            try:
                # A list with only empty cell will throw an error
                next(v for v in row.values() if v.strip())
            except StopIteration:
                continue
            prepped_list.append(row)
        return prepped_list

    def transform_row(self, row):
        """Transform a row into a form that's ready for consolidation.

        Args:
            row (dict): One raw row of data from the source

        Returns: A transformed dict that's ready to be loaded into our consolidated schema.
        """
        return dict(
            postal_code=self.postal_code.upper(),
            company=self.transform_company(row[self.fields["company"]]),
            date=self.transform_date(row[self.fields["date"]]),
            jobs=self.transform_jobs(row[self.fields["jobs"]]),
        )

    def transform_company(self, value):
        """Transform a raw company name.

        Args:
            value (str): The raw company string provided by the source

        Returns: A string object ready for consolidation.
        """
        return value.strip()

    def transform_date(self, value):
        """Transform a raw date string into a date object.

        Args:
            value (str): The raw date string provided by the source

        Returns: A date object ready for consolidation. Or, if the date string is invalid, a None.
        """
        value = value.strip()
        try:
            dt = datetime.strptime(value, self.date_format)
        except ValueError:
            return None
        return str(dt.date())

    def transform_jobs(self, value):
        """Transform a raw jobs number into an integer.

        Args:
            value (str): A raw jobs number provided by the source

        Returns: An integer number ready for consolidation. Or, if the value is invalid, a None.
        """
        value = value.strip()
        try:
            return int(value)
        except ValueError:
            return None