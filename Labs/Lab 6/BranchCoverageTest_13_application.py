import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


def route(session="standard_30", walks=None, confirmed=True, weekend=False):
    return {
        "route_confirmed": confirmed,
        "session_type": session,
        "walks": walks if walks is not None else [],
        "is_weekend": weekend
    }


def walk(pets=1, aggression=False, meds=False):
    return {
        "num_pets": pets,
        "aggression_alert": aggression,
        "needs_meds": meds
    }


def test_invalid_routes_type():
    with pytest.raises(ValueError):
        process_walking_routes("not a list", 5)


def test_negative_transport_fee():
    with pytest.raises(ValueError):
        process_walking_routes([], -1)


def test_unconfirmed_route_is_skipped():
    result = process_walking_routes([route(confirmed=False)], 5)
    assert result["status"] == "ZERO_EARNINGS"


@pytest.mark.parametrize("session,base", [
    ("standard_60", 35.0),
    ("standard_30", 22.0),
    ("express_15", 14.0)
])
def test_supported_sessions(session, base):
    result = process_walking_routes([route(session, [walk()])], 0)
    assert result["total_revenue"] == base + 5
    assert result["status"] == "COMPLETED"


def test_unknown_session():
    result = process_walking_routes([route("unknown", [walk()])], 0)
    assert result["status"] == "ZERO_EARNINGS"


@pytest.mark.parametrize("pets", [0, -1])
def test_non_positive_pet_count(pets):
    result = process_walking_routes([route(walks=[walk(pets)])], 0)
    assert result["total_revenue"] == 0


def test_aggression_standard_30():
    result = process_walking_routes([route(walks=[walk(aggression=True)])], 0)
    assert result["status"] == "ZERO_EARNINGS"


def test_aggression_standard_60():
    result = process_walking_routes([
        route("standard_60", [walk(2), walk(aggression=True), walk(1)], weekend=True)
    ], 7)
    assert result["total_revenue"] == 7
    assert result["status"] == "COMPLETED"


def test_more_than_three_pets():
    result = process_walking_routes([route(walks=[walk(4)])], 0)
    assert result["total_revenue"] == 48.6


def test_three_pets_with_medication():
    result = process_walking_routes([route(walks=[walk(3, meds=True)])], 0)
    assert result["total_revenue"] == 43


def test_weekend_transport_fee():
    result = process_walking_routes([route(walks=[walk()], weekend=True)], 5)
    assert result["total_revenue"] == 32


def test_more_than_four_incidents():
    routes = [route("unknown") for _ in range(5)]
    result = process_walking_routes(routes, 0)
    assert result["status"] == "INCIDENT_AUDIT"


def test_incident_audit_precedence():
    routes = [route(walks=[walk(0)]) for _ in range(5)]
    result = process_walking_routes(routes, 0)
    assert result["status"] == "INCIDENT_AUDIT"


def test_empty_routes():
    result = process_walking_routes([], 0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


def test_incidents_below_threshold():
    result = process_walking_routes([route(walks=[walk(0), walk()])], 0)
    assert result["total_revenue"] == 27
    assert result["status"] == "COMPLETED"


def test_no_gps_data():
    assert inspect_gps_collars([]) == "NO_DATA"


def test_normal_gps_signals():
    assert inspect_gps_collars([[50, 60, 70]]) == "ONLINE"


def test_one_weak_signal():
    assert inspect_gps_collars([[10, 50]]) == "ONLINE"


def test_two_consecutive_weak_signals():
    assert inspect_gps_collars([[10, 15]]) == "LOST_SIGNAL_ALERT"


def test_three_consecutive_weak_signals():
    assert inspect_gps_collars([[10, 15, 12]]) == "LOST_SIGNAL_ALERT"


def test_strong_signal_resets_streak():
    assert inspect_gps_collars([[10, 50, 10]]) == "ONLINE"


def test_multiple_collar_logs():
    assert inspect_gps_collars([[50, 60], [10, 15]]) == "LOST_SIGNAL_ALERT"


def test_empty_individual_collar_log():
    assert inspect_gps_collars([[]]) == "ONLINE"
