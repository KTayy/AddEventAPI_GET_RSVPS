import requests
import pandas as pd
import threading
import time
from config import TOKEN
from datetime import date


def loading_animation():
    animation = "|/-\\"
    idx = 0
    while not Loader:
        print(animation[idx % len(animation)], end="\r")
        idx += 1
        time.sleep(0.1)
        
def get_event_list(token, page=None):
    
    base_url = r"https://www.addevent.com/api/v1/oe/events/list/"
    params = {
        "token": token,
        "page": page
    }
    #add animation
    global Loader 
    Loader = False #initialize animation loader
    # Create a separate thread for the loading animation
    animation_thread = threading.Thread(target=loading_animation)
    animation_thread.start()

    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            list_details = response.json()
            Loader = True  # Set the flag to indicate event details have been received
            return list_details
        else:
            print("Error occurred:", response.text)
    except requests.Timeout:
        print("API request timed out.")

def print_event_list(token):
    list_details = get_event_list(token)
    events = list_details["events"]
    event_details = [(event['id'], event['title']) for event in events]
    for event_id, event_name in event_details:
        print(f"Event ID: {event_id}, Event Name: {event_name}")
       
def get_rsvps_list(token, event_id, page=None):    
    
    base_url = r"https://www.addevent.com/api/v1/oe/rsvps/list/"
    params = {
        "token": token,
        "event_id": event_id,
        "page": page
    }
    
    #add animation
    global Loader
    Loader = False #initialize animation loader
    # Create a separate thread for the loading animation
    animation_thread = threading.Thread(target=loading_animation)
    animation_thread.start()

    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            event_details = response.json()
            Loader = True  # Set the flag to indicate event details have been received
            return event_details
        else:
            print("Error occurred:", response.text)
    except requests.Timeout:
        print("API request timed out.")

def retrieve_all_rsvps(token, event_id):
    print("compiling pages...")
    all_rsvps = []
    page = 1
    while True:
        event_details = get_rsvps_list(token, event_id, page=page)
        rsvps_data = event_details["rsvps"]["attendees"]
        all_rsvps.extend(rsvps_data)
        # Check if there is a next page
        next_url = event_details.get("paging", {}).get("next")
        if next_url:
            page += 1
        else:
            break
    return all_rsvps

def main():
    token = TOKEN
    
    print_event_list(token)
    
    # Get event_id from user input
    event_id = input("Enter your event_id: ")
    all_rsvps = retrieve_all_rsvps(token, event_id)
    df = pd.DataFrame(all_rsvps)


    # Mapping dictionary for renaming columns
    column_mapping = {
        'attending': 'Attending',
        'city': 'City',
        'country': 'Country',
        'createdate': 'Create date',
        'email': 'Email',
        'fld-icareo': 'How would you like to attend?',
        'fld-icexbc': 'Please indicate if you have any accessibility requirements',
        'fld-icexox': 'Disclaimer',
        'fld-iciocr': 'Please list any dietary restrictions',
        'fld-iisocb': 'Last Name',
        'fld-iisocc': 'Job Title',
        'fld-iisoce': 'Organization',
        'id': 'ID',
        'ip': 'IP',
        'location': 'Location',
        'modifydate': 'Last save date',
        'name': 'First Name',
        'postal': 'Postal',
        'region': 'Region',
        'userid': 'System Id'
    }

    # Rename the columns of the DataFrame
    df = df.rename(columns=column_mapping)

    # Create a new Excel file
    file_date = str(date.today())
    file_name = input("\n What do you want to name your file? ")
    extension = ".xlsx"
    file = file_date + "_" + file_name + extension
    df.to_excel(file)
    
    
    
    input("press Enter to exit....")
        
        
        
        
if __name__ == "__main__":
    main()
