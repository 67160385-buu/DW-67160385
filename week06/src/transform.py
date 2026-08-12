import pandas as pd
from .config import PROVINCE_MAP
def transform_data(raw):
    """
    Transform raw data into clean dimensions, sales, and rejects.
    """

    # =========================================================
    # 1. CUSTOMERS
    # =========================================================
    customers = raw["customers"].copy()

    # Remove duplicate customer_id
    customers = customers.drop_duplicates(
        subset="customer_id",
        keep="first"
    )

    # Standardize province
    if "province" in customers.columns:
        customers["province"] = (
            customers["province"]
            .astype("string")
            .str.strip()
            .replace(PROVINCE_MAP)
        )
        customers["province"] = customers["province"].fillna("Unknown")

    # Handle missing email
    if "email" in customers.columns:
        customers["email"] = customers["email"].fillna("Unknown")

    clean_customers = customers


    # =========================================================
    # 2. PRODUCTS
    # =========================================================
    products = raw["products"].copy()

    # Rename common product fields
    rename_map = {
    "id": "product_id",
    "name": "product_name",
    "productId": "product_id",
    "productName": "product_name",
    "category.name": "category",
    "pricing.price": "price"
}

    products = products.rename(columns=rename_map)
    # Convert price to numeric
    if "price" in products.columns:
        products["price"] = (
        products["price"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    products["price"] = pd.to_numeric(
        products["price"],
        errors="coerce"
    )

    # Missing category -> Unknown
    if "category" in products.columns:
        products["category"] = products["category"].fillna("Unknown")

    clean_products = products


    # =========================================================
    # 3. ORDERS
    # =========================================================
    orders = raw["orders"].copy()

    # Remove duplicate order_id
    orders = orders.drop_duplicates(
        subset="order_id",
        keep="first"
    )

    # Normalize status
    if "status" in orders.columns:
        orders["status"] = (
            orders["status"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # Parse order_date
    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce"
    )

    # Convert numeric columns
    orders["qty"] = pd.to_numeric(
        orders["qty"],
        errors="coerce"
    )

    orders["unit_price"] = pd.to_numeric(
        orders["unit_price"],
        errors="coerce"
    )

    orders["discount_pct"] = pd.to_numeric(
        orders["discount_pct"],
        errors="coerce"
    )


    # =========================================================
    # 4. REJECT INVALID ORDERS
    # =========================================================
    invalid_mask = (
        orders["qty"].isna()
        | (orders["qty"] <= 0)
        | orders["unit_price"].isna()
        | (orders["unit_price"] <= 0)
        | orders["discount_pct"].isna()
        | (orders["discount_pct"] < 0)
        | (orders["discount_pct"] > 100)
        | orders["order_date"].isna()
    )

    rejects = orders.loc[invalid_mask].copy()

    # Keep only valid orders
    valid_orders = orders.loc[~invalid_mask].copy()


    # =========================================================
    # 5. KEEP PAID / COMPLETED
    # =========================================================
    valid_orders = valid_orders[
        valid_orders["status"].isin(["paid", "completed"])
    ].copy()


    # =========================================================
    # 6. JOIN CUSTOMERS
    # =========================================================
    sales = valid_orders.merge(
        clean_customers[
            ["customer_id", "name", "province", "email"]
        ],
        on="customer_id",
        how="left",
        indicator=True
    )

    # Unknown customer -> reject
    unknown_customer = sales["_merge"] == "left_only"

    if unknown_customer.any():
        customer_rejects = sales.loc[
            unknown_customer
        ].copy()

        customer_rejects["reject_reason"] = "Unknown customer_id"

        rejects = pd.concat(
            [rejects, customer_rejects],
            ignore_index=True
        )

    sales = sales.loc[~unknown_customer].copy()
    sales = sales.drop(columns=["_merge"])


    # =========================================================
    # 7. JOIN PRODUCTS
    # =========================================================
    sales = sales.merge(
        clean_products[
            ["product_id", "product_name", "category", "price"]
        ],
        on="product_id",
        how="left",
        indicator=True
    )

    # Unknown product -> reject
    unknown_product = sales["_merge"] == "left_only"

    if unknown_product.any():
        product_rejects = sales.loc[
            unknown_product
        ].copy()

        product_rejects["reject_reason"] = "Unknown product_id"

        rejects = pd.concat(
            [rejects, product_rejects],
            ignore_index=True
        )

    sales = sales.loc[~unknown_product].copy()
    sales = sales.drop(columns=["_merge"])


    # =========================================================
    # 8. CALCULATE SALES
    # =========================================================
    sales["gross_amount"] = (
        sales["qty"] * sales["unit_price"]
    )

    sales["discount_amount"] = (
        sales["gross_amount"]
        * sales["discount_pct"]
        / 100
    )

    sales["sales_amount"] = (
        sales["gross_amount"]
        - sales["discount_amount"]
    )


    # =========================================================
    # 9. RETURN
    # =========================================================
    return (
        clean_customers,
        clean_products,
        sales,
        rejects
    )