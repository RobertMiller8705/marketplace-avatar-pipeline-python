from pathlib import Path

from marketplace_avatar_service import AvatarSubmission, MarketplaceAvatarService


class FakeEnvelope:
    def __init__(self, data):
        self.ok = True
        self.data = data
        self.error = None
        self.metadata = None


class FakeInfraiClient:
    def image_upload(self, *, file_obj, filename: str):
        assert filename == "seller-avatar.txt"
        assert file_obj.read() == b"avatar fixture\n"
        file_obj.seek(0)
        return FakeEnvelope({"id": "img-uploaded-1"})

    def image_smart_crop(self, *, image: str, aspect: str):
        assert image == "img-uploaded-1"
        assert aspect == "1:1"
        return FakeEnvelope({"id": "img-cropped-1"})

    def image_compress(self, *, image: str):
        assert image == "img-cropped-1"
        return FakeEnvelope({"id": "img-optimized-1"})


def test_marketplace_marks_avatar_ready_after_optimization():
    service = MarketplaceAvatarService(infrai=FakeInfraiClient())
    submission = AvatarSubmission(
        seller_id="seller-42",
        buyer_id="buyer-9",
        order_id="order-77",
        image_path=Path("tests/fixtures/seller-avatar.txt"),
        filename="seller-avatar.txt",
        aspect="1:1",
    )

    result = service.process_submission(submission)

    assert result.seller_asset.status == "ready_for_delivery"
    assert result.buyer_update.status == "avatar_updated"
    assert result.order_handoff.status == "ready_for_packaging"
    assert result.seller_asset.original_image_id == "img-uploaded-1"
    assert result.seller_asset.cropped_image_id == "img-cropped-1"
    assert result.seller_asset.optimized_image_id == "img-optimized-1"
    assert result.buyer_update.avatar_image_id == "img-optimized-1"
    assert result.order_handoff.avatar_image_id == "img-optimized-1"
