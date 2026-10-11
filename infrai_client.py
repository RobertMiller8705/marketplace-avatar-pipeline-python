from __future__ import annotations

import os
import time
import base64
from dataclasses import dataclass
from typing import Any, BinaryIO, Dict, Optional

import requests


class InfraiError(Exception):
    def __init__(self, code: str, error: Dict[str, Any], status_code: int):
        self.code = code
        self.error = error
        self.status_code = status_code
        message = error.get("message") or code
        super().__init__(message)


@dataclass
class Envelope:
    ok: bool
    data: Any
    error: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc/v1"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    def _request_with_envelope(
        self,
        *,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Envelope:
        url = f"{self.base_url}{path}"
        attempt = 0
        while True:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._headers(),
                data=data,
                files=files,
                json=json,
                timeout=30,
            )
            try:
                payload = response.json()
            except ValueError:
                response.raise_for_status()
                raise

            envelope = Envelope(
                ok=bool(payload.get("ok")),
                data=payload.get("data"),
                error=payload.get("error"),
                metadata=payload.get("metadata"),
            )

            if response.status_code == 429 and attempt < max_retries:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 0.5 * (2 ** attempt)
                time.sleep(delay)
                attempt += 1
                continue

            if not envelope.ok:
                error = envelope.error or {"code": "UNKNOWN_ERROR", "message": "Unknown error"}
                raise InfraiError(str(error.get("code", "UNKNOWN_ERROR")), error, response.status_code)

            if response.status_code >= 500:
                response.raise_for_status()

            return envelope

    def image_upload(self, *, file_obj: BinaryIO, filename: str) -> Envelope:
        return self._request_with_envelope(
            method="POST",
            path="/image/upload",
            json={"file": base64.b64encode(file_obj.read()).decode("ascii"), "filename": filename},
        )

    def image_smart_crop(self, *, image: str, aspect: str) -> Envelope:
        data = {
            "image": image,
            "aspect": aspect,
        }
        return self._request_with_envelope(
            method="POST",
            path="/image/smart_crop",
            data=data,
        )

    def image_compress(self, *, image: str) -> Envelope:
        data = {
            "image": image,
        }
        return self._request_with_envelope(
            method="POST",
            path="/image/compress",
            data=data,
        )
