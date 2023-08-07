
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

def create_database(csv_file, db_name, table_name):
    # Read data from the CSV file into a DataFrame
    data = pd.read_csv(csv_file)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)

    # Create a SQLAlchemy engine
    engine = create_engine(f'sqlite:///{db_name}')

    # Write the DataFrame to a new table in the database
    data.to_sql(table_name, engine, if_exists='replace', index=False)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    # Replace these variables with your own values
    csv_file_path = "C:\\Users\\TBS1BAN\\Desktop\\Owners_Manual\\web\\\Web_app_1\\TableMRU.csv"
    database_name = 'pms2.db'
    table_name = 'TableMRU_1'

    # Call the function to create the database
    create_database(csv_file_path, database_name, table_name)
