import sqlite3

# simple database interface
# NOTE: this executed queries without preparing them.
# Not a good practice, but since the database is only
# accessed by the bot (with data from Kraken), we
# should be okay.
class Orders(object):
    __DB_LOCATION = "Database/orders.db"

    def __init__(self):
        self.__conn = sqlite3.connect(Orders.__DB_LOCATION, detect_types=sqlite3.PARSE_COLNAMES)
        self.__cur = self.__conn.cursor()
        self.__create_table()

    def insertOrder(self, txid, curr, vol, cost):
        sql = "INSERT INTO orders (txid, curr, vol, cost) VALUES (?, ?, ?, ?)"
        info = (txid, curr, vol, cost)
        self.__cur.execute(sql, info)
        return self.__cur.lastrowid

    def deleteOrder(self, txid):
        sql = "DELETE FROM orders WHERE txid = ?"
        self.__cur.execute(sql, (txid,))

    def getOrders(self):
        self.__cur.execute("SELECT txid, curr, vol, cost, t '[timestamp]' FROM orders")
        return self.__cur.fetchall()

    def getOrder(self, txid):
        self.__cur.execute("SELECT txid, curr, vol, cost, t '[timestamp]' FROM orders WHERE txid = ?", txid)
        return self.__cur.fetchone()

    def getOldestOrder(self):
        self.__cur.execute("SELECT txid, t '[timestamp]' FROM orders ORDER BY t LIMIT 1")
        return self.__cur.fetchone()

    def getLatestOrder(self):
        self.__cur.execute("SELECT txid, t '[timestamp]' FROM orders ORDER BY t DESC LIMIT 1")
        return self.__cur.fetchone()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.__cur.close()
        if isinstance(exc_value, Exception):
            self.__conn.rollback()
        else:
            self.__conn.commit()
        self.__conn.close()

    def __create_table(self):
        self.__cur.execute("CREATE TABLE IF NOT EXISTS orders (txid TEXT PRIMARY KEY, curr TEXT, vol REAL, cost REAL, t TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

    def printTable(self):
        self.__cur.execute("SELECT * FROM orders")
        print(self.__cur.fetchall())
