import os
import psycopg2
from flask import Flask, request, jsonify
from psycopg2.extras import RealDictCursor
import time

app = Flask(__name__)

# DB configuration for Docker Compose
DB_HOST = os.environ.get("DATABASE_HOST", "db")
DB_NAME = os.environ.get("POSTGRES_DB", "frostbyte")
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")


def wait_for_db():
    """Wait until the database is ready to accept connections"""
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            print("Waiting for database...")
            time.sleep(1)


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database not reachable")
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(query, params)
        if fetch_one:
            result = cur.fetchone()
            conn.commit()
            return result
        if fetch_all:
            result = cur.fetchall()
            return result
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ---- All your routes stay the same ----

# Example:
@app.route('/locations', methods=['POST'])
def create_location():
    data = request.get_json()
    try:
        query = """
            INSERT INTO locations (name, type, city) 
            VALUES (%s, %s, %s) RETURNING id, name, type, city;
        """
        new_loc = execute_query(query, (data['name'], data['type'], data['city']), fetch_one=True)
        return jsonify(new_loc), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---- other routes remain exactly as before ----


if __name__ == '__main__':
    wait_for_db()
    app.run(host='0.0.0.0', port=8000)
