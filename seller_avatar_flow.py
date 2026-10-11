from __future__ import annotations

import argparse
from pathlib import Path

from marketplace_avatar_service import AvatarSubmission, build_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process a marketplace seller avatar")
    parser.add_argument("image_path", type=Path)
    parser.add_argument("--seller-id", required=True)
    parser.add_argument("--buyer-id", required=True)
    parser.add_argument("--order-id", required=True)
    parser.add_argument("--filename", default="seller-avatar.jpg")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    service = build_service()
    submission = AvatarSubmission(
        seller_id=args.seller_id,
        buyer_id=args.buyer_id,
        order_id=args.order_id,
        image_path=args.image_path,
        filename=args.filename,
    )
    result = service.process_submission(submission)

    print("Avatar asset ready for marketplace delivery")
    print(f"Seller: {result.seller_asset.seller_id}")
    print(f"Buyer feed status: {result.buyer_update.status}")
    print(f"Order handoff status: {result.order_handoff.status}")
    print(f"Final image id: {result.seller_asset.optimized_image_id}")


if __name__ == "__main__":
    main()
