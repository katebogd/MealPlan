import sqlite3
import os

class SQL:
    def __init__(self, filename):
        self._filename = filename
        

    def execute(self, statement, *args):
        connection = sqlite3.connect(
            os.path.join(
                '/www_data/',
                self._filename.replace("sqlite:///", "")))
        cursor = connection.cursor()
        cursor.execute(statement, args)
        return cursor.fetchall()

