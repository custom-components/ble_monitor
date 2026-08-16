"""Tests for batched HCI LE advertising reports."""
from types import SimpleNamespace
from unittest.mock import Mock

from ble_monitor.ble_parser import BleParser

from ble_monitor import HCIdump

EXTENDED_ATC = bytes.fromhex(
    "043E2B0D011300004E7CBC38C1A40100FF7FB90000000000000000001110161A18A4C138BC7C4E0102284F0B6720"
)
EXTENDED_CUSTOM = bytes.fromhex(
    "043E300D011300008B376338C1A40100FF7FBA0000000000000000001602010612161A188B376338C1A4CE0913107F0B521204"
)
LEGACY_ATC = bytes.fromhex(
    "043e1d02010000f4830238c1a41110161a18a4c1380283f400a22f5f0bf819df"
)
LEGACY_CUSTOM = bytes.fromhex(
    "043e1f02010000f4830238c1a41312161a18f4830238c1a4a9066911b60b58f70dde"
)


def batch_reports(*events, count=None, trailing=b""):
    """Combine synthetic single-report fixtures into one HCI event."""
    subevent = events[0][3]
    reports = b"".join(event[5:] for event in events) + trailing
    body = bytes((subevent, len(events) if count is None else count)) + reports
    return bytes((events[0][0], events[0][1], len(body))) + body


def test_two_extended_pvvx_reports_are_both_parsed():
    """Every PVVX/ATC report in one extended event is returned."""
    parsed = BleParser().parse_raw_data_reports(
        batch_reports(EXTENDED_ATC, EXTENDED_CUSTOM)
    )
    assert [sensor["mac"] for sensor, _ in parsed] == [
        "A4C138BC7C4E",
        "A4C13863378B",
    ]


def test_legacy_multi_report_layout_remains_supported():
    """Legacy advertising events can also contain multiple reports."""
    parsed = BleParser().parse_raw_data_reports(
        batch_reports(LEGACY_ATC, LEGACY_CUSTOM)
    )
    assert len(parsed) == 2


def test_unknown_report_does_not_discard_known_report():
    """A mixed batch retains a supported report."""
    unknown = bytearray(EXTENDED_ATC)
    uuid_offset = bytes(unknown).index(bytes.fromhex("1a18"))
    unknown[uuid_offset:uuid_offset + 2] = b"\xff\xff"
    parsed = BleParser().parse_raw_data_reports(
        batch_reports(bytes(unknown), EXTENDED_CUSTOM)
    )
    assert len(parsed) == 1
    assert parsed[0][0]["mac"] == "A4C13863378B"


def test_truncated_later_report_keeps_complete_earlier_report():
    """Safe framing preserves reports preceding a truncated report."""
    event = batch_reports(
        EXTENDED_ATC,
        count=2,
        trailing=EXTENDED_CUSTOM[5:20],
    )
    parsed = BleParser().parse_raw_data_reports(event)
    assert len(parsed) == 1
    assert parsed[0][0]["mac"] == "A4C138BC7C4E"


def test_hcidump_enqueues_all_reports_but_counts_one_raw_event():
    """HCIdump fans out parsed reports without inflating raw activity count."""
    hcidump = HCIdump.__new__(HCIdump)
    hcidump.ble_parser = BleParser()
    hcidump._last_hci_activity = {}
    hcidump.evt_cnt = {}
    hcidump.dataqueue_bin = SimpleNamespace(sync_q=Mock())
    hcidump.dataqueue_meas = SimpleNamespace(sync_q=Mock())
    hcidump.dataqueue_tracker = SimpleNamespace(sync_q=Mock())

    hcidump.process_hci_events(
        batch_reports(EXTENDED_ATC, EXTENDED_CUSTOM), hci=0
    )

    assert hcidump.evt_cnt == {0: 1}
    assert hcidump.dataqueue_meas.sync_q.put_nowait.call_count == 2
