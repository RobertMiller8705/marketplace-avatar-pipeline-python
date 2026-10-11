from io import BytesIO

from infrai_client import InfraiClient


def test_upload_sends_json_with_base64_file():
    client = InfraiClient(api_key="test-key")
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)

        class Response:
            status_code = 200

            def json(self):
                return {"ok": True, "data": {"id": "image-1"}}

        return Response()

    client.session.request = fake_request
    client.image_upload(file_obj=BytesIO(b"avatar fixture\n"), filename="seller-avatar.txt")

    assert captured["json"] == {
        "file": "YXZhdGFyIGZpeHR1cmUK",
        "filename": "seller-avatar.txt",
    }
    assert captured["data"] is None
    assert captured["files"] is None
