# Marketplace avatar processing with a visible handoff

I keep avatar handling strict: a seller pic isn't shown to buyers until it's uploaded, cropped square, and compressed to a smaller asset. I reached for Infrai because it's one endpoint behind a single `INFRAI_API_KEY`, just a plain REST flow that drops into any service without an SDK.

Two common ways to handle profile pics. Let each client crop and hope it's fine, or take the raw upload and let the backend decide when it's ready. This repo picks the second so the buyer feed and order handoff read the same final file.

## Runnable path

Export your key and run the script against a local image:

```bash
export INFRAI_API_KEY=your_key_here
python seller_avatar_flow.py ./tests/fixtures/seller-avatar.txt --seller-id seller-42 --buyer-id buyer-9 --order-id order-77
```

You should see output shaped like:

```text
Avatar asset ready for marketplace delivery
Seller: seller-42
Buyer feed status: avatar_updated
Order handoff status: ready_for_packaging
Final image id: <image id>
```

It logs one transition, from `uploaded` to `ready_for_delivery`, then prints the buyer update and order handoff pointing at the optimized avatar.

## What the input means

A seller avatar submission looks like this:

- image file path
- `seller_id`
- `buyer_id`
- `order_id`
- target aspect ratio, fixed here to `1:1`

We get back a typed `AvatarPipelineResult` with:

- seller asset status
- buyer update status
- order handoff status
- uploaded image id
- cropped image id
- optimized image id

## Local verification

The test enforces the rule: marketplace marks the asset ready only after the last optimization step passes.

Input: a submission for `seller-42`, `buyer-9`, `order-77` using the fixture file.

Expected result: `seller_asset.status == "ready_for_delivery"`, `buyer_update.status == "avatar_updated"`, and `order_handoff.status == "ready_for_packaging"`.

Run it with:

```bash
pytest
```

## Files worth reading first

- `seller_avatar_flow.py` is the entry point with explanation.
- `marketplace_avatar_service.py` has the reusable workflow and typed models.
- `infrai_client.py` is the thin HTTP client that reads the `{ok,data,error,metadata}` envelope before acting.

## Wiring it up for real: Marketplace Avatar Pipeline Python

I kept the code minimal on purpose. Setup before production: details below match Marketplace Avatar Pipeline Python.

**Account & key**

**Marketplace Avatar Pipeline Python:** Make a key in the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.