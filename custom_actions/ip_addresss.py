import ipaddress
import itertools
import re
from typing import Annotated

from pydantic import Field

from tracecat_registry import registry

IPV4_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\b"
IPV6_REGEX = r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)\b"


@registry.register(
    default_title="Extract IP addresses",
    description="Extract unique IPv4 and IPv6 addresses from a list of strings.",
    namespace="etl.extraction",
    display_group="Data Extraction",
)
def extract_ip_addresses(
    texts: Annotated[
        str | list[str],
        Field(..., description="Text or list of text to extract IP addresses from"),
    ],
    ip_version: int | None = None,
) -> list[str]:
    """Extract unique IPv4 and IPv6 addresses from a list of strings."""

    if isinstance(texts, str):
        texts = [texts]

    ip_addresses = itertools.chain.from_iterable(
        re.findall(IPV4_REGEX, text) + re.findall(IPV6_REGEX, text, re.IGNORECASE) for text in texts
    )

    # Validate IP addresses
    valid_ips = set()
    for ip in ip_addresses:
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_version is None or ip_obj.version == ip_version:
                valid_ips.add(str(ip_obj))
        except ValueError:
            continue  # Skip invalid IP addresses

    return list(valid_ips)
