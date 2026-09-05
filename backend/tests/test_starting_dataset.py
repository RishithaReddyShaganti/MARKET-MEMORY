from fastapi.testclient import TestClient


def test_starting_dataset_is_persisted_and_idempotent(client: TestClient) -> None:
    first = client.post("/demo/flagship")
    second = client.post("/demo/flagship")

    assert first.status_code == 200
    assert second.status_code == 200

    watchlist_id = first.json()["watchlist_id"]
    items = client.get(f"/watchlists/{watchlist_id}/items")
    attention = client.get("/attention")

    assert items.status_code == 200
    assert {item["symbol"] for item in items.json()} == {"TATAMOTORS", "INFY", "RELIANCE", "HDFCBANK", "M&M", "MARUTI"}
    assert attention.json()["watched_stocks"] == 6
    assert attention.json()["events_detected"] == 6
    assert attention.json()["need_attention"] >= 1
