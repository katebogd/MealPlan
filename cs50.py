import sqlite3
import os

class SQL:
    def __init__(self, filename):
        self._filename = filename
        self._connection = sqlite3.connect(os.path.join('/www_data/', filename.replace("sqlite:///", "")))
        self._cursor = self._connection.cursor()

    def execute(self, statement, *args):
        self._cursor.execute(statement, args)
        return self.cursor.fetchall()

