import sqlite3

class SQL:
    def __init__(self, filename):
        self._filename = filename
        self._connection = sqlite3.connect(filename.replace("sqlite:///", ""))
        self._cursor = self._connection.cursor()

    def execute(self, *args, **kwargs):
        self._cursor.execute(*args, **kwargs)
        return self.cursor.fetchall()

