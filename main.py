from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
import os
import stripe


YOUR_DOMAIN = 'http://127.0.0.1:5000'
stripe.api_key = 'sk_test_51MnhQTB24jAdJklMUvJBIPFrb6godHZ3t47N823ZOHpfuXmq9us9OAg1wIqWfE3DXPTG19slQLXyUAnwffYXo2zf00Z4vaBN7f'


app = Flask(__name__)
KEY = os.urandom(32)
app.secret_key = KEY  # Change this!

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.app_context().push()



img_cars = ['https://images.unsplash.com/photo-1611298280249-ea1e9c1e28f4?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8MTh8fHxlbnwwfHx8fA%3D%3D&auto=format&fit=crop&w=800&q=60',
            'https://images.unsplash.com/photo-1590316536591-92ba019a7b50?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8NjN8fHxlbnwwfHx8fA%3D%3D&auto=format&fit=crop&w=800&q=60',
            'https://images.unsplash.com/photo-1608319984133-1d0e5e20988e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8MjZ8fHxlbnwwfHx8fA%3D%3D&auto=format&fit=crop&w=800&q=60',
            'https://images.unsplash.com/photo-1591920689160-ee83654e464a?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8MzR8fHxlbnwwfHx8fA%3D%3D&auto=format&fit=crop&w=800&q=60',
            'https://images.unsplash.com/photo-1603831126198-a53fd2a50da5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8Mzl8fHxlbnwwfHx8fA%3D%3D&auto=format&fit=crop&w=800&q=60',
            'https://images.unsplash.com/photo-1621252792374-2b79e3fcf295?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8NDd8fHxlbnwwfHx8fA%3D%3D&auto=format&fit=crop&w=800&q=60']



class Users(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)

class Cars(UserMixin, db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    price = db.Column(db.Integer, unique=True, nullable=False)
    id_price = db.Column(db.String, unique=True, nullable=False)




# Create Database Tables
#db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


log = False
@app.route("/")
def home():

    return render_template("index.html", log=log, user=USER)

@app.route("/sign_in", methods=["GET","POST"])
def sign_in():
    if request.method == "POST":
        name = request.form['user-name']
        email = request.form['email']
        password = request.form['password']
        print(name, email, password)
        if name != '' and email != '' and password != '':
            new_user = Users(
                name = name,
                email = email,
                password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            )
            mail = request.form['email']
            all_emails = Users.query.filter_by(email=mail).first()
            if all_emails:
                flash("You have already sign up this email account.")
                return redirect(url_for('sign_in'))
            else:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                global log, USER
                log = True
                USER = new_user.name


                return redirect(url_for('home', current_user=current_user.id))
        else:
            flash('Please fill all the fields.')
            return redirect(url_for('sign_in'))



    return render_template("sign_in.html")

USER = ''
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if email != '' and password != '':
            user_mail = Users.query.filter_by(email=email).first()
            if user_mail:
                if check_password_hash(user_mail.password, password):
                    login_user(user_mail)
                    global log, USER
                    log = True
                    USER = user_mail.name

                    return redirect(url_for('home', log=log, user=USER))
                else:
                    flash('Password not correct!')
                    return redirect(url_for('login'))
            else:
                flash('Email not correct!')
                return redirect(url_for('login'))
        else:
            flash('Please fill all fields.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    global log, USER
    log = False
    USER = ''
    return redirect(url_for('home', log=log, user=USER))

@app.route("/showroom")
@login_required
def showroom():
    cars_info = Cars.query.all()


    return render_template("showroom.html", log=log, cars=img_cars, user=USER, cars_info=cars_info)


@app.route("/checkout/<int:id>", methods=['GET', 'POST'])
def checkout(id):
    global checkout_car
    checkout_car = Cars.query.get(id)
    img = id - 1

    return render_template('checkout.html', log=log, img_cars=img_cars, user=USER, cars=checkout_car, img=img)

checkout_car = Cars.query.all()


@app.route("/create-checkout-session", methods=["POST"])
def crete_checkout_session():

    try:
        create_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': checkout_car.id_price,
                    'quantity': 1
                },
            ],
            mode='payment',
            success_url = YOUR_DOMAIN +'/success',
            cancel_url = YOUR_DOMAIN +'/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(create_session.url, code=303)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")




if "__main__"  == __name__:
    app.run(debug=True)