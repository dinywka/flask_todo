from flask import Flask, request, render_template, redirect, url_for
import datetime
import random
import sqlite3

app = Flask(__name__, template_folder="templates")


def create_table():
    with sqlite3.connect('database/database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                datetime TEXT
            )
        """)


def db_query_sqlite(query, args=None, many=True):
    with sqlite3.connect('database/database.db') as connection:
        cursor = connection.cursor()
        try:
            if args is not None:
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            if many:
                return cursor.fetchall()
            return cursor.fetchone()
        except Exception as error:
            print(f"An error occurred: {error}")
            return None


@app.route("/")
def home():
    create_table()  # Ensure the table exists
    raw_rows = db_query_sqlite("""SELECT id, description, datetime FROM posts""")
    rows = [{"id": i[0], "description": i[1], "datetime": i[2]} for i in raw_rows]
    return render_template('list.html', list=rows)


@app.route("/list", methods=["GET", "POST"])
def view_list():
    """Отображает все публикации"""
    create_table()  # Ensure the table exists
    if request.method == "GET":
        raw_rows = db_query_sqlite("""SELECT id, description, datetime FROM posts""")
        rows = [{"id": i[0], "description": i[1], "datetime": i[2]} for i in raw_rows]
        return render_template('list.html', list=rows)
    elif request.method == "POST":
        search = request.form.get("search")
        raw_rows = db_query_sqlite("""SELECT id, description, datetime FROM posts
        WHERE description LIKE ?
        """, ('%' + search + '%',))
        rows = [{"id": i[0], "description": i[1], "datetime": i[2]} for i in raw_rows]
        return render_template('list.html', list=rows, search=search)


@app.route("/create", methods=["GET", "POST"])
def view_create():
    if request.method == "GET":
        return render_template('create.html')
    elif request.method == "POST":
        description = request.form.get("description")
        date = str(datetime.datetime.now())[:-7]
        with sqlite3.connect('database/database.db') as connection:
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO posts (description, datetime) VALUES (?, ?)""",
                (description, date)
            )
        return redirect(url_for('view_list'))

@app.route("/change", methods=["GET", "POST"])
def view_change():
    """Обновляет уже существующую публикацию"""

    if request.method == "GET":
        pk = request.args.get('pk', default=0, type=int)
        raw_row = db_query_sqlite(
            """SELECT id, description, datetime FROM posts WHERE id = ?""",
            args=(int(pk),), many=False
        )
        new_dict = {"id": raw_row[0], "description": raw_row[1], "datetime": raw_row[2]}
        return render_template('change.html', post=new_dict)
    elif request.method == "POST":
        pk = request.form.get("pk")
        description = request.form.get("description")
        date = str(datetime.datetime.now())[:-7]
        db_query_sqlite(
            f"""UPDATE POSTS SET description = ?, datetime = ? WHERE id = ?""",
            (description, date, pk)
        )
        return redirect(url_for('view_list'), 301)


@app.route("/delete", methods=["GET"])
def view_delete():
    """Удаляет существующую публикацию"""

    pk = request.args.get('pk', default=0, type=int)
    db_query_sqlite(f"""DELETE FROM posts where id = ?""", (pk,))
    return redirect(url_for('view_list'), 301)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
