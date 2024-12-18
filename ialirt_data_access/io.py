import contextlib
import json
import logging
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import ialirt_data_access

logger = logging.getLogger(__name__)


class IALIRTDataAccessError(Exception):
    """Base class for exceptions in this module."""

    pass

@contextlib.contextmanager
def _get_url_response(request: urllib.request.Request):
    """Get the response from a URL request.

    This is a helper function to make it easier to handle
    the different types of errors that can occur when
    opening a URL and write out the response body.
    """
    try:
        # Open the URL and yield the response
        with urllib.request.urlopen(request) as response:
            yield response

    except HTTPError as e:
        message = (
            f"HTTP Error: {e.code} - {e.reason}\n"
            f"Server Message: {e.read().decode('utf-8')}"
        )
        raise IALIRTDataAccessError(message) from e
    except URLError as e:
        message = f"URL Error: {e.reason}"
        raise IALIRTDataAccessError(message) from e


def query(
        *,
        year: str,
        doy: str,
        instance: str,
):
    """Query the logs.

    Parameters
    ----------
    year : str
        Year
    doy : str
        Day of year
    instance : str
        Instance number

    Returns
    -------
    list
        List of files matching the query
    """
    query_params = {
        "year": year,
        "doy": doy,
        "instance": instance,
    }

    url = f"{ialirt_data_access.config['DATA_ACCESS_URL']}"
    url += f"/ialirt-log-query?{urlencode(query_params)}"

    logger.info("Querying data archive for %s with url %s", query_params, url)
    request = urllib.request.Request(url, method="GET")
    with _get_url_response(request) as response:
        # Retrieve the response as a list of files
        items = response.read().decode("utf-8")
        logger.debug("Received response: %s", items)
        # Decode the JSON string into a list
        items = json.loads(items)
        logger.debug("Decoded JSON: %s", items)
    return items
