from dataclasses import dataclass, field
import json
import os
from typing import Optional, Dict

import requests


@dataclass
class DbtCloud:
    """
    Interact with the DBT cloud api. List, create or update jobs for a given account
    """

    account_id: int
    api_token: str = field(repr=False, init=False)
    api_base: str = field(init=False, default="https://cloud.getdbt.com/api/v2")
    headers: dict = field(repr=False, init=False)

    def __post_init__(self):
        self.api_token = os.environ["API_TOKEN"]
        self.headers = {"Authorization": f"Token {self.api_token}"}

    def _get(self, url_suffix: str, params: dict = None) -> dict:
        url = self.api_base + url_suffix
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def list_jobs(self, params: dict = None):
        url_suffix = f"/accounts/{self.account_id}/jobs/"
        response = self._get(url_suffix, params)
        return DbtCloudResponse(self, url_suffix, params, response)

    def list_runs(self, params: dict = None):
        url_suffix = f"/accounts/{self.account_id}/runs/"
        response = self._get(url_suffix, params)
        return DbtCloudResponse(self, url_suffix, params, response)

    def get_run_artifacts(self, run_id: int, params: dict = None):
        url_suffix = (
            f"/accounts/{self.account_id}/runs/{run_id}/artifacts/run_results.json"
        )
        response = self._get(url_suffix, params)
        return response

    def get_run_manifest(self, run_id: int, params: dict = None):
        url_suffix = (
            f"/accounts/{self.account_id}/runs/{run_id}/artifacts/manifest.json"
        )
        response = self._get(url_suffix, params)
        return response

    def download_run_artifacts(self, run_id: int):
        for file in ("run_results.json", "catalog.json", "manifest.json"):
            with open(file, "w") as f:
                try:
                    url_suffix = (
                        f"/accounts/{self.account_id}/runs/{run_id}/artifacts/{file}"
                    )
                    response = self._get(url_suffix)
                    f.write(json.dumps(response))
                except requests.exceptions.HTTPError:
                    pass


@dataclass
class DbtCloudResponse:
    """
    Wrapper for the respons from DbtCloud class
    """

    client: DbtCloud
    url_suffix: str
    params: Optional[Dict] = None
    response: Optional[Dict] = None

    def __iter__(self):
        self._iteration = 0
        return self

    def __next__(self):
        self._iteration += 1
        if self._iteration == 1:
            return self

        if self.response.get("status").get("is_success") is False:
            raise RuntimeError("Error while requesting data.")

        if self.response.get("extra") is None:
            raise StopIteration

        self.total_count: int = (
            self.response.get("extra").get("pagination").get("total_count")
        )
        self.count: int = self.response.get("extra").get("pagination").get("count")
        self.offset: int = self.response.get("extra").get("filters").get("offset")

        if self.total_count > self.offset:
            self.offset += self.response.get("extra").get("pagination").get("count")
            self.params = {"offset": self.offset}
            self.response = self.client._get(
                url_suffix=self.url_suffix, params=self.params
            )
            self.count += self.response.get("extra").get("pagination").get("count")
            return self
        else:
            raise StopIteration

    def get(self, key, default=None):
        return self.response.get(key, default)
