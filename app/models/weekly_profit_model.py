import sqlite3
from app.db.database_init import get_connection

class WeeklyProfitModel:

    @staticmethod
    def get_weekly_profit(shop_id, start_date=None, end_date=None):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()

        query = """
            SELECT
                strftime('%Y-W%W', date(s.date, '-2 days')) AS week,
                SUM(si.line_total) AS total_sales,
                SUM(si.quantity * (
                    SELECT price
                    FROM Purchases p
                    WHERE p.product_id = si.product_id
                      AND p.shop_id = s.shop_id
                      AND date(p.date) <= date(s.date)
                    ORDER BY date(p.date) DESC, p.purchase_id DESC
                    LIMIT 1
                )) AS purchase_cost
            FROM Sales s
            JOIN SaleItems si ON si.sale_id = s.sale_id
            WHERE s.shop_id = ?
        """

        params = [shop_id]

        if start_date and end_date:
            query += " AND date(s.date) BETWEEN date(?) AND date(?)"
            params.extend([start_date, end_date])

        query += """
            GROUP BY week
            ORDER BY week DESC
        """

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            sales = r["total_sales"] or 0
            cost = r["purchase_cost"] or 0
            profit = sales - cost

            result.append({
                "week": r["week"],
                "total_sales": sales,
                "purchase_cost": cost,
                "profit": profit
            })

        return result
