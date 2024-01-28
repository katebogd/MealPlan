import sqlite3
import os

environment = "DEV"

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
        result = []
        for row in cursor:
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            result.append(d)
        try:
            database.commit()
        except:
            pass
        return result

