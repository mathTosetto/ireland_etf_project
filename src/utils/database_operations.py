import sqlite3
import logging

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="logs/user_log.log")


class databaseManipulator:
    def __init__(self, database: str) -> None:
        LOGGER.info(f"Initializing database: {database}")
        self.database = database
        self.__create_database()

    def __create_database(self):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assetInvestments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    purchaseDate TEXT NOT NULL,
                    initialAmount INTEGER NOT NULL,
                    initialUnitPrice REAL NOT NULL,
                    transactionFee REAL NOT NULL,
                    soldShareStatus TEXT NOT NULL DEFAULT 'No'
                );
            """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS assetSalesHistory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investmentId INTEGER NOT NULL,
                    remainingShares INTEGER NOT NULL DEFAULT 0,
                    saleDate TEXT,
                    quantitySold INTEGER NOT NULL,
                    salePrice REAL NOT NULL,   
                    FOREIGN KEY (investmentId) REFERENCES investments(id)
                );
            """)
            conn.commit()

    def truncate_table(self):
        tables = ["assetInvestments", "assetSalesHistory"]
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(f"DELETE FROM {table};")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
                conn.commit()

    def insert_investment(
        self,
        ticker,
        purchase_date,
        initial_amount,
        initial_unit_price,
        transaction_fee,
        sold_share_status,
    ):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO assetInvestments (
                        ticker,
                        purchaseDate,
                        initialAmount,
                        initialUnitPrice,
                        transactionFee,
                        soldShareStatus
                    )
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    ticker,
                    purchase_date,
                    initial_amount,
                    initial_unit_price,
                    transaction_fee,
                    sold_share_status,
                ),
            )

            investment_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO assetSalesHistory (
                    investmentId, remainingShares, saleDate, quantitySold, salePrice
                ) VALUES (?, ?, NULL, 0, 0)
            """,
                (investment_id, initial_amount),
            )
            conn.commit()

    def fetch_investments(self, investment_id=None):
        query = f"""
            WITH latestSales AS (
                SELECT
                    sa.investmentId,
                    sa.remainingShares,
                    sa.saleDate,
                    ROW_NUMBER() OVER (PARTITION BY sa.investmentId ORDER BY sa.saleDate DESC) AS rn
                FROM assetSalesHistory sa
            ),
            aggregatedSales AS (
                SELECT
                    investmentId,
                    SUM(quantitySold) AS totalQuantitySold,
                    ROUND(AVG(salePrice), 2) AS avgSalePrice
                FROM assetSalesHistory
                GROUP BY investmentId
            )

            SELECT 
                ai.id AS investmentId,
                ai.ticker,
                ai.purchaseDate,
                ai.initialAmount,
                ai.initialUnitPrice,
                ai.transactionFee,
                ai.soldShareStatus,
                (ai.initialAmount - COALESCE(ag.totalQuantitySold, 0)) AS calculatedRemainingShares,
                ls.saleDate AS last_saleDate,
                ag.totalQuantitySold,
                ag.avgSalePrice
            FROM assetInvestments ai
            LEFT JOIN latestSales ls ON ai.id = ls.investmentId AND ls.rn = 1
            LEFT JOIN aggregatedSales ag ON ai.id = ag.investmentId
        """

        if investment_id is not None:
            query += f"WHERE ai.id = {investment_id}"

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def update_investments(
        self,
        investment_id,
        sold_share_status,
        remaining_shares,
        sale_date,
        quantity_sold,
        sale_price,
    ):
        LOGGER.info(f"Updating tables")
        LOGGER.info(f"investmentId: {investment_id}")
        LOGGER.info(f"sold_share_status: {sold_share_status}")
        LOGGER.info(f"remainingShares: {remaining_shares}")
        LOGGER.info(f"saleDate: {sale_date}")
        LOGGER.info(f"quantitySold: {quantity_sold}")
        LOGGER.info(f"salePrice: {sale_price}")

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE assetInvestments
                SET soldShareStatus = ?
                WHERE id = ?
            """,
                (sold_share_status, investment_id),
            )

            cursor.execute(
                """
                SELECT id FROM assetSalesHistory WHERE investmentId = ?
            """,
                (investment_id,),
            )
            sale_record = cursor.fetchone()
            LOGGER.info(f"Sale_record: {sale_record}")

            if sale_record:
                cursor.execute(
                    """
                    INSERT INTO assetSalesHistory (
                        investmentId, 
                        remainingShares, 
                        saleDate, 
                        quantitySold, 
                        salePrice
                    )
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        investment_id,
                        remaining_shares,
                        sale_date,
                        quantity_sold,
                        sale_price,
                    ),
                )

            conn.commit()

    def temp_function(self, investment_id=None):
        query = f"""
            SELECT
                sa.id,
                sa.investmentId,
                sa.remainingShares,
                sa.saleDate,
                sa.quantitySold,
                sa.salePrice
            FROM assetSalesHistory sa
        """

        if investment_id is not None:
            query += f" WHERE ai.id = {investment_id}"

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()