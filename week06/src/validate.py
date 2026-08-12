import sqlite3
from .config import WAREHOUSE_DB


def validate_data(source_sales):
    """
    Validate transformed sales against warehouse data.

    Return:
        source_valid_rows
        warehouse_rows
        duplicate_order_ids
        warehouse_total_sales
        source_total_sales
        status
    """

    # จำนวน records หลัง Transform
    source_valid_rows = len(source_sales)

    # ยอดขายรวมจาก transformed data
    source_total_sales = float(
        source_sales["sales_amount"].sum()
    )

    # เปิด warehouse
    conn = sqlite3.connect(WAREHOUSE_DB)

    try:
        cursor = conn.cursor()

        # จำนวน records ใน fact_sales
        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_sales
        """)

        warehouse_rows = cursor.fetchone()[0]

        # ตรวจ duplicate order_id
        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT order_id
                FROM fact_sales
                GROUP BY order_id
                HAVING COUNT(*) > 1
            )
        """)

        duplicate_order_ids = cursor.fetchone()[0]

        # ยอดขายรวมจาก warehouse
        cursor.execute("""
            SELECT COALESCE(SUM(sales_amount), 0)
            FROM fact_sales
        """)

        warehouse_total_sales = float(
            cursor.fetchone()[0]
        )

    finally:
        conn.close()

    # ตรวจสอบว่า Transform และ Warehouse ตรงกันหรือไม่
    status = "PASS"

    if source_valid_rows != warehouse_rows:
        status = "FAIL"

    if duplicate_order_ids != 0:
        status = "FAIL"

    if abs(source_total_sales - warehouse_total_sales) > 0.01:
        status = "FAIL"

    return {
        "source_valid_rows": source_valid_rows,
        "warehouse_rows": warehouse_rows,
        "duplicate_order_ids": duplicate_order_ids,
        "warehouse_total_sales": warehouse_total_sales,
        "source_total_sales": source_total_sales,
        "status": status
    }