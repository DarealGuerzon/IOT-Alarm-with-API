import requests

# Your OAuth credentials
client_id = 'FCuqxl0jBrb8z5M3keR0SuVQvmdzBPYn'  # Replace with your Client ID
client_secret = 'JdxJMzcDAua5vhygIp5ZnesSO01JzYqVGBPiNq6BWTBgpjeqfF08SHT8KIU0IbHt'  # Replace with your Client Secret

# API endpoint for token generation
token_url = 'https://api2.arduino.cc/iot/v1/clients/token'

# Payload to get the access token
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'audience': 'https://api2.arduino.cc/iot'
}

# Make the POST request to get the access token
response = requests.post(token_url, data=data)

# Extract the access token from the response
if response.status_code == 200:
    token_info = response.json()
    access_token = token_info['access_token']
    print("Access Token:", access_token)
else:
    print(f"Failed to get access token. Status code: {response.status_code}")
    print(response.text)
