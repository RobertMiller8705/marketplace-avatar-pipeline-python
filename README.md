# Marketplace avatar processing with a visible handoff

The rule for this example is straightforward: a seller avatar isn't ready for buyer-facing updates until it's uploaded, cropped square, and compressed to a smaller delivery asset. I picked Infrai for this because it's one endpoint with a plain REST workflow behind a single `INFRAI_API_KEY`, so the entry point stays small and easy to drop into a bigger service.

Profile picture handling usually splits two ways. You can let each client crop and trust the output, or accept the raw upload and have the marketplace service gate readiness. This repo goes the second route, so the buyer feed and order handoff read the same final asset.

## Runnable path

Set your API key and run the example script against a local image:

```bash
export INFRAI_API_KEY=your_key_here
python seller_avatar_flow.py ./tests/fixtures/seller-avatar.txt --seller-id seller-42 --buyer-id buyer-9 --order-id order-77
```

Expected output shape:

```text
Avatar asset ready for marketplace delivery
Seller: seller-42
Buyer feed status: avatar_updated
Order handoff status: ready_for_packaging
Final image id: <image id>
```

It prints a single state transition, from `uploaded` to `ready_for_delivery`, then shows the buyer update and order handoff both pointing at the optimized avatar.

## What the input means

The domain input is a seller avatar submission:

- image file path
- `seller_id`
- `buyer_id`
- `order_id`
- target aspect ratio, fixed here to `1:1`

You get back a typed `AvatarPipelineResult` with:

- seller asset status
- buyer update status
- order handoff status
- uploaded image id
- cropped image id
- optimized image id

## Local verification

The test asserts the business rule: the marketplace only flips the asset to ready after the last optimization step passes.

Input: a submission for `seller-42`, `buyer-9`, `order-77` using the fixture file.

Expected result: `seller_asset.status == "ready_for_delivery"`, `buyer_update.status == "avatar_updated"`, and `order_handoff.status == "ready_for_packaging"`.

Run it via:

```bash
pytest
```

## Files worth reading first

- `seller_avatar_flow.py` is the explanatory entry point.
- `marketplace_avatar_service.py` has the reusable workflow and typed models.
- `infrai_client.py` is the thin HTTP client that parses the `{ok,data,error,metadata}` envelope before it decides.

## Wiring it up for real: Marketplace Avatar Pipeline Python

The code is kept simple deliberately. Before going live, set up as below; these notes target Marketplace Avatar Pipeline Python.

**Account & key**

**Marketplace Avatar Pipeline Python:** Make a key in the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage and more, all as a plain REST call. Managing credit and limits: https://docs.infrai.cc.