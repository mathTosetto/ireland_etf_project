import os
import pytest
import tempfile
import sqlite3

from datetime import datetime

from utils.database_operations import DatabaseManipulator


@pytest.fixture
def db_creation():
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        db_path = tmpfile.name

    try:
        db_manipulator = DatabaseManipulator(database=db_path)

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='assetInvestments';"
            )
            assert (
                cursor.fetchone() is not None
            ), "assetInvestments table was not created"

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='assetSalesHistory';"
            )
            assert (
                cursor.fetchone() is not None
            ), "assetSalesHistory table was not created"

            cursor.execute("""
                INSERT INTO assetInvestments (ticker, purchaseDate, initialAmount, initialUnitPrice, transactionFee, soldShareStatus)
                VALUES ('IWDA.AS', '2024-11-01', 100, 150.0, 1.0, 'No')
            """)
            cursor.execute("""
                INSERT INTO assetInvestments (ticker, purchaseDate, initialAmount, initialUnitPrice, transactionFee, soldShareStatus)
                VALUES ('GOOGL', '2024-11-01', 50, 200.0, 1.0, 'No')
            """)

            cursor.execute("""
                INSERT INTO assetSalesHistory (investmentId, remainingShares, saleDate, quantitySold, salePrice)
                VALUES (1, 100, '2023-02-01', 0, 0)
            """)
            cursor.execute("""
                INSERT INTO assetSalesHistory (investmentId, remainingShares, saleDate, quantitySold, salePrice)
                VALUES (2, 50, '2023-06-01', 0, 0)
            """)

            conn.commit()

        yield db_manipulator, db_path

    finally:
        os.remove(db_path)


def test_truncate_table(db_creation):
    db_manipulator, db_path = db_creation

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM assetInvestments;")
        assert (
            cursor.fetchone()[0] > 0
        ), "assetInvestments table should have data before truncation"

        cursor.execute("SELECT COUNT(*) FROM assetSalesHistory;")
        assert (
            cursor.fetchone()[0] > 0
        ), "assetSalesHistory table should have data before truncation"

    db_manipulator.truncate_table()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM assetInvestments;")
        assert (
            cursor.fetchone()[0] == 0
        ), "assetInvestments table should be empty after truncation"

        cursor.execute("SELECT COUNT(*) FROM assetSalesHistory;")
        assert (
            cursor.fetchone()[0] == 0
        ), "assetSalesHistory table should be empty after truncation"


def test_insert_investment(db_creation):
    db_manipulator, db_path = db_creation

    ticker = "TEST"
    purchase_date = datetime.now().strftime("%Y-%m-%d")
    initial_amount = 10
    initial_unit_price = 150.0
    transaction_fee = 1.0
    sold_share_status = "No"

    db_manipulator.insert_investment(
        ticker,
        purchase_date,
        initial_amount,
        initial_unit_price,
        transaction_fee,
        sold_share_status,
    )

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM assetInvestments WHERE ticker = ?", (ticker,))
        investment_row = cursor.fetchone()
        assert investment_row is not None
        assert investment_row[1] == ticker
        assert investment_row[2] == purchase_date
        assert investment_row[3] == initial_amount
        assert investment_row[4] == initial_unit_price
        assert investment_row[5] == transaction_fee
        assert investment_row[6] == sold_share_status

        investment_id = investment_row[0]
        cursor.execute(
            "SELECT * FROM assetSalesHistory WHERE investmentId = ?", (investment_id,)
        )
        sales_row = cursor.fetchone()
        assert sales_row is not None
        assert sales_row[1] == investment_id
        assert sales_row[2] == initial_amount
        assert sales_row[3] is None
        assert sales_row[4] == 0
        assert sales_row[5] == 0


def test_fetch_investments_all(db_creation):
    db_manipulator, _ = db_creation

    investments = db_manipulator.fetch_investments()

    assert len(investments) == 2
    assert investments[0][1] == "IWDA.AS"
    assert investments[1][1] == "GOOGL"


def test_fetch_investments_by_id(db_creation):
    db_manipulator, _ = db_creation

    investments = db_manipulator.fetch_investments(investment_id=1)

    assert len(investments) == 1
    assert investments[0][1] == "IWDA.AS"

    investments = db_manipulator.fetch_investments(investment_id=2)
    assert len(investments) == 1
    assert investments[0][1] == "GOOGL"


def test_update_investments(db_creation):
    db_manipulator, db_path = db_creation

    investment_id = 1
    sold_share_status = "Partially Sold"
    remaining_shares = 80
    sale_date = datetime.now().strftime("%Y-%m-%d")
    quantity_sold = 20
    sale_price = 55.0

    db_manipulator.update_investments(
        investment_id,
        sold_share_status,
        remaining_shares,
        sale_date,
        quantity_sold,
        sale_price,
    )

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT soldShareStatus FROM assetInvestments WHERE id = ?",
            (investment_id,),
        )
        investment_row = cursor.fetchone()
        assert investment_row is not None
        assert investment_row[0] == sold_share_status

        cursor.execute(
            "SELECT * FROM assetSalesHistory WHERE investmentId = ?", (investment_id,)
        )
        sales_row = cursor.fetchall()
        latest_sales_row = sales_row[-1]
        assert latest_sales_row is not None
        assert latest_sales_row[2] == remaining_shares
        assert latest_sales_row[3] == sale_date
        assert latest_sales_row[4] == quantity_sold
        assert latest_sales_row[5] == sale_price
