import csv
from datetime import datetime
import hashlib
import json
import logging
from pathlib import Path
import typing

from marshmallow import Schema, fields

logger = logging.getLogger(__name__)


class WarnNoticeSchema(Schema):
    """An standardized instance of a WARN Act Notice."""

    hash_id = fields.Str(required=True)
    postal_code = fields.Str(max_length=2, required=True)
    company = fields.Str(required=True)
    location = fields.Str(required=True, allow_none=True)
    date = fields.Date(required=True)
    jobs = fields.Int(required=True, allow_none=True)


class BaseTransformer:
    """Transform a state's raw data for consolidation."""

    schema = WarnNoticeSchema

    # The base attributes that need to be defined on all subclasses.
    postal_code: str = "xx"
    fields: typing.Dict = dict()

    # The default date format. It will need to be customized by source.
    date_format: str = "%m/%d/%Y"
    # Manual date corrections for malformed data
    date_corrections: typing.Dict = {}

    def __init__(self, input_dir: Path):
        """Intialize a new instance.

        Args:
            input_dir (Path): A directory where our raw data is stored
        """
        self.input_dir = input_dir
        self.raw_data = self.get_raw_data()

    def get_raw_data(self) -> typing.List[typing.Dict]:
        """Get the raw data from our scraper for this source.

        Returns: A list of raw rows of data from the source.
        """
        # Get downloaded file
        raw_path = (
            self.input_dir / f"{self.postal_code.lower()}.csv"
        )
        # Open the csv
        with open(raw_path) as fh:
            reader = csv.DictReader(fh)
            # Return it as a list
            return list(reader)

    def transform(self) -> typing.List[typing.Dict]:
        """Transform prepared rows into a form that's ready for consolidation.

        Returns: A validated list of dictionaries that conform to our schema
        """
        logger.debug(f"Transforming {self.postal_code}")

        # Prep the row list for transformation
        row_list = self.prep_row_list(self.raw_data)

        # Transform the row list into dicts that are ready to be submitted for validation
        transformed_list = [self.transform_row(r) for r in row_list]

        # Validate the row list against our schema
        validated_list = [self.schema().load(r) for r in transformed_list]

        # Return the result, which should be ready for consolidation
        return validated_list

    def prep_row_list(
        self, row_list: typing.List[typing.Dict]
    ) -> typing.List[typing.Dict]:
        """Make necessary transformations to the raw row list prior to transformation.

        Args:
            row_list (list): A list of raw rows of data from the source.

        Returns: The row list minus empty records
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

    def transform_row(self, row: typing.Dict) -> typing.Dict:
        """Transform a row into a form that's ready for consolidation.

        Args:
            row (dict): One raw row of data from the source

        Returns: A transformed dict that's ready to be loaded into our consolidated schema.
        """
        return dict(
            hash_id=self.get_hash_id(row),
            postal_code=self.postal_code.upper(),
            company=self.transform_company(row[self.fields["company"]]),
            location=self.transform_location(row[self.fields["location"]]),
            date=self.transform_date(row[self.fields["date"]]),
            jobs=self.transform_jobs(row[self.fields["jobs"]]),
        )

    def get_hash_id(self, row: typing.Dict) -> str:
        """Convert the row into a unique hexdigest to use as a unique identifier.

        Args:
            row (dict): One raw row of data from the source

        Returns: A unique hexdigest string computed from the source data.
        """
        row_string = json.dumps(row)
        hash_obj = hashlib.sha224(row_string.encode("utf-8"))
        return hash_obj.hexdigest()

    def transform_company(self, value: str) -> str:
        """Transform a raw company name.

        Args:
            value (str): The raw company string provided by the source

        Returns: A string object ready for consolidation.
        """
        return value.strip()

    def transform_location(self, value: str) -> str:
        """Transform a raw location.

        Args:
            value (str): The raw location string provided by the source

        Returns: A string object ready for consolidation.
        """
        return value.strip()

    def transform_date(self, value: str) -> str:
        """Transform a raw date string into a date object.

        Args:
            value (str): The raw date string provided by the source

        Returns: A date object ready for consolidation. Or, if the date string is invalid, a None.
        """
        value = value.strip()
        try:
            dt = datetime.strptime(value, self.date_format)
        except ValueError:
            logger.debug(f"Could not parse {value}. Looking up correction")
            dt = self.date_corrections[value]
        return str(dt.date())

    def transform_jobs(self, value: str) -> typing.Optional[int]:
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
