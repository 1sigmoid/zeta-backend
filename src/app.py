# module imports
import flask
import os
import shortuuid
from datetime import datetime
import requests

# file imports
import image_upload_logger as ilog
import jwt_handler as jw

# ml imports
from machine_learning.face_detection import detect as face_detect
from machine_learning.color_detection import detect as color_detect
from machine_learning.handwriting_recognition import recognize as writing_detect
from machine_learning.image_classification import vision as classifier

# initialization
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# global constants
HOST = "0.0.0.0"
PORT = 80

# routes
@app.route('/', methods=['GET'])
def home():
    return flask.jsonify({
        "status": 200,
        "message": "All Systems are GO!"
    })


"""
AUTHENTICATION BASED ROUTES
"""

@app.route('/login', methods=['GET'])
def render_login_page():
    return flask.render_template('login.html')

@app.route('/register', methods=['GET'])
def render_register_page():
    return flask.render_template('register.html')



@app.route('/api/upload/image', methods=['POST'])
def accept_incoming_image():
    try:
        token = flask.request.form['token']
    except:
        return flask.jsonify({
            "message": "Auth Required"
        }), 401
    response = jw.validate_token(token)
    if response[0]:
        if response[1]['decodedToken']['role'] == 'device':
            # set a storage directory for the image. built using the username.
            storage_directory = f"./static/images/{response[1]['decodedToken']['username']}/"
            if os.path.isdir(storage_directory):
                pass
            else:
                os.mkdir(storage_directory)
            # uploaded
            f = flask.request.files['image']
            file_uuid = shortuuid.uuid()
            filename = storage_directory + file_uuid + ".png"
            f.save(filename)
            ilog.log(response[1]['decodedToken']['username'], file_uuid + ".png",
                    f"40.76.37.214:80/static/images/{response[1]['decodedToken']['username']}/{file_uuid}.png", str(datetime.now()))
            return (flask.jsonify({
                "message": f"Accepted the Image from user {response[1]['decodedToken']['username']}"
            })), 200
    else:
        return flask.jsonify({
            "message": "Malformed JWT."
        }), 403


@app.route('/api/getImages', methods=['GET'])
def get_images():
    print("Recieved the request")
    try:
        with open('userlist.csv', 'r') as f:
            text = f.read()
            print("Read the file")
            return text, 200
    except:
        return 500, {"message": "Something went wrong with the text parser"}


"""
App Route to Show the ML Options Page.
"""


@app.route('/functions', methods=['GET'])
def view_ml():
    return flask.render_template('ml_page.html')


@app.route('/snapper', methods=['GET'])
def snapper_view():
    return flask.render_template('snapper.html', data = {"url":"#"})


@app.route('/api/snap_raspberry', methods=['POST'])
def snap_raspberry():
    """
    Should send an API request to the raspberry pi
    :return:
    """
    try:
        print(flask.request.form)
        ip = flask.request.form['raspip']
    except:
        return flask.jsonify({
            "message": "Auth Token or Raspberry Pi Ip not supplied"
        }), 400
    RASP_IP_ADDR = ip
    url = f"http://{RASP_IP_ADDR}:5000/api/snap"
    return flask.render_template('snapper.html', data={
        "url":url
    })




@app.route('/api/deleteImage', methods=['GET'])
def delete_image():
    """Deletes an image in a path supplied

    Returns:
        JSON: a json object with the response
    """
    # check if the token is supplied with the getRequest:
    token = None
    if 'token' in flask.request.args:
        token = flask.request.args['token']
    else:
        return {
            "message":"Token Not Supplied"
        }, 403

    # check if the image path is supplied with the request
    imgpath = None
    if 'path' in flask.request.args:
        imgpath = flask.request.args['path']
    else:
        return {
            "message":"Path not supplied"
        }, 400
    
    # if we reach here, the image path is supplied
    # now we try to delete the image
    
    if imgpath and token:
        # we have a image path and a token
        response = jw.validate_token(token)
        if response[0]:
            if response[1]['decodedToken']['role'] == 'device':
                # means that the response is valid and has a device username
                username = response[1]['decodedToken']['username']
                deletion_path = f'/static/images/{username}/{imgpath}'
                try:
                    os.remove(deletion_path)
                    return flask.jsonify({
                        "message": "Deleted Image"
                    }), 200
                except:
                    return flask.jsonify({
                        "message": "Could not delete"
                    }), 500
        else:
            return flask.jsonify({
                "message": "Malformed JWT."
            }), 403


"""
ML FUNCTIONS
"""   

@app.route('/api/ml/writing_recognition', methods=['GET'])
def ml_writing_recog():
    # retrieve the last image from the database
    with open('userlist.csv', 'r') as f:
        # readlines, select the last line and split
        ls = f.readlines()
        print(ls)
        ls = ls[-1].split(',')
        print(ls)
        filepath = f'./static/images/{ls[1]}/{ls[2]}'

        print(filepath)
        # sending the file path to the ml module
        output = writing_detect.analyse(filepath)
        return output, 200
 
                     
@app.route('/api/ml/face_recognition', methods=['GET'])
def ml_color_recog():
    # retrieve the last image from the database
    with open('userlist.csv', 'r') as f:
        # readlines, select the last line and split
        ls = f.readlines()
        print(ls)
        ls = ls[-1].split(',')
        print(ls)
        filepath = f'./static/images/{ls[1]}/{ls[2]}'
        filepath2 = f'./static/images/{ls[1]}/output/{ls[2]}'

        print(filepath)
        # sending the file path to the ml module
        output = face_detect.detect(filepath, filepath2)
        return {"output":output, "filepath":filepath2}, 200

                     
@app.route('/api/ml/color_recognition', methods=['GET'])
def ml_face_recog():
    # retrieve the last image from the database
    with open('userlist.csv', 'r') as f:
        # readlines, select the last line and split
        ls = f.readlines()
        print(ls)
        ls = ls[-1].split(',')
        print(ls)
        filepath = f'./static/images/{ls[1]}/{ls[2]}'

        print(filepath)
        # sending the file path to the ml module
        output = color_detect.detect(filepath)
        return output, 200 
                     
                     
@app.route('/api/ml/classifier', methods=['GET'])
def classification():
    # retrieve the last image from the database
    with open('userlist.csv', 'r') as f:
        # readlines, select the last line and split
        ls = f.readlines()
        print(ls)
        ls = ls[-1].split(',')
        print(ls)
        filepath = f'./static/images/{ls[1]}/{ls[2]}'

        print(filepath)
        # sending the file path to the ml module
        output = classifier.predict(filepath)
        return output, 200 




if __name__ == "__main__":
    # critical to have this conditional for gunicorn to work!
    app.run(host=HOST, port=PORT)
