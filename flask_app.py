from flask import Flask, request, render_template, redirect, url_for
import datetime
import sqlite3

app = Flask(__name__, template_folder="templates")

DB_FILE = "mydatabase.db"

def create_table():
    connection = sqlite3.connect(DB_FILE)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                datetime DATE
            )
        """)
        print("Table 'posts' created or already exists.")
    except sqlite3.Error as e:
        print("Error while creating or connecting to the 'posts' table:", e)
    finally:
        cursor.close()
        connection.close()
        print("SQLite connection is closed")

@app.route("/")
def home():
    create_table()
    connection = sqlite3.connect(DB_FILE)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, description, datetime FROM posts")
        rows = [{"id": row[0], "description": row[1], "datetime": row[2]} for row in cursor.fetchall()]
        return render_template('list.html', list=rows)
    except sqlite3.Error as e:
        print("Error while fetching posts from the 'posts' table:", e)
    finally:
        cursor.close()
        connection.close()
        print("SQLite connection is closed")

@app.route("/create", methods=["GET", "POST"])
def view_create():
    if request.method == "GET":
        return render_template('create.html')
    elif request.method == "POST":
        description = request.form.get("description")
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        connection = sqlite3.connect(DB_FILE)
        try:
            cursor = connection.cursor()
            query = "INSERT INTO posts (description, datetime) VALUES (?, ?)"
            values = (description, date)
            cursor.execute(query, values)
            connection.commit()
            print("Data inserted successfully.")
        except sqlite3.Error as e:
            connection.rollback()
            print("Error while inserting data into the 'posts' table:", e)
        finally:
            cursor.close()
            connection.close()
            print("SQLite connection is closed")
        return redirect(url_for('home'))

@app.route("/change", methods=["GET", "POST"])
def view_change():
    if request.method == "GET":
        pk = request.args.get('pk', default=0, type=int)
        connection = sqlite3.connect(DB_FILE)
        try:
            cursor = connection.cursor()
            query = "SELECT id, description, datetime FROM posts WHERE id = ?"
            values = (pk,)
            cursor.execute(query, values)
            row = cursor.fetchone()
            if row:
                post = {"id": row[0], "description": row[1], "datetime": row[2]}
                return render_template('change.html', post=post)
            else:
                return redirect(url_for('home'))
        except sqlite3.Error as e:
            print("Error while fetching post from the 'posts' table:", e)
        finally:
            cursor.close()
            connection.close()
            print("SQLite connection is closed")
    elif request.method == "POST":
        pk = request.form.get("pk")
        description = request.form.get("description")
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        connection = sqlite3.connect(DB_FILE)
        try:
            cursor = connection.cursor()
            query = "UPDATE posts SET description = ?, datetime = ? WHERE id = ?"
            values = (description, date, pk)
            cursor.execute(query, values)
            connection.commit()
            print("Data updated successfully.")
        except sqlite3.Error as e:
            connection.rollback()
            print("Error while updating data in the 'posts' table:", e)
        finally:
            cursor.close()
            connection.close()
            print("SQLite connection is closed")
        return redirect(url_for('home'))

@app.route("/delete", methods=["GET"])
def view_delete():
    pk = request.args.get('pk', default=0, type=int)
    connection = sqlite3.connect(DB_FILE)
    try:
        cursor = connection.cursor()
        query = "DELETE FROM posts WHERE id = ?"
        values = (pk,)
        cursor.execute(query, values)
        connection.commit()
        print("Data deleted successfully.")
    except sqlite3.Error as e:
        connection.rollback()
        print("Error while deleting data from the 'posts' table:", e)
    finally:
        cursor.close()
        connection.close()
        print("SQLite connection is closed")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001, debug=True)
