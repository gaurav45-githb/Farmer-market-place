from flask import Flask, render_template,request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"

app.secret_key = 'gaurav459'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Gaurav%403512@localhost:5432/farmers_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class Users(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mno = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(15), nullable=False)

    image = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    des = db.Column(db.String(200), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# main home page
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/main")
def main():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        mno = request.form.get("mno")
        password = request.form.get("password")

        user = Users.query.filter_by(mno=mno).first()

        if user and user.password == password:

            session["user"] = user.mno
            flash("Login Successful", "success")
            return redirect(url_for("main"))

        else:
            return "Invalid mobile number or password"

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        mno = request.form.get("mno")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # password match check
        if password != confirm_password:
            return "Passwords do not match"

        # check mobile already exists
        user = Users.query.filter_by(mno=mno).first()

        if user:
            return "Mobile number already registered"

        new_user = Users(
            name=name,
            mno=mno,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Register Successful", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# users = {    
#     'admin' : '123',
#     'abc' : '987'}



# @app.route("/submit", methods=["POST"])
# def submit():
    mno = request.form.get("mno")
    password = request.form.get("password")
    
    if mno in users and password == users[mno]:
        session['user'] = mno
        return render_template("index.html")
    else:
        return render_template('login.html')
    
        

@app.route("/addproduct", methods=["GET","POST"])
def addproduct():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        pname = request.form.get("pname")
        price = request.form.get("price")
        contact = request.form.get("contact")

        image = request.files.get("image")
        category = request.form.get("category").lower()
        desc = request.form.get("desc")
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        user = Users.query.filter_by(mno=session["user"]).first()

        product = Product(
            pname=pname,
            price=price,
            contact=contact,
            image=filename,
            category=category,
            des=desc,
            user_id=user.id
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added Successfully ", "success")
        return redirect(url_for("dashboard"))

    return render_template("addproduct.html")

@app.route("/category/<cat>")
def category(cat):
    products = Product.query.filter_by(category=cat).all()

    return render_template("category.html", products=products, category=cat)

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/products")
def products():
    products = Product.query.all()
    return render_template("products.html", products=products)

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    user = Users.query.filter_by(mno=session["user"]).first()

    products = Product.query.filter_by(user_id=user.id).all()

    return render_template("dashboard.html", user=user, products=products)


@app.route("/delete_product/<int:id>")
def delete_product(id):
    product = Product.query.get(id)
    user = Users.query.filter_by(mno=session["user"]).first()

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logout, Thank you ", "success")
    return render_template("index.html")



if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)