import os
import io
import time
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_file
from flask_session import Session

from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, convert_image_to_binary

from datetime import datetime

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///keystroke.db")


UPLOAD_URL = "/images"
app.config['UPLOAD_URL'] = UPLOAD_URL


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":

        # get user input for seaching requirements
        search_query = request.form.get("Search")
        search_method = request.form.get("radioOption")

        # checks to see if user input is safe/exists
        if search_query and (search_method in ["username", "title", "language"]):
            posts = db.execute(
                f"Select * FROM posts WHERE {search_method} LIKE ? ORDER BY date_created DESC LIMIT 1 ", f"%{search_query}%")

            # posts["comments"] is a stored as a string which needs to be split for the front end
            for post in posts:
                post["comments"] = post["comments"].split("^")

            return render_template("index.html", posts=posts, search_query=search_query, search=search_method)

    # just give the first 10 posts that exist in the database
    posts = db.execute("Select * FROM posts ORDER BY date_created DESC LIMIT 10 ")

    # again alter post[comments] to fix the front end
    for post in posts:
        if post["comments"]:
            post["comments"] = post["comments"].split("^")
        else:
            post["comments"] = [""]

    return render_template("index.html", posts=posts)


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():

    if request.method == "POST":

        # get info on post details
        file = request.files['image']
        title = request.form.get("title")
        bodytext = request.form.get("post-text")
        language = request.form.get("language")

        # check if there is a file
        if file:
            filename = file.filename
            # Check file input is ok
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                return render_template("post.html", filename="Please enter an image file")

            # Get current username for adding post to database
            username = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["username"]

            # add post to database
            db.execute("INSERT INTO posts (title, bodytext, imageBinary, username, date_created, language) VALUES (?, ?, ?, ?, ?, ?)",
                       title, bodytext, convert_image_to_binary(file), username, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), language)

            # hack to get back the id of the thing we just inserted into the database
            image_id = db.execute("SELECT * FROM posts ORDER BY date_created DESC LIMIT 1")[0]["id"]

            # url to retrieve the image from specific upload_url route
            image_url = os.path.join(app.config['UPLOAD_URL'], f"{image_id}")

            return render_template("post.html", image_url=image_url)

    return render_template("post.html")


# url which allows a login user to add a comment to a post
@app.route("/post/<postid>/comment", methods=["POST"])
@login_required
def postcomment(postid):

    # get current users username
    current_username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

    # get comment text from html form
    comment_text = request.form.get("comment")

    # retrieve old comments from database
    old_comments = db.execute("SELECT comments FROM posts WHERE id = ?", postid)[0]["comments"]

    # append new comments
    new_comments = f"{old_comments}^{current_username}: {comment_text}"

    # update database
    db.execute("UPDATE posts SET comments = ? WHERE id = ?", new_comments, postid)

    # redirect to homepage
    return redirect("/")


# Image routing for UI
@app.route("/images/<fileid>")
def retrieve_file(fileid):
    # Store Image binary from database
    file_blob = db.execute("SELECT * FROM posts WHERE id=?", fileid)[0]["imageBinary"]

    # return reconstrcuted file
    return send_file(
        io.BytesIO(file_blob),
        as_attachment=True,
        download_name=f'file_{fileid}.txt',
        mimetype='application/octet-stream'
    )


@login_required
@app.route("/addfriends", methods=["GET", "POST"])
def addfriends():
    if request.method == "POST":

        # post can be from 2 different forms on this page
        # friend query is the search
        friend_query = request.form.get("search")

        # checks to see if it exists
        if friend_query:
            # limit users that appear to just people with the search name
            users = db.execute("SELECT * FROM users WHERE username LIKE ?", f"%{friend_query}%")
        else:
            # first 50 users
            users = db.execute("SELECT * FROM users LIMIT 50")

        # other choice is user is clicking the add friend remove friend button
        # user is adding friend
        addfriend_id = request.form.get("user_id")

        # user is removing a friend
        removefriend_id = request.form.get("removeuser_id")

        # if the user is adding a friend
        if addfriend_id:
            # add friend to database
            db.execute("INSERT INTO friends (userID, friendID) VALUES (?,?)", session["user_id"], addfriend_id)

        # if the user is removing a friend
        if removefriend_id:
            # remove friend
            db.execute("DELETE FROM friends WHERE userID = ? AND friendID = ?", session["user_id"], removefriend_id)

        # for displaying the correct value on the html a new attribute is attached.
        # this cant be stored in the database because it is session["user_id"] dependent
        # check if any users are already friends with current user
        for user in users:
            # check if they are already friends
            if db.execute("SELECT * FROM friends WHERE userID = ? AND friendID = ?", session["user_id"], user["id"]):
                user["AlreadyFriends"] = True
            else:
                user["AlreadyFriends"] = False

        return render_template("addfriends.html", users=users)

    # get users limit 50
    users = db.execute("Select * FROM users LIMIT 50")
    # same check as before
    for user in users:
        # check if they are already friends
        if db.execute("SELECT * FROM friends WHERE userID = ? AND friendID = ?", session["user_id"], user["id"]):
            user["AlreadyFriends"] = True
        else:
            user["AlreadyFriends"] = False

    return render_template("addfriends.html", users=users)


@app.route("/userpfp/<userid>")
def userpfp(userid):
    # Store Image binary from database
    file_blob = db.execute("SELECT * FROM users WHERE id=?", userid)[0]["profilephoto"]

    # return reconstrcuted file
    return send_file(
        io.BytesIO(file_blob),
        as_attachment=True,
        download_name=f'file_{userid}.txt',
        mimetype='application/octet-stream'
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":
        # profile photo
        file = request.files['image']

        if file:
            filename = file.filename
            # Check file input is ok
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):

                # add profilephoto to database
                db.execute("UPDATE users SET profilephoto = ? WHERE id = ?", convert_image_to_binary(file), session["user_id"])

    # get current user
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    # get current users posts
    posts = db.execute("SELECT * FROM posts WHERE username = ?", user["username"])

    # add the comment fix
    for post in posts:
        post["comments"] = post["comments"].split("^")

    return render_template("profile.html", user=user, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        if not username or not password:
            return apology("Username is blank")

        if db.execute("SELECT username FROM users WHERE username = ?", username):
            return apology("Username already in database")

        if not password == confirm_password:
            return apology("Passwords Do Not Match")

        # add hashed password and username into database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        return render_template("login.html")

    return render_template("register.html")

