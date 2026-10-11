from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from infrai_client import InfraiClient


class AvatarSubmission(BaseModel):
    seller_id: str = Field(min_length=1)
    buyer_id: str = Field(min_length=1)
    order_id: str = Field(min_length=1)
    image_path: Path
    filename: str = Field(min_length=1)
    aspect: str = Field(default="1:1", min_length=3)


class SellerAsset(BaseModel):
    seller_id: str
    original_image_id: str
    cropped_image_id: str
    optimized_image_id: str
    status: str


class BuyerUpdate(BaseModel):
    buyer_id: str
    seller_id: str
    avatar_image_id: str
    status: str


class OrderHandoff(BaseModel):
    order_id: str
    seller_id: str
    avatar_image_id: str
    status: str


class AvatarPipelineResult(BaseModel):
    seller_asset: SellerAsset
    buyer_update: BuyerUpdate
    order_handoff: OrderHandoff


class ImageClient(Protocol):
    def image_upload(self, *, file_obj, filename: str): ...
    def image_smart_crop(self, *, image: str, aspect: str): ...
    def image_compress(self, *, image: str): ...


@dataclass
class MarketplaceAvatarService:
    infrai: ImageClient

    def process_submission(self, submission: AvatarSubmission) -> AvatarPipelineResult:
        with submission.image_path.open("rb") as image_file:
            uploaded = self.infrai.image_upload(file_obj=image_file, filename=submission.filename)

        original_id = self._extract_image_id(uploaded.data)
        cropped = self.infrai.image_smart_crop(image=original_id, aspect=submission.aspect)
        cropped_id = self._extract_image_id(cropped.data)
        optimized = self.infrai.image_compress(image=cropped_id)
        optimized_id = self._extract_image_id(optimized.data)

        seller_asset = SellerAsset(
            seller_id=submission.seller_id,
            original_image_id=original_id,
            cropped_image_id=cropped_id,
            optimized_image_id=optimized_id,
            status="ready_for_delivery",
        )
        buyer_update = BuyerUpdate(
            buyer_id=submission.buyer_id,
            seller_id=submission.seller_id,
            avatar_image_id=optimized_id,
            status="avatar_updated",
        )
        order_handoff = OrderHandoff(
            order_id=submission.order_id,
            seller_id=submission.seller_id,
            avatar_image_id=optimized_id,
            status="ready_for_packaging",
        )
        return AvatarPipelineResult(
            seller_asset=seller_asset,
            buyer_update=buyer_update,
            order_handoff=order_handoff,
        )

    @staticmethod
    def _extract_image_id(data):
        if isinstance(data, dict):
            for key in ("id", "image", "image_id"):
                value = data.get(key)
                if isinstance(value, str) and value:
                    return value
        if isinstance(data, str) and data:
            return data
        raise ValueError("Expected an image identifier in response data")


def build_service() -> MarketplaceAvatarService:
    return MarketplaceAvatarService(infrai=InfraiClient())
