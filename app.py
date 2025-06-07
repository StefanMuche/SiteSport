from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articole.db'
app.config['SECRET_KEY'] = 'secretul_meu_super_secret'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

### MODELE ###
class Articol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titlu = db.Column(db.String(200), nullable=False)
    continut = db.Column(db.Text, nullable=False)
    data = db.Column(db.String(100), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # nou!

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Dacă vrei să permiți și crearea de admin din form, adaugă un checkbox:
        is_admin = "is_admin" in request.form

        if User.query.filter_by(username=username).first():
            flash("Numele de utilizator există deja!")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash("Cont creat cu succes! Acum te poți loga.")
        return redirect(url_for("login"))
    return render_template("register.html", user=current_user)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

### RUTE ###
@app.route("/")
def index():
    articole = Articol.query.order_by(Articol.id.desc()).all()
    return render_template("index.html", articole=articole, user=current_user)

@app.route("/articol/<int:id>")
def articol(id):
    articol = Articol.query.get_or_404(id)
    return render_template("articol.html", articol=articol, user=current_user)

@app.route("/despre")
def despre():
    return render_template("despre.html", user=current_user)

@app.route("/contact")
def contact():
    return render_template("contact.html", user=current_user)

@app.route("/adauga", methods=["GET", "POST"])
@login_required
def adauga():
    if not current_user.is_admin:
        flash("Doar adminii pot posta articole!")
        return redirect(url_for('index'))
    if request.method == "POST":
        titlu = request.form['titlu']
        continut = request.form['continut']
        data = datetime.now().strftime("%d %B %Y")
        articol_nou = Articol(titlu=titlu, continut=continut, data=data)
        db.session.add(articol_nou)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("adauga.html", user=current_user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('adauga'))
        else:
            flash("Cont sau parolă incorectă!")
    return render_template("login.html", user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

### CREARE DB/USER ADMIN – rulează o singură dată și apoi comentează ###
# with app.app_context():
#     db.create_all()
#     if not User.query.filter_by(username="admin").first():
#         user = User(username="admin", password="parola123")  # Schimbă parola!
#         db.session.add(user)
#         db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
