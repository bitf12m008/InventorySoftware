import sqlite3
from app.db.database_init import get_connection

class ProfitReportModel:

    @staticmethod
    def get_profit_report(shop_id, start_date, end_date):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                si.product_id,
                p.name AS product_name,
                si.quantity,
                si.price_per_unit,
                si.line_total,
                COALESCE((
                    SELECT pr.price
                    FROM Purchases pr
                    WHERE pr.product_id = si.product_id
                      AND pr.shop_id = s.shop_id
                      AND date(pr.date) <= date(s.date)
                    ORDER BY date(pr.date) DESC, pr.purchase_id DESC
                    LIMIT 1
                ), 0) AS purchase_price
            FROM SaleItems si
            JOIN Sales s ON s.sale_id = si.sale_id
            JOIN Products p ON p.product_id = si.product_id
            WHERE s.shop_id = ?
              AND date(s.date) BETWEEN date(?) AND date(?)
            ORDER BY p.name
        """, (shop_id, start_date, end_date))

        sale_items = cur.fetchall()

        if not sale_items:
            conn.close()
            return []

        report = {}

        for row in sale_items:
            pid = row["product_id"]
            qty = row["quantity"]
            sale_price = row["price_per_unit"]
            sale_total = row["line_total"]
            purchase_price = row["purchase_price"]

            profit_per_unit = sale_price - purchase_price
            total_profit = profit_per_unit * qty
            purchase_cost = purchase_price * qty

            if pid not in report:
                report[pid] = {
                    "product_id": pid,
                    "product_name": row["product_name"],
                    "qty_sold": 0,
                    "sale_total": 0,
                    "purchase_cost": 0,
                    "profit_per_unit": profit_per_unit,
                    "total_profit": 0
                }

            report[pid]["qty_sold"] += qty
            report[pid]["sale_total"] += sale_total
            report[pid]["purchase_cost"] += purchase_cost
            report[pid]["total_profit"] += total_profit

        conn.close()
        return list(report.values())
