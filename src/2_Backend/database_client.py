import sqlite3
from datetime import datetime

DATABASE_FILE = "sqlite.db"
COLS = ["ACK", "CODE", "DF", "DPT", "DST", "Datetime", "GID", "ID", "IN", "LEN", "MAC", "MARK", "OUT", "PREC", "PROTO", "SEQ", "SPT", "SRC", "Status", "TOS", "TTL", "TYPE", "UID", "URGP", "WINDOW"]
class database_client(object):
	def __init__(self):
		self.conn = sqlite3.connect(DATABASE_FILE)
		self.c = self.conn.cursor()
		self.c.execute('CREATE TABLE IF NOT EXISTS "Logs"( "pk" Integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Datetime" DateTime NOT NULL, "Status" Text NOT NULL, "IN" Text, "OUT" Text, "MAC" Text, "SRC" Text, "DST" Text, "LEN" Integer, "PREC" Text, "TTL" Integer, "DF" Boolean, "PROTO" Text, "TYPE" Text, "CODE" Integer, "ID" Integer, "SEQ" Integer, "UID" Integer, "GID" Integer, "MARK" Integer, "TOS" Integer, "SPT" INTEGER, "DPT" INTEGER, "ACK" INTEGER, "WINDOW" INTEGER, "URGP" INTEGER, CONSTRAINT "unique_id" UNIQUE( "pk") );')
		self.c.execute('DELETE FROM "Logs";')
		self.conn.commit()

	def add_log(self, log_str):
		items = log_str.split(' ')
		datetime_str = ' '.join(items[0:4])  # 'Apr  9 09:44:39'
		dt = datetime.strptime(datetime_str, '%b  %d %H:%M:%S').replace(year=datetime.now().year)
		log_items = {'datetime':dt.__str__(), 'status':items[5]}
		for item in items[7:]:
			if '=' in item:
				k, v = item.split('=')
				if k and v and k in COLS:
					log_items[k]=v
		insert_str = 'INSERT INTO "Logs" ( \''+'\',\''.join(list(log_items.keys()))+'\') VALUES (\''+'\',\''.join(list(log_items.values()))+'\');'
		self.c.execute(insert_str)
		self.conn.commit()

