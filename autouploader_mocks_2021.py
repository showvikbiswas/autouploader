from __future__ import print_function
import os.path
from os import listdir
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import msvcrt as m
import atexit

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
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

    files = listdir('Scripts')

    while True:
        parent_id = input('Please enter the root folder ID (http://drive.google.com/.../folders/<ID>) carefully\n')
        try:
            parent_folder = service.files().get(fileId=parent_id).execute()
            if parent_folder['mimeType'] != 'application/vnd.google-apps.folder':
                raise Exception
            print('Found parent folder: ' + parent_folder['name'])
            print('Do you want to select this as the parent folder? <y/n>')
            if m.getch().decode('ASCII') != 'y':
                continue
        except:
            print('CAREFULLY (HINT: CTRL+C CTRL+V)')
            continue

        print('Parent folder set to ' + parent_folder['name'])
        break

    for f in files:
        tokens = f.split(maxsplit=3)
        print('Trying to upload ' + f)
        # Debug tool
        # if m.getch().decode('ASCII') == 'N':
        #     break
        
        query = ("name contains '" + tokens[0] + "' and name contains '" + tokens[1] + "' and "
                + "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + "' in parents and trashed = False")
        folders = search(query, service)

        if len(folders) == 0:
            print('Could not find a match for ' + f)
            upload_root = create_new_student_folder(parent_id, f, service)
        
        elif len(folders) == 1:
            while True:
                print('Found folder with name: ' + service.files().get(fileId=folders[0].get('id')).execute()['name'] + '. Do you want to upload to this folder? <y/n>')
                pressedKey = m.getch().decode('ASCII')
                if pressedKey == 'y':
                    upload_root = folders[0]
                    break
                else:
                    upload_root = create_new_student_folder(parent_id, f, service)
                    break
        
        else:
            print('There are ' + str(len(folders)) + ' matches for the current name in the present root. Please choose ID of the folder' + 
                ' to upload to.')
            for i in range(len(folders)):
                possibility = service.files().get(fileId=folders[i].get('id')).execute()
                print(str(i+1) + ': ' + possibility['name'])
            while True:
                try: 
                    choice = int(input('Choice: '))
                    if choice >= 1 and choice <= len(folders):
                        upload_root = folders[choice-1]
                        break
                    else:
                        print('Choice is not within range. Please try again.')                                    
                except:
                    print('Not a number. Try again.')
            

        upload_root_id = upload_root.get('id')
        query = "name contains 'MOCKS' and '" + upload_root_id + "' in parents and trashed = False"
        mock_folder_list = search(query, service)
        try:
            upload_folder = create_mock_folder(mock_folder_list, service, upload_root_id)
        except Exception:
            error()
            continue

        upload_folder_id = upload_folder.get('id')

        # Search for preexisting files with given name and delete
        query = "name = '" + f + "' and '" + upload_folder_id +"' in parents and trashed = False"
        file_duplicates = search(query, service)
        if len(file_duplicates) > 0:
            print('Duplicates found for ' + f + '. Deleting duplicates...')
            for file in file_duplicates:
                service.files().delete(fileId=file.get('id')).execute()

        file_metadata = {
            'name': f,
            'parents': [upload_folder_id]
        }
        try:                
            media = MediaFileUpload('Scripts\\' + f,
                                    mimetype='application/pdf',
                                    resumable=True)
            print('Uploading...')
            uploadfile = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
            uploadfile = service.files().get(fileId=uploadfile.get('id')).execute() 
            upload_folder = service.files().get(fileId=upload_root_id).execute()
            print('Successfully uploaded ' + uploadfile['name'] + ' to ' + parent_folder['name'] + '/' + upload_folder['name'])
        except:
            print('An error occurred. File ' + f + ' could not be uploaded.')
        
        print()

def search(query, service):
    page_token = None
    response = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()
    return response.get('files', [])

def error():
    print('There seems to be a problem with your Google Drive authentication or the Internet connection. Check if your internet connection is okay, and press any key to continue...')
    m.getch()

def create_new_student_folder(parent_id, file_name, service):
    while True:
        folder_name = input('Please choose a folder name for ' + file_name + '\n')
        print('Are you sure you want to name the new folder ' + folder_name + '? <y/n>')
        if m.getch().decode('ASCII') == 'y':
            # Check for existing folders with given name
            query = ("name = '" + folder_name +  "' and "
                + "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + "' in parents and trashed = False")
            possible_duplicates = search(query, service)

            if len(possible_duplicates) == 0:
                break

            if len(possible_duplicates) == 1:
                print('There seems to be a folder with the specified name. Do you want to upload to the existing folder? <y/n>')
                if m.getch().decode('ASCII') == 'y':
                    upload_root = possible_duplicates[0]
                    return upload_root

            elif len(possible_duplicates) > 1:
                print('Oops. There seems to be multiple folders with the specified name. Too lazy to implement this. Upload manually for now. :p')
                return
    
    file_metadata = {
        'name': folder_name,
        'parents': [parent_id],
        'mimeType': 'application/vnd.google-apps.folder'
        }

    try:
        upload_root = service.files().create(body=file_metadata, fields='id').execute()
        return upload_root
    except Exception:
        error()

def create_mock_folder(mock_folder_list, service, upload_root_id):
    if len(mock_folder_list) == 0:
            file_metadata = {
                'name': 'MOCKS',
                'parents': [upload_root_id],
                'mimeType': 'application/vnd.google-apps.folder'
                }
            try:
                upload_folder = service.files().create(body=file_metadata, fields='id').execute()
                return upload_folder
            except:
                raise Exception
        
    elif len(mock_folder_list) == 1:
        upload_folder = mock_folder_list[0]
        return upload_folder
    
    else:
        print('Warning: There may be duplicate "MOCKS" folders. Please upload this file manually.')
        


if __name__ == '__main__':
    main()