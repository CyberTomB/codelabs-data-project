import mysql.connector
from dotenv import dotenv_values
import mysql.connector.errorcode
import pandas as pd

DB_USER, DB_PASS, DB_HOST, DB_NAME = dotenv_values(".env").values()

def execute_query(query: str, data = {}):
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME)
    
    try:
        return pd.read_sql(query, conn, index_col='id')
    except mysql.connector.errorcode as e:
        print(f"Something went wrong: {e}")
    finally:
        conn.close()
    