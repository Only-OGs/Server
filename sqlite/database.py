import sqlite3
import hashlib
import logging as log

#
# Diese Klasse kümmert sich um die SQLite Datenbank inklusive aller nötigen Funktionen
#


class Database:

    def __init__(self, db):
        self.db_name = db
        self.conn = sqlite3.connect(self.db_name)
        self.cr = self.conn.cursor()
        self.initialize_db()
        logging.info("database initialized")

    # Überprüft ob User existiert
    def user_exist(self, username):
        logging.info("check if user exists")
        self.cr.execute(f'SELECT * FROM user WHERE name = ?', (username,))

        if self.cr.fetchall():
            logging.info(f"{username} already existent in database {self.db_name}")
            return True
        return False

    # Überprüft ob Login korrekt ist
    def check_credentials(self, username, passw):
        password = hashlib.sha256(passw.encode()).hexdigest()
        try:
            self.cr.execute(f'SELECT * FROM user WHERE name = ? AND password = ?', (username, password,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.info(f"SQLite-Fehler: {e}")

        if self.cr.fetchall():
            logging.info(f"correct credentials found for {username} in {self.db_name}")
            return True
        return False

    # Legt User in der Datenbank
    def add_user(self, username, passw):
        password = hashlib.sha256(passw.encode()).hexdigest()
        logging.info(password)
        logging.info("add user")
        try:
            self.cr.execute(f'''
            INSERT INTO user (name, password, score)
                    VALUES 
                    (?,?,0)
            ''', (username, password,))
            self.conn.commit()
            logging.info(f"Added {username} to database  {self.db_name}")
        except sqlite3.Error as e:
            logging.info("SQLite-Fehler:", e)

        return

    # Erstellt Datenbank falls nicht bereits existent
    def initialize_db(self):
        self.cr.execute('''
            CREATE TABLE IF NOT EXISTS user(
            [user_id] INTEGER PRIMARY KEY, 
            [name] TEXT UNIQUE, 
            [password] TEXT,
            [score] INT
            ) 
        ''')

        self.conn.commit()
