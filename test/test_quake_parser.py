import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import datetime
from quake_parser import parse_quake_record


def test_parse_quake_record_returns_complete_fields(monkeypatch):
    sample_eq = {
        "EarthquakeInfo": {
            "OriginTime": "2023-01-01 12:34:56",
            "Epicenter": {"Location": "台北市大安區"},
            "FocalDepth": 10,
            "EarthquakeMagnitude": {"MagnitudeValue": 4.5},
        },
        "ReportContent": "test report",
        "Web": "https://example.com",
    }

    def fake_get_coordinates(name):
        return 25.0, 121.5

    monkeypatch.setattr("quake_parser.get_coordinates_from_text", fake_get_coordinates)

    quake = parse_quake_record(sample_eq)
    assert quake is not None
    expected_fields = [
        "origin_time",
        "epicenter",
        "depth",
        "magnitude",
        "report",
        "link",
        "lat",
        "lon",
    ]
    for field in expected_fields:
        assert field in quake
        assert quake[field] is not None
    assert quake["origin_time"].tzinfo is not None
    assert quake["origin_time"].strftime("%Y-%m-%d %H:%M:%S") == "2023-01-01 12:34:56"