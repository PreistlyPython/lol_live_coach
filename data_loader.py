import pandas as pd
import sqlite3

def load_csv_data(file_path):
    """Load data from a CSV file."""
    return pd.read_csv(file_path)

def load_db_data(file_path):
    """Load data from a SQLite database file."""
    # Connect to the SQLite database
    conn = sqlite3.connect(file_path)
    
    # Query to get the list of tables in the database
    query_tables = "SELECT name FROM sqlite_master WHERE type='table';"
    
    # Execute the query and fetch the results
    tables = conn.execute(query_tables).fetchall()
    
    # Close the connection
    conn.close()
    
    # Extract table names from the query result
    table_names = [table[0] for table in tables]
    
    return table_names

def load_data_from_table(db_path, table_name):
    """Load data from a specific table in the SQLite database."""
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

def print_table_names(file_path):
    """_summary_
    list and return all tables with a .db file

    Args:
        file_path (_string_): File path as a string of the .db file
    """
        # Connect to the SQLite database
    conn = sqlite3.connect(file_path)
    
    # Query to get the list of tables in the database
    query_tables = "SELECT name FROM sqlite_master WHERE type='table';"
    
    # Execute the query and fetch the results
    tables = conn.execute(query_tables).fetchall()
    
    # Extract table names from the query result
    table_names = [table[0] for table in tables]
    
    # Print the table names
    print("Available tables:", table_names)
    
    # Optionally, return the table names for further use
    return table_names

def clean_data(df):
    """
    Clean data from duplicates and "NA".
    pandas df input
    pands df output
    """
    # Handle missing values
    df = df.dropna()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # More preprocessing steps can be added here (e.g., feature engineering)
    return df

if __name__ == "__main__":
        # For testing purposes, replace with your actual database file path
    db_path = "C:\Python\LoL\src\league.db"
    table_names = load_db_data(db_path)
    
    # If you want to load data from all tables
    for table_name in table_names:
        data = load_data_from_table(db_path, table_name)
        print(f"Data from {table_name}:\n", data.head())
    

    