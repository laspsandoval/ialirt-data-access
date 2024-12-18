"""Tests for the ``io`` module."""

from __future__ import annotations

import json
import os
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

import pytest

import ialirt_data_access

@pytest.fixture()
def mock_urlopen():
    """Mock urlopen to return a file-like object.

    Yields
    ------
    mock_urlopen : unittest.mock.MagicMock
        Mock object for ``urlopen``
    """
    mock_data = b"Mock file content"
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = mock_data
        yield mock_urlopen

def _set_mock_data(mock_urlopen: unittest.mock.MagicMock, data: bytes):
    """Set the data returned by the mock urlopen.

    Parameters
    ----------
    mock_urlopen : unittest.mock.MagicMock
        Mock object for ``urlopen``
    data : bytes
        The mock data
    """
    mock_response = mock_urlopen.return_value.__enter__.return_value
    mock_response.read.return_value = data

@pytest.mark.parametrize(
    "query_params",
    [
        {
            "year": "2024",
            "doy": "045",
            "instance": "1",
        },
    ],
)
def test_query(mock_urlopen: unittest.mock.MagicMock, query_params: list[dict]):
    """Test a basic call to the Query API.

    Parameters
    ----------
    mock_urlopen : unittest.mock.MagicMock
        Mock object for ``urlopen``
    query_params : list of dict
        A list of key/value pairs that set the query parameters
    """
    _set_mock_data(mock_urlopen, json.dumps([]).encode("utf-8"))
    response = ialirt_data_access.query(**query_params)
    # No data found, and JSON decoding works as expected
    assert response == list()

    # Should have only been one call to urlopen
    mock_urlopen.assert_called_once()
    # Assert that the correct URL was used for the query
    urlopen_call = mock_urlopen.mock_calls[0].args[0]
    called_url = urlopen_call.full_url
    expected_url_encoded = f"https://alirt.test.com/ialirt-log-query?{urlencode(query_params)}"
    assert called_url == expected_url_encoded