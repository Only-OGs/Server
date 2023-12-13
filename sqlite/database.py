import sqlite3
import logic
import hashlib



class Database:

    def __init__(self, db):
        self.db_name = db
        self.conn = sqlite3.connect(self.db_name)
        self.cr = self.conn.cursor()
        print("database initialized")

    def user_exist(self, username):
        print("check if user exists")
        self.cr.execute(f'SELECT * FROM user WHERE name = ?', (username,))

        if self.cr.fetchall():
            print(f"{username} already existent in database {self.db_name}")
            return True
        return False

    def check_credentials(self, username, passw):
        password = hashlib.sha256(passw.encode()).hexdigest()
        try:
            self.cr.execute(f'SELECT * FROM user WHERE name = ? AND password = ?', (username,password,))
            self.conn.commit()
        except sqlite3.Error as e:
            print("SQLite-Fehler:", e)

        if self.cr.fetchall():
            print(f"correct credentials found for {username} in {self.db_name}")
            return True
        return False

    def add_user(self, username, passw):
        password = hashlib.sha256(passw.encode()).hexdigest()
        print(password)
        print("add user")
        try:
            self.cr.execute(f'''
            INSERT INTO user (name, password, score)
                    VALUES 
                    (?,?,0)
            ''', (username, password,))
            self.conn.commit()
            print("Added ", username, " to database ", self.db_name)
        except sqlite3.Error as e:
            print("SQLite-Fehler:", e)

        return

    def delete_user(self, username):

        return

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

    def migrate(self):
        for user in logic.users.keys():
            print(user, " : ", logic.users[user])
            self.add_user(user, logic.users[user])
        return

