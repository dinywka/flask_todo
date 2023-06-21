from flask import Flask, request, render_template, redirect, url_for
import datetime
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder="templates")

def create_table():
    connection = mysql.connector.connect(
        host='localhost',
        user='dina',
        password='28MySql!',
        database='mydatabase'
    )
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                description VARCHAR(1000),
                datetime DATE
            )
        """)
        print("Table 'posts' created or already exists.")
    except Error as e:
        print("Error while creating or connecting to the 'posts' table:", e)
    finally:
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

@app.route("/")
def home():
    create_table()
    connection = mysql.connector.connect(
        host='localhost',
        user='dina',
        password='28MySql!',
        database='mydatabase'
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, description, datetime FROM posts")
        raw_rows = cursor.fetchall()
        rows = [{"id": i[0], "description": i[1], "datetime": i[2]} for i in raw_rows]
        return render_template('list.html', list=rows)
    except Error as e:
        print("Error while fetching posts from the 'posts' table:", e)
    finally:
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

@app.route("/create", methods=["GET", "POST"])
def view_create():
    if request.method == "GET":
        return render_template('create.html')
    elif request.method == "POST":
        description = request.form.get("description")
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        connection = mysql.connector.connect(
            host='localhost',
            user='dina',
            password='28MySql!',
            database='mydatabase'
        )
        try:
            cursor = connection.cursor()
            query = "INSERT INTO posts (description, datetime) VALUES (%s, %s)"
            values = (description, date)
            cursor.execute(query, values)
            connection.commit()
            print("Data inserted successfully.")
        except Error as e:
            connection.rollback()
            print("Error while inserting data into the 'posts' table:", e)
        finally:
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
