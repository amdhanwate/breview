import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="brewery",
        user="abhi",
        password="password",
        host="localhost",
    )
    return conn