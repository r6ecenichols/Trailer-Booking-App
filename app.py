from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# SQLite DB config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail config from environment variables
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

db = SQLAlchemy(app)
mail = Mail(app)

# Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    date = db.Column(db.String(20))
    trailer_size = db.Column(db.String(50))

# Home / booking form
@app.route('/', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        new_booking = Booking(
            name=request.form['name'],
            email=request.form['email'],
            date=request.form['date'],
            trailer_size=request.form['trailer_size']
        )
        db.session.add(new_booking)
        db.session.commit()

                # Send confirmation email
        msg = Message("Booking Confirmation",
                      recipients=[new_booking.email])
        msg.body = f"""Hi {new_booking.name},

Your trailer is booked for {new_booking.date} (Size: {new_booking.trailer_size}).

Thank you for using our trailer booking service!

This is an automated message."""
        mail.send(msg)


        return render_template('success.html', name=new_booking.name, date=new_booking.date)
    return render_template('book.html')

# View all bookings
@app.route('/bookings')
def view_bookings():
    search = request.args.get('search', '')
    date = request.args.get('date', '')
    
    query = Booking.query
    if search:
        query = query.filter(
            (Booking.name.ilike(f'%{search}%')) |
            (Booking.email.ilike(f'%{search}%'))
        )
    if date:
        query = query.filter(Booking.date == date)

    bookings = query.all()
    return render_template('bookings.html', bookings=bookings)

# Delete a booking
@app.route('/delete/<int:id>', methods=['POST'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return redirect('/bookings')

# Edit a booking
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_booking(id):
    booking = Booking.query.get_or_404(id)
    if request.method == 'POST':
        booking.name = request.form['name']
        booking.email = request.form['email']
        booking.date = request.form['date']
        booking.trailer_size = request.form['trailer_size']
        db.session.commit()
        return redirect('/bookings')
    return render_template('edit.html', booking=booking)

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
