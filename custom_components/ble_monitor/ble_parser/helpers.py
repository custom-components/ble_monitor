"""Helpers for bleparser"""
from uuid import UUID


def to_uuid(uuid: str) -> str:
    """Return formatted UUID"""
    return str(UUID(''.join(f'{i:02X}' for i in uuid)))


def to_mac(addr: str) -> str:
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)


def to_unformatted_mac(addr: str) -> str:
    """Return unformatted MAC address"""
    return ''.join(f'{i:02X}' for i in addr[:])
