import sqlite3
from Project.config import DATABASE

themes = [ (_,) for _ in (["Смешная история", "Отчет", "Грустная история", "Обыкновенная запись"])]
statuses = [ (_,) for _ in (["Написан", "Дописывается", "Не написан"])]

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE notes (
                            note_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            note_name TEXT NOT NULL,
                            date INTEGER,
                            soder TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE themes (
                            theme_id INTEGER PRIMARY KEY,
                            theme_name TEXT
                        )''')
            conn.execute('''CREATE TABLE note_themes (
                            note_id INTEGER,
                            theme_id INTEGER,
                            FOREIGN KEY(note_id) REFERENCES notes(note_id),
                            FOREIGN KEY(theme_id) REFERENCES theme(theme_id)
                        )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()
        print("База данных успешно создана.")

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
            

    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO themes (theme_name) values(?)'
        data = themes
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)


    def insert_note(self, data):
        sql = 'INSERT OR IGNORE INTO notes (user_id, note_name, soder, status_id) values(?, ?, ?, ?)'
        self.__executemany(sql, data)

    def insert_themes(self, user_id, note_name, skill):
        sql = 'SELECT note_id FROM notes WHERE note_name = ? AND user_id = ?'
        note_id = self.__select_data(sql, (note_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT theme_id FROM themes WHERE theme_name = ?', (skill,))[0][0]
        data = [(note_id,skill_id)]
        sql = 'INSERT OR IGNORE INTO note_theme VALUES (?, ?)'
        self.__executemany(sql, data)

  
    def get_statuses(self):
        sql='SELECT status_name from status'
        return self.__select_data(sql)
        
    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_notes(self, user_id):
        return self.__select_data(sql='SELECT * FROM notes WHERE user_id = ?', data = (user_id,))

    def get_note_id(self, note_name, user_id):
        return self.__select_data(sql='SELECT note_id FROM notes WHERE note_name = ? AND user_id = ?  ', data = (note_name, user_id,))[0][0]

    def get_themes(self):
        return self.__select_data(sql='SELECT * FROM themes')
    
    def get_note_themes(self, note_name):
        res = self.__select_data(sql='''SELECT theme_name FROM notes 
JOIN note_themes ON notes.note_id = note_themes.note_id 
JOIN themes ON themes.theme_id = note_themes.theme_id 
WHERE note_name = ?''', data = (note_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_note_info(self, user_id, note_name):
        sql = """
SELECT note_name, date, soder, status_name FROM notes 
JOIN status ON
status.status_id = notes.status_id
WHERE note_name=? AND user_id=?
"""
        return self.__select_data(sql=sql, data = (note_name, user_id))
    

    def update_notes(self, param, data):
        self.__executemany(f"UPDATE notes SET {param} = ? WHERE note_name = ? AND user_id = ?", [data]) # data ('atr', 'mew', 'name', 'user_id')


    def delete_note(self, user_id, note_id):
        sql = "DELETE FROM notes WHERE user_id = ? AND note_id = ? "
        self.__executemany(sql, [(user_id, note_id)])

    def delete_theme(self, note_id, skill_id):
        sql = "DELETE FROM themes WHERE theme_id = ? AND note_id = ? "
        self.__executemany(sql, [(skill_id, note_id)])


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()
