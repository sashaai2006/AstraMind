import base64
import os
import time
from pathlib import Path
from typing import Dict

import httpx
import pytest
import requests
import requests_mock
from fastapi.testclient import TestClient

from backend import settings as settings_module
from backend.main import app


@pytest.fixture(autouse=True)
def test_env(tmp_path, monkeypatch):
    projects_root = tmp_path / "projects"
    monkeypatch.setenv("PROJECTS_ROOT", str(projects_root))
    monkeypatch.setenv("LLM_MODE", "mock")
    settings_module.get_settings.cache_clear()
    yield
    settings_module.get_settings.cache_clear()


def _create_project(client: TestClient) -> str:
    response = client.post(
        "/api/projects",
        json={"title": "test", "description": "demo", "target": "web"},
    )
    assert response.status_code == 201
    return response.json()["project_id"]


def _wait_for_files(client: TestClient, project_id: str) -> None:
    for _ in range(20):
        files = client.get(f"/api/projects/{project_id}/files").json()
        if files:
            return
        time.sleep(0.2)
    raise AssertionError("Files were not generated in time")


def test_create_project_creates_directory():
    with TestClient(app) as client:
        project_id = _create_project(client)
        root = Path(os.environ["PROJECTS_ROOT"])
        assert (root / project_id).exists()


def test_files_endpoint_returns_entries():
    with TestClient(app) as client:
        project_id = _create_project(client)
        _wait_for_files(client, project_id)
        response = client.get(f"/api/projects/{project_id}/files")
        assert response.status_code == 200
        assert len(response.json()) > 0


def test_publish_to_github(monkeypatch):
    with TestClient(app) as client:
        project_id = _create_project(client)
        _wait_for_files(client, project_id)

        with requests_mock.Mocker() as mocker:
            mocker.post(
                "https://api.github.com/user/repos",
                json={"full_name": "demo/example", "owner": {"login": "demo"}},
                status_code=201,
            )
            mocker.put(
                requests_mock.ANY,
                json={"content": {"sha": "abc123"}},
                status_code=201,
            )

            async def fake_request(self, method, url, headers=None, json=None):
                full_url = f"{self.base_url}{url}"
                response = requests.request(
                    method,
                    full_url,
                    headers=headers,
                    json=json,
                )
                return httpx.Response(
                    status_code=response.status_code,
                    content=response.content,
                    request=httpx.Request(method, full_url),
                )

            monkeypatch.setattr(httpx.AsyncClient, "request", fake_request, raising=False)

            publish_response = client.post(
                f"/api/projects/{project_id}/publish/github",
                json={"token": "abc", "repo_name": "example", "private": False},
            )

        assert publish_response.status_code == 200
        assert publish_response.json()["url"] == "https://github.com/demo/example"
        last_request = mocker.request_history[-1]
        encoded = last_request.json()["content"]
        assert base64.b64decode(encoded.encode("ascii"))

