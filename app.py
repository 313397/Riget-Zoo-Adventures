from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime
import datetime as dt
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
# Get the database for the users, ticket bookings and hotel bookings
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////Users/priyanshuagarwal/Downloads/Task 2 (Summer 24)/Riget_Zoo_Adventures_DB.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Used for managing Flask-Login for logging a user in and out
login_manager = LoginManager()
login_manager.init_app(app)
# Used for the tables in the database
class Base(DeclarativeBase):
    pass

# Used to create a class for the users table in the database for the user ID, name, email and password
# Specifies the data type for each of the fields and primary key, foreign key, autoincrement or null
class Users(UserMixin, db.Model):
    __tablename__ = 'Users'
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(1000), nullable=False)
# Represent the user ID for the user
    def __repr__(self):
        return f'<Session {self.user_id}>'
# Return the user ID for the user
    def get_id(self):
        return str(self.user_id)

# Used to create a class for the ticket bookings table in the database for the booking ID, user ID, number of tickets, time and date
# Specifies the data type for each of the fields and primary key, foreign key, autoincrement or null
class Ticket_Bookings(db.Model):
    __tablename__ = 'Ticket_Bookings'
    booking_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('Users.user_id'))
    number_of_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[str] = mapped_column(String(100), nullable=False)
# Represent the booking ID for the ticket booking
    def __repr__(self):
        return f'<Session {self.booking_id}>'
# Return the booking ID for the ticket booking
    def get_id(self):
        return str(self.booking_id)

# Used to create a class for the hotel bookings table in the database for the booking ID, user ID, number of people, time, date and room number
# Specifies the data type for each of the fields and primary key, foreign key, autoincrement or null
class Hotel_Bookings(db.Model):
    __tablename__ = 'Hotel_Bookings'
    booking_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('Users.user_id'))
    number_of_people: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    room_number: Mapped[int] = mapped_column(Integer)

# Return the booking ID for the hotel booking
    def __repr__(self):
        return f'<Session {self.booking_id}>'
# Return the booking ID for the hotel booking
    def get_id(self):
        return str(self.booking_id)

# Loads a user and gets the user from the database
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


with app.app_context():
    db.create_all()

# Route the user to the home page when they run the application
@app.route("/")
def index():
    return render_template("index.html", logged_in=current_user.is_authenticated)

# Route the user to the about us page when they click on about us on the navigation bar
@app.route("/about_us")
def about_us():
    return render_template("about_us.html", logged_in=current_user.is_authenticated)

# Route the user to the contact us page when they click on contact us o n the navigation bar
@app.route("/contact_us")
def contact_us():
    return render_template("contact_us.html", logged_in=current_user.is_authenticated)

# Route the user to the attractions and facilities page when they click on attractions and facilities on the navigation bar
@app.route("/attractions_and_facilities")
def attractions_and_facilities():
    return render_template("attractions_and_facilities.html", logged_in=current_user.is_authenticated)

# Route the user to the educational visits page when they click on educational visits on the navigation bar
@app.route("/educational_visits")
def educational_visits():
    return render_template("educational_visits.html", logged_in=current_user.is_authenticated)

# Route the user to the reserve book zoo tickets page when they click on reserve and book tickets for zoo on the navigation bar
@app.route("/reserve_book_zoo_tickets", methods=["GET", "POST"])
def reserve_book_zoo_tickets():
    if not current_user.is_authenticated: # Checks if a user isn't logged in when accessing the page
        flash("You must be logged in to reserve and book tickets for the zoo")
        return redirect(url_for('login')) # Redirects to the login page if a user isn't logged in
    
    if request.method == 'POST':
            number_of_tickets = request.form.get('number_of_tickets') # Gets the number of tickets from the user
            time = request.form.get('time') # Gets the time from the dropdown list
            day = request.form.get('DD') # Gets the day in DD format from the DD field
            month = request.form.get('MM') # Gets the month in MM format from the MM field
            year = request.form.get('YYYY') # Gets the year in YYYY format from the YYYY field

            if len(day) != 2 or len(month) != 2: # Validate that day and month are exactly two digits
                if len(day) > 2 or len(month) > 2:
                    flash("The date entered is invalid")  # If day or month have three or more digits
                    return redirect(url_for('reserve_book_zoo_tickets'))
                flash("The day and month must be entered as two digits (e.g. '01' for January, '09' for the 9th day)")
                return redirect(url_for('reserve_book_zoo_tickets')) # Stay on the reserve and book tickets for zoo page if day or month isn't 2 digits
            # validate the number of tickets to check that it is not any value other than a number
            try:
                int(number_of_tickets) # convert number of tickets to an integer
            except:
                flash("Number of tickets entered is invalid") # If number of tickets is not a number
                return redirect(url_for('reserve_book_zoo_tickets')) # Stay on same page if number of tickets is not a number
            else:
                if int(number_of_tickets) < 0 or int(number_of_tickets) == 0:
                    flash("Number of tickets must be a positive number and greater than 0")
                    return redirect(url_for('reserve_book_zoo_tickets')) # Stay on same page if number of tickets is not a number
            date = f"{day}/{month}/{year}" # Converts the date entered by the user into DD/MM/YYYY format
            new_booking = Ticket_Bookings(
            number_of_tickets=number_of_tickets, # gets the number of tickets for the number of tickets field in the database
            time=time, # gets the time for the time field in the database
            date=date, # gets the date for the date field in the database
            user_id=current_user.user_id,
            )
            try:
                date = datetime.strptime(date, "%d/%m/%Y") # Convert the date input to DD/MM/YYYY format
            except ValueError: 
                flash("The date entered is invalid") # Validate if the date is either not entered as a numerical value or is more than the maximum values e.g. month is more than 12 or less than 01
                return redirect(url_for('reserve_book_zoo_tickets')) # Stay on the reserve and book tickets for zoo page if the date entered is invalid
            
            if int(day) < 1 or int(day) > 31 or int(month) < 1 or int(month) > 12:
                flash("The date entered is invalid")  # If day or month is out of valid range
                return redirect(url_for('reserve_book_zoo_tickets'))

            # Ensure the date is a valid calendar date
            try:
            # This will raise an error if the day/month combination is not valid
                datetime(int(year), int(month), int(day))
            except:
                flash("The date entered is invalid")  # Catch invalid dates like 31/11 or 30/02
                return redirect(url_for('reserve_book_zoo_tickets'))  # Stay on the reserve and book tickets for zoo page if the date is invalid

            now = date.today() # Gets the date today
            if date < now: # Checks if the date is in the past
                flash("The date entered is in the past") # Displays a message if the date entered is in the past
                return redirect(url_for('reserve_book_zoo_tickets')) # Stay on the reserve and book tickets for zoo page if the date entered is in the past
            db.session.add(new_booking) # Adds a new booking to the database
            db.session.commit() # Commits the booking to the database
            return render_template("success.html") # Redirects to the success page after the booking is made
    return render_template("reserve_book_zoo_tickets.html", logged_in=current_user.is_authenticated)

# Route the user to the book hotel stay page when they click on book stay at hotel on the navigation bar
@app.route("/book_hotel_stay", methods=["GET", "POST"])
def book_hotel_stay():
    if not current_user.is_authenticated: # Checks if a user isn't logged in when accessing the page
        flash("You must be logged in to book a stay at the hotel")
        return redirect(url_for('login')) # Redirects to the login page if a user isn't logged in
    
    if request.method == 'POST':
        number_of_people = request.form.get('number_of_people') # Gets the number of people from the user
        time = request.form.get('time') # Gets the time from the dropdown list
        day = request.form.get('DD') # Gets the day in DD format from the DD field
        month = request.form.get('MM') # Gets the month in MM format from the MM field
        year = request.form.get('YYYY') # Gets the year in YYYY format from the YYYY field

        if len(day) != 2 or len(month) != 2: # Validate that day and month are exactly two digits
            if len(day) > 2 or len(month) > 2:
                flash("The date entered is invalid")  # If day or month have three or more digits
                return redirect(url_for('book_hotel_stay'))
            flash("The day and month must be entered as two digits (e.g. '01' for January, '09' for the 9th day)")
            return redirect(url_for('book_hotel_stay')) # Stay on the book hotel stay page if day or month isn't 2 digits
        # validate the number of people to check that it is not any value other than a number
        try:
            int(number_of_people) # convert number of people to an integer
        except:
            flash("Number of people entered is invalid") # If number of people is not a number
            return redirect(url_for('book_hotel_stay'))
        else:
            if int(number_of_people) < 0 or int(number_of_people) == 0:
                flash("Number of people must be a positive number and greater than 0")
                return redirect(url_for('book_hotel_stay')) # Stay on same page if number of people is not a number
        
        date = f"{day}/{month}/{year}" # Converts the date entered by the user into DD/MM/YYYY format
        new_booking = Hotel_Bookings(
        number_of_people=number_of_people, # gets the number of tickets for the number of tickets field in the database
        time=time, # gets the time for the time field in the database
        date=date, # gets the date for the date field in the database
        user_id=current_user.user_id,
        )
        try:
            date = datetime.strptime(date, "%d/%m/%Y") # Convert the date input to DD/MM/YYYY format
        except ValueError: 
            flash("The date entered is invalid") # Validate if the date is either not entered as a numerical value or is more than the maximum values e.g. month is more than 12 or less than 01
            return redirect(url_for('book_hotel_stay')) # Stay on the book hotel stay page if the date entered is invalid
            
        if int(day) < 1 or int(day) > 31 or int(month) < 1 or int(month) > 12:
            flash("The date entered is invalid")  # If day or month is out of valid range
            return redirect(url_for('book_hotel_stay'))

        # Ensure the date is a valid calendar date
        try:
        # This will raise an error if the day/month combination is not valid
            datetime(int(year), int(month), int(day))
        except ValueError:
            flash("The date entered is invalid")  # Catch invalid dates like 31/11 or 30/02
            return redirect(url_for('book_hotel_stay'))  # Stay on the book hotel stay page if the date is invalid

        now = date.today() # Gets the date today
        if date < now: # Checks if the date is in the past
            flash("The date entered is in the past") # Displays a message if the date entered is in the past
            return redirect(url_for('book_hotel_stay')) # Stay on the book hotel stay page if the date entered is in the past
        db.session.add(new_booking) # Adds a new booking to the database
        db.session.commit() # Commits the booking to the database
        return render_template("success.html") # Redirects to the success page after the booking is made
    return render_template("book_hotel_stay.html", logged_in=current_user.is_authenticated)

# Route the user to the settings page when they click on settings on the navigation bar
@app.route("/settings")
def settings():
    return render_template("settings.html", logged_in=current_user.is_authenticated)

# Route the user to the login page when they click on log in on the navigation bar
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email') # Gets the email entered by the user from the email field
        password = request.form.get('password') # Gets the password entered by the user from the password field
        result = db.session.execute(db.select(Users).where(Users.email == email)) # Finds the matching user by their email
        user = result.scalar() # Fetches the user
        if not user:
            flash("That email does not exist, please try again")
            return redirect(url_for('login')) # Stays on the login page if the email doesn't exist
        elif not check_password_hash(user.password, password):
            flash("Incorrect password, please try again") # Stays on the login page if the password is incorrect
            return redirect(url_for('login'))
        else:
            login_user(user) # Logs the user in if their email and password are correct
            flash("You have successfully logged in") # Displays a message to let the user know that they have logged in
            return redirect(url_for('index')) # Redirects to the home page after the user is logged in
    return render_template("login.html", logged_in=current_user.is_authenticated)

# Routes to the register page if a user clicks on register
@app.route("/register", methods=["GET", "POST"])
def register():
     if request.method == "POST":
        email = request.form.get('email') # Gets the email entered by the user from the email field
        name = request.form.get("name") # Gets the name entered from the name field
        result = db.session.execute(db.select(Users).where(Users.email == email)) # Finds the matching user by their email
        user = result.scalar() # Fetches the user
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login')) # Redirects to the login page if the user uses an existing email
        if not re.match(r"^[A-Za-z]+(?:-[A-Za-z]+)?(?:\s[A-Za-z]+(?:-[A-Za-z]+)?)?$", name) or '  ' in name or ' -' in name or '- ' in name: # Checks if the name doesn't meet the criteria
            flash("Name must contain only alphabets, spaces or a single hyphen between two parts and there must be no consecutive spaces or spaces before/after hyphens") # Displays a message to the user if the name doesn't meet the criteria of the name
            return redirect(url_for('register')) # Stays on the register page if the user
        
        hash_and_salted_password = generate_password_hash( # Generates a password hash
            request.form.get('password'), # Gets the password entered by the user from the password field
            method='pbkdf2:sha256', # Method for hashing the password
            salt_length=8 # Number of characters generated for the salt
        )
        new_user = Users( # new user is equal to user in users class
            email=request.form.get('email'), # email in users database retrieved from email field
            password=hash_and_salted_password, # hashes the password
            name=request.form.get('name'), # Gets the name entered by the user from the name field
        )
        db.session.add(new_user) # Adds a new user to the database
        db.session.commit() # Commits the user to the database
        login_user(new_user) # Registers the user
        flash("You have successfully registered") # Displays a message to let the user know that they have registered
        return redirect(url_for("index")) # Redirects to the home page after the user has registered
     
     return render_template("register.html", logged_in=current_user.is_authenticated)

# Routes to logging out a user
@app.route("/logout")
def logout():
    logout_user() # Logs a user out
    flash("You have successfully logged out") # Displays a message to let the user know that they have logged out
    return redirect(url_for('index')) # Redirects to the home page after a user is logged out







