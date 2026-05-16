from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Admin
import time
import click

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():

    if request.path.startswith("/api/"):

        return jsonify({
            "error": "Login required"
        }), 401

    return redirect(url_for("login"))

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    admin = Admin.query.filter_by(
        username=username
    ).first()

    if not admin:
        time.sleep(1)

        return jsonify({
            "error": "Invalid username"
        }), 401

    if not admin.check_password(password):

        time.sleep(1)

        return jsonify({
            "error": "Invalid password"
        }), 401

    login_user(admin)

    return jsonify({
        "success": True
    })

@app.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect("/")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()

    return jsonify([
        user.to_dict()
        for user in users
    ])

@app.route("/api/users/<username>", methods=["GET"])
def get_user(username):
    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify(user.to_dict())

@app.route("/api/admin/create-user", methods=["POST"])
@login_required
def create_user():
    data = request.json

    username = data.get("username")

    if not username:
        return jsonify({
            "error": "Username required"
        }), 400

    existing = User.query.filter_by(
        username=username
    ).first()

    if existing:
        return jsonify({
            "error": "User already exists"
        }), 400

    user = User(
        username=username,
        macho_bucks=0
    )

    db.session.add(user)
    db.session.commit()

    socketio.emit("user_created", user.to_dict())

    return jsonify({"success": True, "user": user.to_dict()})

@app.route("/api/admin/add-bucks", methods=["POST"])
@login_required
def add_bucks():
    data = request.json

    username = data.get("username")
    amount = data.get("amount")

    if username is None or amount is None:
        return jsonify({
            "error": "Missing data"
        }), 400

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.macho_bucks += int(amount)

    db.session.commit()

    payload = {
        "username": user.username,
        "macho_bucks": user.macho_bucks
    }

    socketio.emit("balance_update", payload
    )

    return jsonify({
        "success": True,
        "user": user.to_dict()
    })

@app.route("/api/admin/remove-bucks", methods=["POST"])
@login_required
def remove_bucks():
    data = request.json

    username = data.get("username")
    amount = data.get("amount")

    if username is None or amount is None:
        return jsonify({
            "error": "Missing data"
        }), 400

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.macho_bucks -= int(amount)

    db.session.commit()

    payload = {
        "username": user.username,
        "macho_bucks": user.macho_bucks
    }

    socketio.emit("balance_update", payload
    )

    return jsonify({
        "success": True,
        "user": user.to_dict()
    })

@app.route("/api/admin/set-bucks", methods=["POST"])
@login_required
def set_bucks():
    data = request.json

    username = data.get("username")
    amount = data.get("amount")

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    user.macho_bucks = int(amount)

    db.session.commit()

    payload = {
        "username": user.username,
        "macho_bucks": user.macho_bucks
    }

    socketio.emit(
        "balance_update",
        payload
    )

    return jsonify({
        "success": True,
        "user": user.to_dict()
    })

@app.route("/api/admin/delete-user", methods=["POST"])
@login_required
def delete_user():

    data = request.json

    username = data.get("username")

    if not username:
        return jsonify({
            "error": "Username required"
        }), 400

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    db.session.delete(user)
    db.session.commit()

    socketio.emit(
        "user_deleted",
        {
            "username": username
        }
    )

    return jsonify({
        "success": True,
        "deleted_user": username
    })

@socketio.on("connect")
def handle_connect():
    print("Client connected")

    emit("connected", {
        "message": "Connected to Macho Bank"
    })

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@app.cli.command("create-admin")
@click.argument("username")
@click.password_option()
def create_admin(username, password):

    existing = Admin.query.filter_by(
        username=username
    ).first()

    if existing:
        print("Admin already exists")
        return

    admin = Admin(
        username=username
    )

    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    print(f"Created admin: {username}")

@app.cli.command("delete-admin")
@click.argument("username")
def delete_admin(username):

    admin = Admin.query.filter_by(
        username=username
    ).first()

    if not admin:
        print("Admin not found")
        return

    db.session.delete(admin)
    db.session.commit()

    print(f"Deleted admin: {username}")

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )