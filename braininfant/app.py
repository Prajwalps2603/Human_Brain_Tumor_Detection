from flask import Flask, render_template, request, flash, redirect
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# Keras
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template,session,flash,redirect, url_for, session,flash
from werkzeug.utils import secure_filename
#from gevent.pywsgi import WSGIServer
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
from bs4 import BeautifulSoup
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
import wikipedia

app = Flask(__name__)
app.secret_key = '1a2b3c4d5e'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'accounts'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' :
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            #session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return render_template('home.html')#redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    print("test result")
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' :
        print("test result resultrss")
        # Create variables for easy access
        username = request.form['un']
        password = request.form['pwd']
        email = request.form['em']
        ph = request.form['cn']
        br = request.form['br']
        clg = request.form['clg']
        adr = request.form['adr']
        cpwd = request.form['cpwd']
        
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM accounts WHERE username LIKE %s", [username] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        elif cpwd != password :
            flash("Password Should Match", "danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s,%s, %s, %s, %s)', (username,email, password,ph,br,clg,adr))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return render_template('login.html',title="Login")

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('register.html',title="Register")

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

# Load the saved model
model = load_model('brain.h5')

def get_common_name(scientific_name):
    try:
        # Search Wikipedia for the scientific name
        summary = wikipedia.summary(scientific_name, sentences=8)
        
        # Display the summary
        print(f"Summary: {summary}\n")
    except:
        summary="no data found / internet is down"

    return summary


# Preprocess the image for prediction
def preprocess_image(image_path, img_size=(64, 64)):
    img = load_img(image_path, target_size=img_size)  # Resize image to the same size used during training
    img_array = img_to_array(img) / 255.0  # Normalize pixel values
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension (for a single image)
    return img_array




@app.route("/predict", methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'static/uploads', secure_filename(f.filename))
        f.save(file_path)
        processed_image = preprocess_image(file_path)
        prediction = model.predict(processed_image)
        predicted_class_index = np.argmax(prediction, axis=1)
        label_set = ['glioma_tumor', 'meningioma_tumor', 'Healthy Brain','pituitary_tumor']  # Replace with your actual class labels
        predicted_label = label_set[predicted_class_index[0]]
        desc=get_common_name(predicted_label)
        img = load_img(file_path)
        plt.imshow(img)
        plt.title(f"Predicted: {predicted_label}")
        plt.axis('off')
        plt.show()
        return render_template('result.html', pred = predicted_label,desc=desc,fname=f.filename,)
    return render_template('home.html')


if __name__ == '__main__':
	app.run(debug = True)
