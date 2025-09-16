# Lambda function code

```python
import json
import os
from decimal import Decimal
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.getenv("TABLE_NAME", "ProductCatalog")
table = dynamodb.Table(TABLE_NAME)

def _to_native(o):
    # Convert Decimal and nested structures to plain Python types for JSON
    if isinstance(o, list):
        return [_to_native(i) for i in o]
    if isinstance(o, dict):
        return {k: _to_native(v) for k, v in o.items()}
    if isinstance(o, Decimal):
        # Keep integers as int, others as float
        return int(o) if o % 1 == 0 else float(o)
    return o

def lambda_handler(event, context):
    """
    event examples (see test events below):
    { "op": "get_by_id", "id": 101 }
    { "op": "batch_get", "ids": [101, 201, 205] }
    { "op": "scan_by_category_price", "category": "Book", "min_price": 10 }
    { "op": "scan_all", "limit": 5 }
    """
    op = event.get("op")

    if op == "get_by_id":
        item_id = int(event["id"])
        resp = table.get_item(Key={"Id": item_id})
        item = resp.get("Item")
        return {
            "found": item is not None,
            "item": _to_native(item) if item else None
        }

    if op == "batch_get":
        ids = [int(i) for i in event["ids"]]
        keys = [{"Id": i} for i in ids]
        client = boto3.client("dynamodb")

        resp = client.batch_get_item(
            RequestItems={TABLE_NAME: {"Keys": [{"Id": {"N": str(k["Id"])}} for k in keys]}}
        )
        items = resp.get("Responses", {}).get(TABLE_NAME, [])
        # client returns AttributeValue format; use resource’s TypeDeserializer or quick decode via boto3.dynamodb.types
        from boto3.dynamodb.types import TypeDeserializer
        d = TypeDeserializer()
        py_items = [{k: d.deserialize(v) for k, v in it.items()} for it in items]
        return {"count": len(py_items), "items": _to_native(py_items)}

    if op == "scan_by_category_price":
        category = event["category"]
        min_price = Decimal(str(event.get("min_price", 0)))
        from boto3.dynamodb.conditions import Attr
        resp = table.scan(
            FilterExpression=Attr("ProductCategory").eq(category) & Attr("Price").gte(min_price)
        )
        return {"count": resp["Count"], "items": _to_native(resp.get("Items", []))}

    if op == "scan_all":
        limit = int(event.get("limit", 10))
        resp = table.scan(Limit=limit)
        return {"count": resp.get("Count", 0), "items": _to_native(resp.get("Items", []))}

    return {"error": "Unknown op", "event": event}
```

## Test events

1. Get a single book (Id 101)

```json
{
  "op": "get_by_id",
  "id": 101
}
```

2. Get a single bike (Id 201)

```json
{
  "op": "get_by_id",
  "id": 201
}
```

3. Batch get a few items

```json
{
  "op": "batch_get",
  "ids": [101, 201, 205]
}
```

4. Scan: books priced >= 10

```json
{
  "op": "scan_by_category_price",
  "category": "Book",
  "min_price": 10
}
```