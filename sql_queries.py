import mysql.connector as sql
import pandas as pd
import logging
import os

# -------------------- SETUP --------------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/database.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def connect_to_db(host, user, password, database=None):
    try:
        conn = sql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            use_pure=True
        )
        logging.info(f"Connected to MySQL server at {host}, database={database or 'None'}")
        return conn
    except Exception as e:
        logging.error(f"MySQL connection error: {e}")
        raise

def create_database(conn, db_name):
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        conn.commit()
        logging.info(f"Database '{db_name}' created or exists.")
    finally:
        cursor.close()

def create_table(conn, drop_existing=True):
    cursor = conn.cursor()
    try:
        if drop_existing:
            cursor.execute("DROP TABLE IF EXISTS Global_Electronics_Master")
            logging.info("Dropped existing table Global_Electronics_Master.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Global_Electronics_Master (
            Order_Number VARCHAR(255),
            Line_Item INT,
            Order_Date DATE,
            Delivery_Date DATE,
            Customer_ID VARCHAR(255),
            Store_ID VARCHAR(255),
            Product_ID VARCHAR(255),
            Currency VARCHAR(10),
            Quantity INT,
            Unit_Cost FLOAT,
            Unit_Price FLOAT,
            Customer_Name VARCHAR(255),
            Gender VARCHAR(10),
            Birthday DATE,
            DOB DATE,
            Age INT,
            Product_Name VARCHAR(255),
            Category VARCHAR(100),
            Sub_Category VARCHAR(100),
            Store_Name VARCHAR(255),
            Store_Location VARCHAR(255),
            Store_Size FLOAT,
            Open_Date DATE,
            Exchange_Rate FLOAT,
            Revenue FLOAT,
            Cost FLOAT,
            Profit FLOAT
        );
        """)
        conn.commit()
        logging.info("Created table Global_Electronics_Master.")
    finally:
        cursor.close()

def insert_csv_to_mysql(conn, csv_path):
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)  # Replace NaNs with None

    cursor = conn.cursor()
    try:
        columns = df.columns.tolist()
        col_str = ','.join(f"`{col}`" for col in columns)
        placeholders = ','.join(['%s'] * len(columns))
        query = f"INSERT INTO Global_Electronics_Master ({col_str}) VALUES ({placeholders})"

        for _, row in df.iterrows():
            values = tuple(row.values)
            try:
                cursor.execute(query, values)
            except Exception as row_err:
                logging.warning(f"Row insert failed: {row_err}")
        conn.commit()
        logging.info(f"Inserted {len(df)} rows into Global_Electronics_Master.")
    except Exception as e:
        logging.error(f"Bulk insert failed: {e}")
        raise
    finally:
        cursor.close()

def run_query(conn, query):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        return pd.DataFrame(cursor.fetchall())
    finally:
        cursor.close()

def run_all_queries(conn):
    queries = {
        "Total Revenue & Profit": """
            SELECT ROUND(SUM(Revenue), 2) AS Total_Revenue, ROUND(SUM(Profit), 2) AS Total_Profit
            FROM Global_Electronics_Master;
        """,
        "Monthly Revenue Trend": """
            SELECT DATE_FORMAT(Order_Date, '%%Y-%%m') AS Month, ROUND(SUM(Revenue), 2) AS Monthly_Revenue
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
                ROUND(SUM(Revenue)/COUNT(DISTINCT Order_Number), 2) AS Avg_Order_Value
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

# -------------------- MAIN (CLI ENTRY POINT) --------------------
if __name__ == "__main__":
    host = "localhost"
    user = "your_mysql_user"
    password = "your_mysql_password"
    database_name = "global_electronics"
    csv_file = "output/Global_Electronics_Master.csv"  # adjust path as needed

    try:
        # Step 1: Initial DB connection and creation
        conn = connect_to_db(host, user, password)
        create_database(conn, database_name)
        conn.close()

        # Step 2: Reconnect to specific DB
        conn = connect_to_db(host, user, password, database_name)
        create_table(conn)
        insert_csv_to_mysql(conn, csv_file)

        # Step 3: Run analytics queries
        run_all_queries(conn)
    finally:
        conn.close()
        logging.info("MySQL connection closed.")
