# import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import scrapeMars_ra

# create instance of Flask app
app = Flask(__name__)

# create route that scrapes the data
@app.route("/scrape")
def scrape():
    # IMPORTANT: Flask expects us to adhere to a particular folder structure.
    # It expects that all html pages will be held in the `templates` directory.
    # Because of this, we don't need to pass a relative path to the html page. It automatically
    # assumes that it's in the templates directory.
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)

    db = client.mars_db
    
    try:
        db.create_collection('mars')
    except pymongo.errors.CollectionInvalid:
        db.drop_collection('mars')
        db.create_collection('mars')

    collection = db.mars

    missionMars = scrapeMars_ra.scrape()

    # Insert document into collection
    collection.insert_one(missionMars)

    results = db.mars.find()
    for result in results:
        title = result['News']['Title']
        article = result['News']['Article']
        featured = result['Featured_image_url']
        hemispheres = result['Mars_hemispheres']

    return render_template("index.html", title=title, article=article, fiu=featured, hem=hemispheres)


# create route that renders index.html template
@app.route("/")
def index():
    # IMPORTANT: Flask expects us to adhere to a particular folder structure.
    # It expects that all html pages will be held in the `templates` directory.
    # Because of this, we don't need to pass a relative path to the html page. It automatically
    # assumes that it's in the templates directory.
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_db

    try:
        db.create_collection('mars')
    except pymongo.errors.CollectionInvalid:
        print('Mars collection already exists...')

    results = db.mars.find()

    if results.count() > 0:
        for result in results:
            title = result['News']['Title']
            article = result['News']['Article']
            featured = result['Featured_image_url']
            hemispheres = result['Mars_hemispheres']
    else:
        title="No data...click Scrape New Data"
        article="Thank you"
        featured="mission_to_mars.png"
        hemispheres=[]
    
    return render_template("index.html", title=title, article=article, fiu=featured, hem=hemispheres)
    

@app.route("/facts")
def facts():
    return render_template("factsMars.html")


if __name__ == "__main__":
    app.run(debug=True)


