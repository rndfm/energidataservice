"""Fixed price connector."""
from __future__ import annotations

from datetime import datetime, timedelta
from logging import getLogger

import pytz

from ...const import CONF_FIXED_PRICE_VALUE, INTERVAL
from .regions import REGIONS

_LOGGER = getLogger(__name__)

SOURCE_NAME = "Fixed Price"

DEFAULT_CURRENCY = None

__all__ = ["REGIONS", "Connector", "DEFAULT_CURRENCY"]


def prepare_data(value, date, tz) -> list:  # pylint: disable=invalid-name
    """Get today prices."""
    local_tz = pytz.timezone(tz)
    reslist = []
    i = 0
    while i < 24:
        hour = str(i)
        if len(hour) < 2:
            hour = f"0{hour}"
        tmpdate = (
            datetime.fromisoformat(f"{date}T{hour}:00:00+00:00")
            .replace(tzinfo=pytz.utc)
            .astimezone(local_tz)
        )
        tmp = INTERVAL(value, local_tz.normalize(tmpdate))
        if date in tmp.hour.strftime("%Y-%m-%d"):
            reslist.append(tmp)

        i += 1

    return reslist


class Connector:
    """Fixed price connector class."""

    def __init__(
        self,
        regionhandler,
        client=None,  # pylint: disable=unused-argument
        tz=None,  # pylint: disable=invalid-name
        config=None,
    ) -> None:
        """Init API connection to Energi Data Service"""
        self.config = config
        self.tz = tz  # pylint: disable=invalid-name
        self.regionhandler = regionhandler
        self.value = self.config.options.get(CONF_FIXED_PRICE_VALUE)

    async def async_get_spotprices(self) -> None:
        """Returns the fixed price set in the configuration flow."""
        _LOGGER.debug("Returning the fixed value of '%s'", self.value)
        return self.value

    @property
    def today(self) -> list:
        """Return raw dataset for today."""
        date = datetime.now().strftime("%Y-%m-%d")
        return prepare_data(self.value, date, self.tz)

    @property
    def tomorrow(self) -> list:
        """Return raw dataset for today."""
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        return prepare_data(self.value, date, self.tz)
