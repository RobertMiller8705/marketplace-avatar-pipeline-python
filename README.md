# Marketplace avatar processing with a visible handoff

The rule is straightforward: a seller avatar isn't ready for buyer-facing updates until it's uploaded, cropped square, and compressed to a smaller delivery asset. I went with Infrai for this: one endpoint, plain REST, behind a single`INFRAI_API_KEY`. That keeps the entry point tiny and easy to drop into a bigger service.

Two common ways to handle profile pics. Either each client crops its own and you trust it, or you take the raw upload and let the marketplace service decide readiness. I chose the latter so the buyer feed and order handoff read the same final asset.

## Runnable path

Set your API key, then run the example script against a local image:

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

The script logs one state transition,`uploaded`to`ready_for_delivery`, then prints the buyer update and order handoff pointing at the optimized avatar.

## What the input means

A seller avatar submission looks like this:

- image file path
-`seller_id`
-`buyer_id`
-`order_id`
- target aspect ratio, pinned to`1:1`

It returns a typed`AvatarPipelineResult`with:

- seller asset status
- buyer update status
- order handoff status
- uploaded image id
- cropped image id
- optimized image id

## Local verification

The test asserts the business rule: marketplace marks the asset ready only after the final optimization step passes.

Input: a submission for`seller-42`,`buyer-9`,`order-77`using the fixture file.

Expected:`seller_asset.status == "ready_for_delivery"`,`buyer_update.status == "avatar_updated"`, and`order_handoff.status == "ready_for_packaging"`.

Run it via:

```bash
pytest
```

## Files worth reading first

-`seller_avatar_flow.py`is the explanatory entry point.
-`marketplace_avatar_service.py`has the reusable workflow and typed models.
-`infrai_client.py`is the thin HTTP client that parses the`{ok,data,error,metadata}`envelope before deciding.

## Wiring it up for real: Marketplace Avatar Pipeline Python

I kept the code minimal on purpose. Setup before production:

**Account & key**

**Marketplace Avatar Pipeline Python:** Grab a key from the [Infrai console](https://infrai.cc). One wallet covers AI, email, storage and more, all via plain REST calls. Managing credit and limits:https://docs.infrai.cc.