import logging
import os

from bln.client import Client

from . import utils

BLN_API_KEY = os.getenv("BLN_API_KEY")
BLN_PROJECT_ID = os.getenv("BLN_PROJECT_ID")

logger = logging.getLogger(__name__)


def main():
    """Download all the CSVs in the WARN Notice project on biglocalnews.org."""
    # Login to BLN.
    c = Client(BLN_API_KEY)

    # Get the Warn Act Notices project.
    p = c.search_projects(lambda x: x['name'] == 'WARN Act Notices')[0]

    # Get all the files in the project.
    file_list = [f['name'] for f in p['files']]

    # Make the download directory, if it doesn't already exist.
    if not utils.OUTPUT_DIR.exists():
        utils.OUTPUT_DIR.mkdir(parents=True)

    # Download all the files.
    for f in file_list:
        logger.debug(f"Download {f} to {utils.OUTPUT_DIR}")
        c.download_file(BLN_PROJECT_ID, f, output_dir=utils.OUTPUT_DIR)


if __name__ == "__main__":
    main()