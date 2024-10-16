# Import libraries
from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import requests
import time
import threading

# Import functions
from streams.thermal import thermalStream
from streams.webcam import webcamStream

# Initialize the Flask server
app = Flask(__name__)

# Set up your OAuth credentials
client_id = 'FCuqxl0jBrb8z5M3keR0SuVQvmdzBPYn'
client_secret = 'JdxJMzcDAua5vhygIp5ZnesSO01JzYqVGBPiNq6BWTBgpjeqfF08SHT8KIU0IbHt'

# API endpoint for token generation
token_url = 'https://api2.arduino.cc/iot/v1/clients/token'

# Function to get access token
def get_access_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'audience': 'https://api2.arduino.cc/iot'
    }
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_info = response.json()
        access_token = token_info['access_token']
        print("Access Token:", access_token)
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        return None

# Get the access token
access_token = get_access_token()
if access_token is None:
    print("Exiting due to access token error.")
    exit()

# Arduino IoT Cloud details
BASE_URL = 'https://api2.arduino.cc/iot/v2'
THING_ID = '19350464-388a-4b31-9ec2-c6666dbfc5ef'
PROPERTY_ID = 'a4bd4a7a-6406-4afc-b5fd-2585400cbf36'

# Function to update the buzzer state
def update_buzzer(state):
    url = f'{BASE_URL}/things/{THING_ID}/properties/{PROPERTY_ID}/publish'
    data = {'value': state}
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Buzzer {'activated' if state else 'deactivated'}!")
    except requests.exceptions.RequestException as e:
        print(f"Error updating buzzer: {e}")

# Function to activate the buzzer in a separate thread
def activate_buzzer():
    update_buzzer(True)  # Activate the buzzer
    time.sleep(3)  # Keep the buzzer on for 3 seconds
    update_buzzer(False)  # Deactivate the buzzer

# Import the model
modelPath = "C:/Users/Daryl Guerzon/Desktop/github repo/models/etian35.pt"
model = YOLO(modelPath)
names = model.model.names

# Set the cameras
webcam = cv2.VideoCapture(0)
thermalCamera = cv2.VideoCapture(1)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Set the webcam feed and route using the webcamStream function
@app.route('/webcam_feed')
def webcam_feed():
    return Response(webcamStream(webcam, model, thermalCamera, 300),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Set the thermal camera feed and route
@app.route('/thermal_feed')
def thermal_feed():
    return Response(thermalStream(webcam, thermalCamera, model),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Initialize the app on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
