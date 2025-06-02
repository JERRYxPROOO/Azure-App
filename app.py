from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

# Połączenie z bazą danych Azure SQL
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=tcp:filmserver123.database.windows.net,1433;'
    'DATABASE=FilmDB;'
    'UID=adminuser;'
    'PWD=Azure273725;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'rating')
    order = request.args.get('order', 'desc')

    # zabezpieczenie przed SQL injection – dopuszczalne wartości
    valid_sort_fields = ['title', 'rating']
    valid_order = ['asc', 'desc']

    if sort_by not in valid_sort_fields:
        sort_by = 'rating'
    if order not in valid_order:
        order = 'desc'

    cursor = conn.cursor()
    query = f"SELECT * FROM Movies ORDER BY {sort_by} {order.upper()}"
    cursor.execute(query)
    movies = cursor.fetchall()

    return render_template("index.html", movies=movies, sort_by=sort_by, order=order)


@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            rating = float(request.form['rating'])
            cover_url = request.form['cover_url']

            # Walidacja oceny
            if rating < 0 or rating > 10 or (rating * 2) % 1 != 0:
                return "Ocena musi być liczbą od 0 do 10 w krokach co 0.5", 400

            cursor = conn.cursor()
            cursor.execute("INSERT INTO Movies (title, description, rating, cover_url) VALUES (?, ?, ?, ?)",
                           (title, description, rating, cover_url))
            conn.commit()
            return redirect(url_for('index'))
        except ValueError:
            return "Nieprawidłowa wartość oceny – musi być liczbą", 400

    return render_template("add.html")

@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    cursor = conn.cursor()
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            rating = float(request.form['rating'])
            cover_url = request.form['cover_url']

            if rating < 0 or rating > 10 or (rating * 2) % 1 != 0:
                return "Ocena musi być liczbą od 0 do 10 w krokach co 0.5", 400

            cursor.execute("UPDATE Movies SET title=?, description=?, rating=?, cover_url=? WHERE id=?",
                           (title, description, rating, cover_url, movie_id))
            conn.commit()
            return redirect(url_for('index'))
        except ValueError:
            return "Nieprawidłowa wartość oceny – musi być liczbą", 400

    cursor.execute("SELECT * FROM Movies WHERE id=?", (movie_id,))
    movie = cursor.fetchone()
    return render_template("edit.html", movie=movie)

@app.route('/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Movies WHERE id=?", (movie_id,))
    conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
