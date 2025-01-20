import os
import random
from flask import Flask, render_template, request, redirect, send_from_directory, session
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import secrets

# Initialize Firebase app
cred = credentials.Certificate('credentials/dum-charades-firebase-adminsdk-fbsvc-06f76423cf.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://dum-charades-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Firebase reference
ref = db.reference('movies')

# Global variables
previous_movies = []
movies = []
languages = []
categories = []

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/options', methods=['GET', 'POST'])
def options():
    global movies, languages, categories, previous_movies
    languages = []
    categories = []
    previous_movies = []
    movies = []
    print("Options page initialized.")
    return render_template('options.html')

def select_random_movie(movies):
    global previous_movies
    while True:
        i = random.randint(0, len(movies) - 1)
        if i not in previous_movies:
            previous_movies.append(i)
            break
    movie = get_movie_by_id(movies[i])
    print("\nSelected Movie ID:", movies[i])
    print("Movie Data:", movie)
    return render_template('game.html', movie=movie)

def fetch_movies(languages, categories):
    result_movies = []
    all_movies = ref.get()
    for language in languages:
        for category in categories:
            for movie in all_movies:
                if movie.startswith(f"{language} {category}"):
                    print(f"Found Movie: {movie}")
                    result_movies.append(movie)
    return result_movies

# Fetch the movie data by ID from Firebase
def get_movie_by_id(movie_id):
    movie_ref = ref.child(movie_id)
    movie_data = movie_ref.get()
    return movie_data

@app.route('/game', methods=['GET', 'POST'])
def game():
    global movies, languages, categories, previous_movies
    
    if request.method == 'POST':
        if request.form.get('next'):
            if len(previous_movies) >= len(movies):
                return render_template('error.html', message='No more movies left!')
            return select_random_movie(movies)
        elif request.form.get('back'):
            # Reset all global variables
            languages = []
            categories = []
            previous_movies = []
            movies = []
            return redirect('/options')
    
    # Handle initial language and category selection
    if not languages:
        languages = request.form.getlist('languages') or ['hindi', 'kannada', 'telugu']
        categories = request.form.getlist('categories') or ['timeless_classics', 'new_age_blockbusters']
    
    # Fetch and shuffle movies if not already done
    if not movies:
        movies = fetch_movies(languages, categories)
        random.shuffle(movies)
    
    return select_random_movie(movies)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
