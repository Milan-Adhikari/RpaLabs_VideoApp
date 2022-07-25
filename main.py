"""
@author: Milan Adhikari
date: 2022/07/25
"""

from flask import Flask, render_template, request, redirect, url_for
from wtforms.validators import InputRequired
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from pymediainfo import MediaInfo
from flask_wtf import FlaskForm
import json
import os

# initialising flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'RpaLabsTask'  # secret key is necessary to use the csrf token that comes with the form
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# restricting the extensions allowed to upload
ALLOWED_EXTENSIONS = {'mp4', 'mkv'}


# function that validates the extension of the video
def validating_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# function to validate the size and duration of the video
def validating_size_and_duration(file):
    MAXIMUM_DURATION = 600   # 10 minutes is the maximum duration
    MAXIMUM_SIZE = 1073741824  # 1GB IS THE MAXIMUM SIZE
    json_object = MediaInfo.parse(file, output='JSON')  # MediaInfo parses the video and provides the data about video
    info = json.loads(json_object)["media"]["track"][0]  # converting into readable format
    duration = info['Duration']  # extracting the video duration
    size = info['FileSize']  # extracting the video size
    if float(duration) <= MAXIMUM_DURATION and int(size) <= MAXIMUM_SIZE:
        return True
    else:
        return False


# creating a class for the form that will inherit from the FlaskForm
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])  # for getting the nav function to navigate the files
    submit = SubmitField("Upload")  # for submitting the file to upload


@app.route('/')
def index():
    return render_template('index.html')  # main page


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadFileForm()  # getting the form
    if form.validate_on_submit():
        file = form.file.data  # grabbing the file from the form
        if validating_file_extension(file.filename):  # this is invoked after pressing submit button
            if validating_size_and_duration(file):
                file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                       secure_filename(file.filename)))  # saving the video
                return render_template('index.html', message='File has been uploaded')
            else:
                return render_template('upload.html', message="Video cannot exceed 10 minutes in length and 1 Gb in size", form=form)
        else:
            return render_template('upload.html', form=form, message="Videos with Mp4 or MKV extensions are only accepted")
    return render_template('upload.html', form=form)


@app.route('/browse')
def browse():
    # getting the list of files in the folder
    list_of_files = os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER']))
    return render_template('browse.html', list=list_of_files)


@app.route('/charges', methods=['POST', 'GET'])
def charges():
    if request.method == 'GET':
        return render_template('charges.html')
    if request.method == 'POST':
        form_data = request.form  # getting the data from the form
        price = 0
        # the magic numbers below are the conditions to pay the money
        if int(form_data['Size']) < 500:
            price = 5
        elif int(form_data['Size']) > 1024:
            price = 'not allocated since the video size exceeds the Maximum Limit'
        else:
            price += 12.5
        if int(form_data['Length']) < 6.18:
            price += 12.5
        elif int(form_data['Length']) > 10:
            price = 'not allocated since the video length exceeds the Maximum Limit'
        else:
            price += 20
        return render_template('index.html', message='Price is {}'.format(price))


# to run the main application
if __name__ == '__main__':
    app.run(debug=True)
