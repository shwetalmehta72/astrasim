from app.core.config import get_settings


def test_meta_info_endpoint_returns_app_details(client) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/api/v1/meta/info")
    assert response.status_code == 200

    payload = response.json()
    settings = get_settings()
    assert payload["app_name"] == settings.APP_NAME
    assert payload["environment"] == settings.APP_ENV
    assert payload["version"] == settings.APP_VERSION

