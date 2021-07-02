import sqlite3
from sqlite3 import Error
from config import DB_FILE

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, ddl_sql):
    """ create a table from the ddl_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(ddl_sql)
    except Error as e:
        print(e)


def main():

    ddl_duo_langs = """CREATE TABLE duo_langs (
        id   VARCHAR (3)  PRIMARY KEY NOT NULL,
        lang VARCHAR (50) UNIQUE NOT NULL,
        taal VARCHAR (50) UNIQUE NOT NULL
        );"""

    ddl_duo_data = """CREATE TABLE duo_data (
        id                   VARCHAR (3) NOT NULL,
        date                 DATE        NOT NULL,
        points               INTEGER,
        level                INTEGER,
        level_progress       INTEGER,
        level_percent        INTEGER,
        level_points         INTEGER,
        level_left           INTEGER,
        next_level           INTEGER,
        num_skills_learned   INTEGER,
        points_rank          INTEGER,
        PRIMARY KEY (id ASC, date ASC),
        FOREIGN KEY (id) REFERENCES duo_langs (id)
        );"""

    ddl_duo_status = """CREATE TABLE duo_status (
        id                   VARCHAR (3) NOT NULL,
        points               INTEGER,
        level                INTEGER,
        level_progress       INTEGER,
        level_percent        INTEGER,
        level_points         INTEGER,
        level_left           INTEGER,
        next_level           INTEGER,
        num_skills_learned   INTEGER,
        points_rank          INTEGER,
        streak_start         DATE,
        streak_end           DATE,
        PRIMARY KEY (id ASC),
        FOREIGN KEY (id) REFERENCES duo_langs (id)
        );"""



    # create a database connection
    conn = create_connection(DB_FILE)

    # create tables
    if conn is not None:
        create_table(conn, ddl_duo_langs)
        create_table(conn, ddl_duo_data)
        create_table(conn, ddl_duo_status)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()