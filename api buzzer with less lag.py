import requests
import time
import cv2
import numpy as np
from ultralytics import YOLO
import threading  # Import threading module

# Your OAuth credentials
client_id = 'FCuqxl0jBrb8z5M3keR0SuVQvmdzBPYn'  # Replace with your Client ID
client_secret = 'JdxJMzcDAua5vhygIp5ZnesSO01JzYqVGBPiNq6BWTBgpjeqfF08SHT8KIU0IbHt'  # Replace with your Client Secret

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
    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        print("Access Token:", access_token)
        return access_token
    else:
        print(f"Failed to get access token. Status code: {response.status_code}")
        print(response.text)
        return None  # Return None if token generation fails

# Get the access token
access_token = get_access_token()

if access_token is None:
    exit()  # Exit the program if the token could not be obtained

BASE_URL = 'https://api2.arduino.cc/iot/v2'
THING_ID = '19350464-388a-4b31-9ec2-c6666dbfc5ef'  # Your Thing ID
PROPERTY_ID = 'a4bd4a7a-6406-4afc-b5fd-2585400cbf36'  # Your Buzzer Property ID

# Function to update the buzzer state
def update_buzzer(state):
    url = f'{BASE_URL}/things/{THING_ID}/properties/{PROPERTY_ID}/publish'
    data = {
        'value': state
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Buzzer {'activated' if state else 'deactivated'}!")
    else:
        print(f"Failed to update buzzer. Status code: {response.status_code}")
        print("Response:", response.text)

# Function to activate the buzzer in a separate thread
def activate_buzzer():
    update_buzzer(True)  # Activate the buzzer
    time.sleep(3)  # Keep the buzzer on for 3 seconds
    update_buzzer(False)  # Deactivate the buzzer

# Load the YOLO model
modelPath = "C:/Users/Daryl Guerzon/Desktop/models/train6/last.pt"
model = YOLO(modelPath)
names = model.model.names

# Initialize the video capture from webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open video stream")
    exit()

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing is completed")
        break

    results = model(im0)  # Run the model on the frame
    chickens_detected = False  # Flag to check if chickens are detected

    for result in results:
        boxes = result.boxes  # Bounding boxes

        for box in boxes:
            cls = int(box.cls[0])  # Class value
            conf = box.conf[0]  # Confidence value

            if names[cls] == "chicken":  # Check if detected object is a chicken
                chickens_detected = True  # Set flag to true if chicken is detected
                cv2.putText(im0, f"{names[cls]} {conf:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # Print detected class name

                # Draw the bounding box around the chicken
                x1, y1, x2, y2 = box.xyxy[0]  # Get box coordinates
                cv2.rectangle(im0, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

    # Activate the buzzer in a separate thread if a chicken is detected
    if chickens_detected:
        buzzer_thread = threading.Thread(target=activate_buzzer)
        buzzer_thread.start()  # Start the buzzer thread

    # Display the video feed with detections
    cv2.imshow("Video Feed", im0)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
