from fastapi.testclient import TestClient


def create_watchlist(client: TestClient, name: str = "Long-term investments") -> dict[str, object]:
    response = client.post("/watchlists", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_create_list_rename_and_delete_watchlist(client: TestClient) -> None:
    watchlist = create_watchlist(client)
    watchlist_id = watchlist["id"]
    assert watchlist["name"] == "Long-term investments"

    renamed = client.patch(f"/watchlists/{watchlist_id}", json={"name": "Growth ideas"})
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Growth ideas"

    deleted = client.delete(f"/watchlists/{watchlist_id}")
    assert deleted.status_code == 204
    assert client.get(f"/watchlists/{watchlist_id}").status_code == 404


def test_retrieve_watchlists_and_user_relationship(client: TestClient) -> None:
    create_watchlist(client, "Core")
    response = client.get("/watchlists")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == "00000000-0000-0000-0000-000000000001"


def test_add_retrieve_update_and_delete_stock(client: TestClient) -> None:
    watchlist_id = create_watchlist(client)["id"]
    created = client.post(f"/watchlists/{watchlist_id}/items", json={"symbol": "tatamotors", "company_name": "Tata Motors", "intent_type": "growth", "intent_text": "Track EV growth."})
    assert created.status_code == 201
    item = created.json()
    assert item["symbol"] == "TATAMOTORS"

    listed = client.get(f"/watchlists/{watchlist_id}/items")
    assert listed.status_code == 200
    assert listed.json()[0]["company_name"] == "Tata Motors"

    updated = client.patch(f"/watchlists/{watchlist_id}/items/{item['id']}", json={"intent_type": "valuation", "intent_text": ""})
    assert updated.status_code == 200
    assert updated.json()["intent_type"] == "valuation"
    assert updated.json()["intent_text"] is None

    assert client.delete(f"/watchlists/{watchlist_id}/items/{item['id']}").status_code == 204
    assert client.get(f"/watchlists/{watchlist_id}/items").json() == []


def test_validation_duplicates_and_missing_resources(client: TestClient) -> None:
    assert client.post("/watchlists", json={"name": "   "}).status_code == 422
    watchlist_id = create_watchlist(client, "India")["id"]
    stock = {"symbol": "reliance", "company_name": "Reliance Industries", "intent_type": "long_term_business"}
    assert client.post(f"/watchlists/{watchlist_id}/items", json=stock).status_code == 201
    assert client.post(f"/watchlists/{watchlist_id}/items", json=stock).status_code == 409
    assert client.post(f"/watchlists/{watchlist_id}/items", json={**stock, "symbol": "X", "intent_type": "invalid"}).status_code == 422
    assert client.post(f"/watchlists/{watchlist_id}/items", json={**stock, "symbol": "Y", "intent_type": "custom"}).status_code == 422
    assert client.get("/watchlists/00000000-0000-0000-0000-000000000099").status_code == 404
    assert client.delete(f"/watchlists/{watchlist_id}/items/00000000-0000-0000-0000-000000000099").status_code == 404


def test_duplicate_watchlist_name_conflicts(client: TestClient) -> None:
    create_watchlist(client, "Core")
    assert client.post("/watchlists", json={"name": "Core"}).status_code == 409
