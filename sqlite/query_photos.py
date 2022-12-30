
import os
import sqlite3
from datetime import datetime
from pprint import pprint

class MediaConnection:
    """The Purpose of this Class is to handle the connection to sqlite in the Mac OS Photos Application.

    When the main method is called, it establishes a connection and prints out some useful information to the console."""

    # Get into the directory so we have access to the sqlite database
    def __init__(self):
        print("#----------------------------------Media Connection----------------------------------#")

        # Default directory stored into by the 'Photos' application
        os.chdir("/Users/erikdkosberg/Pictures")

        # Photos\Photo Library.photolibrary
        path = os.listdir()[-1]
        os.chdir(path)

        # This is where the sqlite tables are
        os.chdir("database")

        # So we can index multiple cursors individually
        self.cursor_count = 0

    # Connect to the database; return True if the connection was successful
    def connect(self) -> bool:
        try:
            self.con = sqlite3.connect("Photos.sqlite")
            return True

        except ConnectionError as e:
            print(e)
            return False

    # Open up a cursor to an already successful connection; separate function to allow multiple cursors
    def curse(self) -> bool:
        try:
            self.cursor = self.con.cursor()
            self.cursor_count += 1
            return True

        except ConnectionError as e:
            print(e)
            return False            

    # Get a list of all table names
    def get_table_names(self) -> list:
        query = """SELECT name FROM sqlite_master WHERE type='table' ORDER BY [Name];"""

        self.cursor.execute(query)
        tables = [z[0] for z in self.cursor.fetchall()]
        return tables

    # Get a list of all columns based on the table name
    def column_names_and_types(self, table) -> list:
        query = f"""PRAGMA table_info({table});"""

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_data_by_column(self, table, column, max_count=0) -> list:
        query = f"""SELECT {column} FROM {table}"""

        self.cursor.execute(query)
        return self.cursor.fetchall()

    # Example of accessing the top 50 rows of a given table - so we dont have to look through everything
    def get_top_50_rows(self, table) -> list:
        query = f"""SELECT * FROM {table} LIMIT 5"""

        self.cursor.execute(query)
        return self.cursor.fetchall()


    # Example of accessing all rows for a given table
    def get_rows(self, table) -> list:
        query = f"""SELECT * FROM {table}"""

        self.cursor.execute(query)
        return self.cursor.fetchall()


    # Main function - call internal methods
    def main(self):
        self.connect()
        self.curse()

        path = os.getcwd()

        for root, dirs, files in os.walk(path):
            for file in files:
        
                # change the extension from '.mp3' to
                # the one of your choice.
                if file.endswith('.HEIC'):
                    print (root+'/'+str(file))

        table_names = self.get_table_names()
        
        num_tables = len(table_names)

        max_count = None

        for i, table in enumerate(table_names[:max_count]):
            print(f"[TABLE COLLECTION] {datetime.now()}")
            print(f"Table {i+1} of {num_tables}")
            print(f"Name: {table}\n")

            top_5_data_records = self.get_top_50_rows(table)

            column_types = self.column_names_and_types(table)
            column_names = [z[1] for z in column_types]

            table_data = self.get_rows(table)
            
            print(f"The column names are: {column_names}\n")


            #print("These are the columns found in this table...\n")
            #pprint(column_names)
            print()


if __name__ == '__main__':
    obj = MediaConnection()
    obj.main()

    print("...THE END")
