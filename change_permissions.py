import os.path
from os import path
from os import listdir
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from autouploader_mocks_2021 import search, create_new_student_folder, create_mock_folder
import msvcrt as m
import re

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def main():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    parent_id = '1wR2buGuQdMBk-wrw6MbEdUC_dA8OLhSw'
    new_folders = list()
    man_upload = list()

    with open('new_folders.txt', 'r') as file:
        new_folders = file.readlines()

    batch = service.new_batch_http_request(callback=callback)
    
    for folder in new_folders:
        folder = folder.rstrip()
        query = ("name = '" + folder +  "' and "
                + "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + "' in parents and trashed = False")
        results = search(query, service)
        current_folder = results[0]
        if len(results) == 0:
            print('Could not find a folder for ' + folder + '. You need to manually do this.')
            man_upload.append(folder)
            continue      

        file_id = current_folder.get('id')
        skipped = False
        while True:
            print('Do you want to share ' + folder + ' now? <y to confirm, any other key to skip sharing>')
            if m.getch().decode('ASCII') != 'y':
                skipped = True
                break

            email = input("Please enter the email address with which the folder '" + folder + "' is to be shared.\n")
            if check(email):
                print("Are you sure you want to share the folder '" + folder + "' with " + email + "? <y to confirm, any other key to retry>")
                if m.getch().decode('ASCII') == 'y':
                    print()
                    break
            
            else:
                print('Invalid email. Please try again.')

        if skipped:
            continue

        user_permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': email
        }

        batch.add(service.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields='id',
        ))

        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': 'skhan8009@gmail.com'
        }

        batch.add(service.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields='id',
        ))

    batch.execute()

def callback(request_id, response, exception):
    if exception:
        # Handle error
        print(exception)
    else:
        print("Successfully shared. Permission ID: %s" % response.get('id'))

def check(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    # pass the regular expression
    # and the string in search() method
    if(re.search(regex, email)):
        return True
 
    else:
        return False