from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "smartquizzer_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

# Database Models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Selection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    skill = db.Column(db.String(50))
    topic = db.Column(db.String(50))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form["username"].strip()
        pwd = request.form["password"].strip()
        if User.query.filter_by(username=uname).first():
            flash("❌ Username already exists.", "danger")
        else:
            db.session.add(User(username=uname, password=pwd))
            db.session.commit()
            flash("✅ Registration successful. Please login.", "success")
            return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"].strip()
        pwd = request.form["password"].strip()
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            flash("✅ Login successful!", "success")
            return redirect("/topics")
        flash("❌ Invalid credentials.", "danger")
    return render_template("login.html")


@app.route("/topics", methods=["GET", "POST"])
def topics():
    if "user_id" not in session:
        return redirect("/login")
    topics_list = ["Mathematics", "Science",
                   "History", "Literature", "Geography"]
    if request.method == "POST":
        db.session.add(Selection(
            user_id=session["user_id"],
            skill=request.form["skill"],
            topic=request.form["topic"]
        ))
        db.session.commit()
        flash("✅ Topic saved! Quiz coming soon.", "success")
    return render_template("topics.html", topics=topics_list)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
