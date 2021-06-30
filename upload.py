from __future__ import print_function
import os
import re
import msvcrt as m
from os import path
from os import listdir
from google.oauth2.challenges import PasswordChallenge
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import sendmail

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
root = str()

def main():
    # os.remove('token.json')
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists('token.json'):
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

    files = listdir('Scripts')

    service = build('drive', 'v3', credentials=creds)
    page_token = None
    while True:
        root_folder_name = input('Please type the name of the root folder carefully (case insensitive): ')
        query = "name = '" + root_folder_name + "' and mimeType='application/vnd.google-apps.folder' and trashed=False"
        root_folder = search(query, service)
        if root_folder:
            print('Are you sure you want to set the root folder as ' + root_folder[0]['name'] + '? <y/n>')
            if m.getch().decode('ASCII') == 'y':
                root = "'" + root_folder[0]['id'] + "'"
                break
        else:
            print('Invalid name')
            

    # Set up emails
    email_list = dict()
    with open('mail.txt') as file:
        data = file.readlines()
        for line in data:
            line = line.rstrip()
            name = line.split(sep=',')[1]
            email = line.split(sep=',')[4]
            email_list[name] = email
            
    batch = service.new_batch_http_request(callback=callback)
    # Call the Drive v3 API
    for f in files:
        full_name = f.split(sep='-')[1].strip().split(sep='.')[0]
        print(full_name)
        query = "name = '" + full_name + "' and mimeType='application/vnd.google-apps.folder'" + " and " + root + " in parents and trashed=False"
        folders = search(query, service)
        
        if len(folders) == 1:
            print("Found perfect match for " + f + ": " + folders[0]['name'])

            # Search for possible file duplicates within folder and delete
            query = "name = '" + f + "' and mimeType='application/pdf' and '" + folders[0]['id'] + "' in parents and trashed=False"
            duplicates = search(query, service)
            if len(duplicates) > 0:
                print('Duplicates found in folder with same file name. Proceeding to delete...')
                for duplicate in duplicates:
                    service.files().delete(fileId=duplicate['id']).execute()

            upload(f, folders[0]['id'], service)
        
        elif len(folders) == 0:
            print('No match for ' + f + '. Attempting to create new folder and upload.')
            print('Do you want the folder name to be ' + full_name + '? <y/n>')
            if m.getch().decode('ASCII') != 'y':
                # Check whether this folder already exists
                while True:
                    print('Please enter the destination folder name for ' + f)
                    new_folder_name = input()
                    query = "name = '" + new_folder_name + "' and mimeType='application/vnd.google-apps.folder'" + " and root in parents and trashed=False"
                    possible_duplicate_folders = search(query, service)
                    if len(possible_duplicate_folders) > 0:
                        print('A folder with this name already exists.')
                        continue
                    else:
                        break
            else:
                new_folder = create_new_folder(full_name, service)
                new_folder_id = new_folder['id']
                new_folder_link = new_folder['link']
                print(new_folder_link)
                upload(f, new_folder_id, service)
                try:
                    if check(email_list[full_name]) == False:
                        raise KeyError
                    share(new_folder_id, new_folder_link, full_name, email_list[full_name], batch, service)
                except KeyError:
                    print('Could not find a valid email address for ' + full_name + '. Do you still want to share this folder? <y/n>')
                    if m.getch().decode('ASCII') != 'y':
                        continue
                    while True:
                        print('Enter email address for ' + full_name)
                        man_email = input()
                        if check(man_email):
                            share(new_folder_id, new_folder_link, full_name, man_email, batch, service)
                            break
                        print('Invalid email.')

    batch.execute()

    # Send mails to designated folders

def share(folder_id, folder_link, full_name, email, batch, service):
    user_permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email,	
    }
    batch.add(service.permissions().create(
            fileId=folder_id,
            body=user_permission,
            fields='id',
            sendNotificationEmail=False
    ))
    service.files().update(fileId=folder_id, body={'folderColorRgb': '#00FF00'}).execute()

    print('Do you want to email the Drive folder link to ' + email + '? <y/n>')
    if m.getch().decode('ASCII') == 'y':
        body = 'Edbase Physics Drive Folder Link: \n\n' + folder_link + '\n\nPlease do not lose access to this link.'
        message = sendmail.create_message('workspace.edbase01@gmail.com', email, 'Physics_' + full_name + '_Edbase', body)
        try:
            sendmail.main(message)
        except Exception:
            print('An error occurred while trying to send an email to ' + email + '.')

def create_new_folder(full_name, service):
    file_metadata = {
    'name': full_name,
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [root],
    }

    print('Creating new folder named ' + full_name)

    folder = service.files().create(body=file_metadata,
                                    fields='webViewLink, id').execute()

    return {'id': folder.get('id'), 'link': folder.get('webViewLink')}

def upload(filename, folderid, service):
    file_metadata = {
    'name': filename,
    'parents': [folderid]
    }

    try:                
        media = MediaFileUpload('Scripts\\' + filename,
                                mimetype='application/pdf',
                                resumable=True)
        print('Uploading...')
        uploadfile = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
        # uploadfile = service.files().get(fileId=uploadfile.get('id')).execute() 
        upload_folder = service.files().get(fileId=folderid).execute()
        print('Successfully uploaded ' + filename + ' to ' + upload_folder['name'])
    except:
        print('An error occurred. File ' + filename + ' could not be uploaded.')            


def search(query, service):
    page_token = None
    results = service.files().list(q=query,
                                         spaces='drive',
                                         fields='nextPageToken, files(id, name)',
                                         pageToken=page_token).execute()
    items = results.get('files', [])
    return items

def callback(request_id, response, exception):
    if exception:
        # Handle error
        print(exception)
    else:
        print("Permission Id: %s" % response.get('id'))

def check(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    # pass the regular expression
    # and the string in search() method
    if(re.search(regex, email)):
        return True
 
    else:
        return False

if __name__ == '__main__':
    main()
