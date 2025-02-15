"""
In my opinion, validators difffers from models:
  - models determine what the structure of a request body / response body should look like, fixing the fields and their name
  - validators parse a field, without enforcing what the name of that field should be
"""

from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status


def validate_date(date_string: Optional[str] = None) -> Optional[datetime]:
    """
    Parses input string to check if it conforms to DD-MM-YYYY format

    Args:
        date_string: the string passed in as a query parameter

    Returns:

        If there was a date string parameter, the DD-MM-YYYY formatted date string

        If there was no date string parameter, None

    Raises:

        HTTPException: if the date is not formatted properly
    """
    if not date_string:
        return None

    try:
        date_obj = datetime.strptime(date_string, "%d-%m-%Y")
        return date_obj

    except (ValueError, TypeError) as e:
        # I would reason that there is no need for a custom error class here because
        # there is not much helpful logging that you can have here
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date: {date_string}. Format should be DD-MM-YYYY",
        )
