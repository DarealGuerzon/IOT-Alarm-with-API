import requests
import time
import cv2
import numpy as np
from ultralytics import YOLO

# Your access token (the one you provided)
access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL2FwaTIuYXJkdWluby5jYy9pb3QiLCJhenAiOiJGQ3VxeGwwakJyYjh6NU0za2VSMFN1VlF2bWR6QlBZbiIsImV4cCI6MTcyNzQ1MzUwOSwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwiaHR0cDovL2FyZHVpbm8uY2MvY2xpZW50X2lkIjoiTm9ubmFoIiwiaHR0cDovL2FyZHVpbm8uY2MvaWQiOiJjNWE3MDBiZS1hZWQ3LTQzNWQtYjM2OC0xMTVjYTFhNGYwYjAiLCJodHRwOi8vYXJkdWluby5jYy9yYXRlbGltaXQiOjEwLCJodHRwOi8vYXJkdWluby5jYy91c2VybmFtZSI6Im5hcnV0b2QxIiwiaWF0IjoxNzI3NDUzMjA5LCJzdWIiOiJGQ3VxeGwwakJyYjh6NU0za2VSMFN1VlF2bWR6QlBZbkBjbGllbnRzIn0.O3qIo1mcZQ8IXkmfXMIW2Fjs9Ov2Y06LY12jIXGIvxI'
BASE_URL = 'https://api2.arduino.cc/iot/v2'
THING_ID = '53958204-2e49-4798-a5c9-8b23db733b78'  # Your Thing ID
PROPERTY_ID = '675aa667-7df2-4d69-adca-aff80435cedc'  # Your Buzzer Property ID

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
        if state:
            time.sleep(3)  # Wait for 3 seconds
            update_buzzer(False)  # Stop the buzzer after 3 seconds
    else:
        print(f"Failed to update buzzer. Status code: {response.status_code}")
        print("Response:", response.text)

# Load the YOLO model
modelPath = "C:/Users/Daryl Guerzon/Desktop/models/train6/last.pt"
model = YOLO(modelPath)
names = model.model.names

# Set distance to be considered isolation
distanceThreshold = 300

# Calculate the distance between centers of each bounding box
def euclideanDistance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

def main():
    # Video stream
    webcam = 0
    cap = cv2.VideoCapture(webcam)

    # Print this if IP camera is not found or if can't open camera
    if not cap.isOpened():
        print("ERROR: Could not open video stream")
        exit()

    # If camera is open
    while cap.isOpened():
        success, im0 = cap.read()  # im0 is the frame variable
        if not success:
            print("Video frame is empty or video processing is completed")
            break

        results = model(im0)  # Run the model on the frame
        centers = []  # Store the center of each bounding box to an array
        boundingBoxes = []  # Store the bounding boxes of each detection to an array

        for result in results:
            boxes = result.boxes  # Bounding boxes

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]  # Bounding box coordinates
                cls = int(box.cls[0])  # Class value
                conf = box.conf[0]  # Confidence value

                # Calculate centers of the bounding boxes
                centerX = int((x1 + x2) / 2)
                centerY = int((y1 + y2) / 2)

                centers.append((centerX, centerY))  # Populate the array with the calculated centers
                boundingBoxes.append((x1, y1, x2, y2))  # Populate the array with the detected bounding boxes

                cv2.rectangle(im0, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)  # Draw the bounding boxes
                cv2.circle(im0, (centerX, centerY), 5, (0, 255, 0), -1)  # Put circles in the centers of each bounding box
                cv2.putText(im0, f"{names[cls]} {conf:.2f}", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # Print the detected class name and confidence percentage

            isolatedFlags = [True] * len(centers)  # Initialize the isolation

            for i in range(len(centers)):
                for j in range(len(centers)):
                    if i != j:  # Don't compare a chicken to itself
                        dist = euclideanDistance(centers[i], centers[j])  # Calculate the distances between centers

                        # Marks objects less than the threshold as not isolated
                        if dist < distanceThreshold:
                            isolatedFlags[i] = False
                            isolatedFlags[j] = False
                            cv2.line(im0, centers[i], centers[j], (0, 0, 255), 2)  # Draws the line between objects that are close to each other

                        # Prints the distances between centers
                        midPoint = ((centers[i][0] + centers[j][0]) // 2, (centers[i][1] + centers[j][1]) // 2)
                        cv2.putText(im0, f"{dist:.2f} px", midPoint, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Checks for isolation
            for idx, (center, bbox, isolated) in enumerate(zip(centers, boundingBoxes, isolatedFlags)):
                if isolated:
                    cv2.putText(im0, "Isolated", (int(bbox[0]), int(bbox[1]) - 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)  # Prints isolation mark on top of the bounding boxes
                    cv2.rectangle(im0, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 2)  # Draws red bounding boxes on isolated objects

                    # Activate the buzzer when an object is isolated
                    update_buzzer(True)  # Activate buzzer for 3 seconds

        # Show the video feed with detections
        cv2.imshow("Video Feed", im0)  # Display the frame

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()  # Close all OpenCV windows

# Run the main function
if __name__ == "__main__":
    main()
