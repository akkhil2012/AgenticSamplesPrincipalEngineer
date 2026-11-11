"""Read replaceable supplier exports; no recommendation or routing rules here."""

import csv
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = {
    "quote_id",
    "category",
    "product",
    "supplier",
    "unit_price",
    "currency",
    "available_units",
    "lead_days",
    "region",
    "certifications",
    "quoted_on",
}


def load_quotes():
    path = Path(os.getenv("QUOTES_CSV", "data/example_quotes.csv"))
    if not path.is_absolute():
        path = ROOT / path
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if set(reader.fieldnames or []) != FIELDS:
            raise ValueError("Quote CSV must have exactly the documented columns")
        rows = list(reader)
    if not 0 < len(rows) <= 5000:
        raise ValueError("Quote CSV must contain 1 to 5000 rows")
    seen = set()
    for row in rows:
        if not all(isinstance(v, str) and len(v) <= 500 for v in row.values()):
            raise ValueError("Invalid quote field")
        if not row["quote_id"] or row["quote_id"] in seen:
            raise ValueError("Quote IDs must be unique and nonempty")
        seen.add(row["quote_id"])
        try:
            price = Decimal(row["unit_price"])
            available = int(row["available_units"])
            lead = int(row["lead_days"])
        except (ValueError, InvalidOperation):
            raise ValueError("Invalid numeric quote field") from None
        if not price.is_finite() or price <= 0 or available < 0 or lead < 0:
            raise ValueError("Quote amounts and lead times must be valid")
    return rows


def search_quotes(query: str) -> list[dict]:
    """Search product/category/supplier text. Empty query lists up to 50 quotes."""
    terms = query.lower().split()
    return [
        r
        for r in load_quotes()
        if all(
            t in " ".join(r[k] for k in ("category", "product", "supplier")).lower()
            for t in terms
        )
    ][:50]


def quote_cost(quote_id: str, quantity: int) -> dict:
    """Calculate exact merchandise subtotal; never implies reservation or purchase."""
    if (
        isinstance(quantity, bool)
        or not isinstance(quantity, int)
        or not 1 <= quantity <= 100000
    ):
        raise ValueError("Quantity must be an integer between 1 and 100000")
    row = next((r for r in load_quotes() if r["quote_id"] == quote_id), None)
    if row is None:
        raise ValueError("Unknown quote ID")
    return {
        "quote_id": quote_id,
        "quantity": quantity,
        "subtotal": str(
            (Decimal(row["unit_price"]) * quantity).quantize(Decimal("0.01"))
        ),
        "currency": row["currency"],
        "available_units": int(row["available_units"]),
        "lead_days": int(row["lead_days"]),
        "quoted_on": row["quoted_on"],
        "exclusions": "Taxes, shipping, FX conversion and discounts are not included.",
    }
