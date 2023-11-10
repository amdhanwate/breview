import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="breview",
        user="amdhanwate",
        password="VZqrO0bj3LYD",
        host="ep-cool-mouse-74251756.ap-southeast-1.aws.neon.tech",
        port=5432
    )
    return conn
