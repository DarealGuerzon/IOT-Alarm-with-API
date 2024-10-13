import requests
import time
import threading

# Set up your OAuth credentials
client_id = 'FCuqxl0jBrb8z5M3keR0SuVQvmdzBPYn'  # Replace with your Client ID
client_secret = 'JdxJMzcDAua5vhygIp5ZnesSO01JzYqVGBPiNq6BWTBgpjeqfF08SHT8KIU0IbHt'  # Replace with your Client Secret

# API endpoint for token generation
token_url = 'https://api2.arduino.cc/iot/v1/clients/token'
BASE_URL = 'https://api2.arduino.cc/iot/v2'
THING_ID = '19350464-388a-4b31-9ec2-c6666dbfc5ef'  # Your Thing ID
PROPERTY_ID = 'a4bd4a7a-6406-4afc-b5fd-2585400cbf36'  # Your Buzzer Property ID


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
        return None


# Function to update the buzzer state
def update_buzzer(state):
    access_token = get_access_token()
    if access_token is None:
        print("No access token. Cannot update buzzer.")
        return

    url = f'{BASE_URL}/things/{THING_ID}/properties/{PROPERTY_ID}/publish'
    data = {'value': state}
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
    threading.Thread(target=_activate_buzzer).start()


def _activate_buzzer():
    update_buzzer(True)  # Activate the buzzer
    time.sleep(3)  # Keep the buzzer on for 3 seconds
    update_buzzer(False)  # Deactivate the buzzer
