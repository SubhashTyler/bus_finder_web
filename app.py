from flask import Flask, render_template, request, redirect, url_for
import json
import datetime
import os

app = Flask(__name__)

ROUTES = [
    {"from": "City A", "to": "City B", "bus": "Express 101", "departure": "09:00", "arrival": "12:00"},
    {"from": "City C", "to": "City D", "bus": "Rapid 202", "departure": "14:00", "arrival": "18:00"},
    {"from": "City E", "to": "City F", "bus": "Deluxe 303", "departure": "07:00", "arrival": "11:00"},
]

BOOKINGS_FILE = "data/bookings.json"

def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, 'r') as f:
        return json.load(f)

def save_booking(booking):
    bookings = load_bookings()
    bookings.append(booking)
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=2)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    from_city = request.form['from']
    to_city = request.form['to']
    date = request.form['date']
    matches = [r for r in ROUTES if r['from'].lower() == from_city.lower() and r['to'].lower() == to_city.lower()]
    return render_template('home.html', results=matches, from_city=from_city, to_city=to_city, date=date)

@app.route('/book', methods=['POST'])
def book():
    booking = {
        'from': request.form['from'],
        'to': request.form['to'],
        'date': request.form['date'],
        'bus': request.form['bus']
    }
    save_booking(booking)
    return redirect(url_for('bookings'))

@app.route('/routes')
def routes():
    return render_template('routes.html', routes=ROUTES)

@app.route('/bookings')
def bookings():
    return render_template('bookings.html', bookings=load_bookings())

@app.route('/track')
def track():
    return render_template('track.html')

if __name__ == '__main__':
    app.run(debug=True)
