import sqlite3
from .config import WAREHOUSE_DB


def load_data(customers, products, sales):
    """
    Create/load these tables:
      dim_customer
      dim_product
      fact_sales

    Requirements:
    - customer_id unique in dim_customer
    - product_id unique in dim_product
    - order_id unique in fact_sales
    - running the pipeline twice must NOT duplicate fact_sales
    """

    # Connect to warehouse database
    conn = sqlite3.connect(WAREHOUSE_DB)

    try:
        cursor = conn.cursor()

        # =====================================================
        # 1. Create dim_customer
        # =====================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dim_customer (
                customer_id TEXT PRIMARY KEY,
                name TEXT,
                province TEXT,
                email TEXT
            )
        """)

        # =====================================================
        # 2. Create dim_product
        # =====================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dim_product (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                category TEXT,
                price REAL
            )
        """)

        # =====================================================
        # 3. Create fact_sales
        # =====================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fact_sales (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                product_id TEXT,
                order_date TEXT,
                qty REAL,
                unit_price REAL,
                discount_pct REAL,
                sales_amount REAL
            )
        """)

        # =====================================================
        # 4. Insert customers
        # =====================================================
        customer_columns = [
            "customer_id",
            "name",
            "province",
            "email"
        ]

        customer_rows = customers[customer_columns].itertuples(
            index=False,
            name=None
        )

        cursor.executemany("""
            INSERT OR REPLACE INTO dim_customer
            (customer_id, name, province, email)
            VALUES (?, ?, ?, ?)
        """, customer_rows)

        # =====================================================
        # 5. Insert products
        # =====================================================
        product_columns = [
            "product_id",
            "product_name",
            "category",
            "price"
        ]

        product_rows = products[product_columns].itertuples(
            index=False,
            name=None
        )

        cursor.executemany("""
            INSERT OR REPLACE INTO dim_product
            (product_id, product_name, category, price)
            VALUES (?, ?, ?, ?)
        """, product_rows)

        # =====================================================
        # 6. Insert sales
        # =====================================================
        sales_columns = [
            "order_id",
            "customer_id",
            "product_id",
            "order_date",
            "qty",
            "unit_price",
            "discount_pct",
            "sales_amount"
        ]

        sales_rows = sales[sales_columns].copy()

        # Convert datetime to string for SQLite
        sales_rows["order_date"] = (
            sales_rows["order_date"]
            .astype(str)
        )

        sales_rows = sales_rows.itertuples(
            index=False,
            name=None
        )

        cursor.executemany("""
            INSERT OR IGNORE INTO fact_sales
            (order_id, customer_id, product_id, order_date,
             qty, unit_price, discount_pct, sales_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sales_rows)

        # Save changes
        conn.commit()

    finally:
        conn.close()