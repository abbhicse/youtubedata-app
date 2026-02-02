import sqlite3
import pandas as pd
import logging
import os

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/database.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def connect_to_db(db_file="global_electronics.db"):
    try:
        conn = sqlite3.connect(db_file)
        logging.info(f"Connected to SQLite DB at {db_file}")
        return conn
    except Exception as e:
        logging.error(f"SQLite connection error: {e}")
        raise

def create_table(conn, drop_existing=True):
    cursor = conn.cursor()
    try:
        if drop_existing:
            cursor.execute("DROP TABLE IF EXISTS Global_Electronics_Master")
            logging.info("Dropped existing table Global_Electronics_Master.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Global_Electronics_Master (
            Order_Number TEXT,
            Line_Item INTEGER,
            Order_Date TEXT,
            Delivery_Date TEXT,
            Customer_ID TEXT,
            Store_ID TEXT,
            Product_ID TEXT,
            Currency TEXT,
            Quantity INTEGER,
            Unit_Cost REAL,
            Unit_Price REAL,
            Customer_Name TEXT,
            Gender TEXT,
            Birthday TEXT,
            DOB TEXT,
            Age INTEGER,
            Product_Name TEXT,
            Category TEXT,
            Sub_Category TEXT,
            Store_Name TEXT,
            Store_Location TEXT,
            Store_Size REAL,
            Open_Date TEXT,
            Exchange_Rate REAL,
            Revenue REAL,
            Cost REAL,
            Profit REAL
        );
        """)
        conn.commit()
        logging.info("Created table Global_Electronics_Master.")
    finally:
        cursor.close()

def insert_csv_to_sqlite(conn, csv_path):
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)

    try:
        df.to_sql("Global_Electronics_Master", conn, if_exists="append", index=False)
        logging.info(f"Inserted {len(df)} rows into Global_Electronics_Master.")
    except Exception as e:
        logging.error(f"Data insert failed: {e}")
        raise

def run_query(conn, query):
    return pd.read_sql_query(query, conn)

def run_all_queries(conn):
    queries = {
        "Total Revenue & Profit": """
            SELECT ROUND(SUM(Revenue), 2) AS Total_Revenue, ROUND(SUM(Profit), 2) AS Total_Profit
            FROM Global_Electronics_Master;
        """,
        "Monthly Revenue Trend": """
            SELECT substr(Order_Date, 1, 7) AS Month, ROUND(SUM(Revenue), 2) AS Monthly_Revenue
            FROM Global_Electronics_Master
            GROUP BY Month ORDER BY Month;
        """,
        "Top Products by Quantity": """
            SELECT Product_ID, Product_Name, SUM(Quantity) AS Total_Quantity
            FROM Global_Electronics_Master
            GROUP BY Product_ID, Product_Name
            ORDER BY Total_Quantity DESC LIMIT 5;
        """,
        "Most Profitable Products": """
            SELECT Product_ID, Product_Name, ROUND(SUM(Profit), 2) AS Total_Profit
            FROM Global_Electronics_Master
            GROUP BY Product_ID, Product_Name
            ORDER BY Total_Profit DESC LIMIT 5;
        """,
        "Customer Age Grouping": """
            SELECT CASE 
                WHEN Age BETWEEN 18 AND 25 THEN '18-25'
                WHEN Age BETWEEN 26 AND 35 THEN '26-35'
                WHEN Age BETWEEN 36 AND 45 THEN '36-45'
                WHEN Age BETWEEN 46 AND 60 THEN '46-60'
                ELSE '60+'
            END AS Age_Group,
            COUNT(DISTINCT Customer_ID) AS Num_Customers
            FROM Global_Electronics_Master
            GROUP BY Age_Group ORDER BY Age_Group;
        """,
        "Top Stores by Revenue": """
            SELECT Store_ID, Store_Name, ROUND(SUM(Revenue), 2) AS Total_Revenue
            FROM Global_Electronics_Master
            GROUP BY Store_ID, Store_Name
            ORDER BY Total_Revenue DESC;
        """,
        "Profit by Category": """
            SELECT Category, Sub_Category, ROUND(SUM(Profit), 2) AS Total_Profit
            FROM Global_Electronics_Master
            GROUP BY Category, Sub_Category
            ORDER BY Total_Profit DESC;
        """,
        "Revenue by Currency": """
            SELECT Currency, ROUND(SUM(Revenue), 2) AS Total_Revenue
            FROM Global_Electronics_Master
            GROUP BY Currency
            ORDER BY Total_Revenue DESC;
        """,
        "Average Order Value per Customer": """
            SELECT Customer_ID, Customer_Name,
                ROUND(SUM(Revenue)*1.0 / COUNT(DISTINCT Order_Number), 2) AS Avg_Order_Value
            FROM Global_Electronics_Master
            GROUP BY Customer_ID, Customer_Name
            ORDER BY Avg_Order_Value DESC LIMIT 10;
        """,
        "Top Customers by Revenue": """
            SELECT Customer_ID, Customer_Name, ROUND(SUM(Revenue), 2) AS Total_Revenue
            FROM Global_Electronics_Master
            GROUP BY Customer_ID, Customer_Name
            ORDER BY Total_Revenue DESC LIMIT 10;
        """
    }

    for title, query in queries.items():
        logging.info(f"Running query: {title}")
        df = run_query(conn, query)
        print(f"\n--- {title} ---")
        print(df.to_string(index=False))

# -------------------- MAIN ENTRY (for CLI usage) --------------------
if __name__ == "__main__":
    db_file = "global_electronics.db"
    csv_file = "output/Global_Electronics_Master.csv"  # Adjust path if needed

    try:
        conn = connect_to_db(db_file)
        create_table(conn)
        insert_csv_to_sqlite(conn, csv_file)
        run_all_queries(conn)
    finally:
        conn.close()
        logging.info("SQLite connection closed.")
