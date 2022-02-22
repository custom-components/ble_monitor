"""Helper for ble_monitor."""
import logging
import re
from typing import Optional, Any
from uuid import UUID
import voluptuous as vol

from homeassistant.const import (
    CONF_MAC,
)
from .const import (
    MAC_REGEX,
    AES128KEY24_REGEX,
    AES128KEY32_REGEX,

    CONF_UUID,
)

_LOGGER = logging.getLogger(__name__)


def identifier_normalize(value: str) -> str:
    if validate_uuid(value):
        return str(UUID(value))

    if ':' in value:
        return value

    return ":".join(value[i : i + 2] for i in range(0, len(value), 2))


def detect_conf_type(value: str) -> str:
    return CONF_UUID if validate_uuid(value) else CONF_MAC


def dict_get_or(data: dict, first: str = CONF_UUID, second: str = CONF_MAC) -> Optional[str]:
    key = dict_get_key_or(data, first, second)

    return data[key] if key in data else None


def dict_get_or_normalize(data: dict, first: str = CONF_UUID, second: str = CONF_MAC) -> Optional[str]:
    key = dict_get_key_or(data, first, second)

    return identifier_normalize(data[key]) if key in data else None


def dict_get_or_clean(data: dict, first: str = CONF_UUID, second: str = CONF_MAC) -> str:
    return identifier_clean(dict_get_or(data, first, second))


def dict_get_key_or(data: dict, first: str = CONF_UUID, second: str = CONF_MAC) -> str:
    return first if first in data and data[first] else second


def identifier_clean(value: str) -> str:
    """Clean the identifier key."""
    return value.replace("-", "").replace(":", "").upper()


def validate_mac(value: str) -> bool:
    """Mac validation."""
    return _validate_regex(value, MAC_REGEX)


def validate_uuid(value: str) -> bool:
    """UUID validation."""
    try:
        config_validation_uuid(value)

        return True
    except vol.Invalid:
        return False


def validate_key(value: str) -> bool:
    """Key validation."""
    if not value or value == "-":
        return True

    if not _validate_regex(value, AES128KEY24_REGEX):
        if not _validate_regex(value, AES128KEY32_REGEX):
            return False

    return True


def _validate_regex(value: str, regex: str) -> bool:
    """Validate that the value is a string that matches a regex."""
    compiled = re.compile(regex)
    if not compiled.match(value):
        return False
    return True


def config_validation_uuid(value: Any) -> str:
    try:
        result = str(UUID(value))
    except (ValueError, AttributeError, TypeError) as error:
        raise vol.Invalid("Invalid UUID", error_message=str(error))

    if identifier_clean(result).lower() != identifier_clean(value).lower():
        raise vol.Invalid("Invalid UUID")

    return result
