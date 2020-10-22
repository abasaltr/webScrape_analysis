# import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

# create instance of Flask app
app = Flask(__name__)

# create route that renders index.html template
@app.route("/")
def index():
    # IMPORTANT: Flask expects us to adhere to a particular folder structure.
    # It expects that all html pages will be held in the `templates` directory.
    # Because of this, we don't need to pass a relative path to the html page. It automatically
    # assumes that it's in the templates directory.

    name = "Reza Abasaltian"

    return render_template("index.html", data=f'Hello {name}!!')

if __name__ == "__main__":
    app.run(debug=True)
