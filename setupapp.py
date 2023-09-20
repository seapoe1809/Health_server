#!/usr/bin/env python3
#/* DARNA.HI
# * Copyright (c) 2023 Seapoe1809   <https://github.com/seapoe1809>
# * Copyright (c) 2023 pnmeka   <https://github.com/pnmeka>
# * 
# *
# *   This program is free software: you can redistribute it and/or modify
# *   it under the terms of the GNU General Public License as published by
# *   the Free Software Foundation, either version 3 of the License, or
# *   (at your option) any later version.
# *
# *   This program is distributed in the hope that it will be useful,
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *   GNU General Public License for more details.
# *
# *   You should have received a copy of the GNU General Public License
# *   along with this program. If not, see <http://www.gnu.org/licenses/>.
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

app = Flask(__name__)

# Initialize Flask extensions
bcrypt = Bcrypt(app)

# Encrypt a secret key
key = Fernet.generate_key()
cipher_suite = Fernet(key)
app.secret_key = cipher_suite.encrypt(app.root_path.encode())

# Configure the SQLAlchemy part to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

# Create tables and initialize users
with app.app_context():
    db.create_all()

    admin_exists = User.query.filter_by(username='ADMIN').first()
    user1_exists = User.query.filter_by(username='USER1').first()

    if not admin_exists:
        admin = User(username='ADMIN', password=bcrypt.generate_password_hash('health').decode('utf-8'))
        db.session.add(admin)

    if not user1_exists:
        user1 = User(username='USER1', password=bcrypt.generate_password_hash('wellness').decode('utf-8'))
        db.session.add(user1)

    if not admin_exists or not user1_exists:
        db.session.commit()

    print("Database and users initialized.")

