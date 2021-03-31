from __future__ import print_function
import os.path
from os import path
from os import listdir
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import msvcrt as m
from pythonping import ping
import change_permissions
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

IDs = (('OL MAY 21', '1Gbc8HwWG5soUBkAa33kM_PAOlwbT9L_L'), ('AS MAY 21', '1ISm564KqrH3l0YF-ToDHn0jND4ddni37'))

man_upload = list()
new_folders = list()
parent_id = str()


def main():

    if os.path.exists('token.json'):
        os.remove('token.json')

    if os.path.exists('new_folders.txt'):
        os.remove('new_folders.txt')

    try:
        files = listdir('Scripts')
    except FileNotFoundError:
        print('The Scripts folder was not found in this directory. Exiting...')
        return

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
    
    for i in range(len(IDs)):
        print(str(i+1) + ': ' + IDs[i][0])

    while True:
        try:
            choice = int(input('\nChoose ID of the parent folder (1, 2, 3, etc): '))
            if choice < 1 or choice > len(IDs):
                print('Choice outside range')
                continue
            
            parent_id = IDs[choice - 1][1]
            parent_folder = service.files().get(fileId=parent_id).execute()
            print('Are you sure you want to set the parent folder to ' + IDs[choice - 1][0] + '? <y to confirm, any other key to retry>')
            
            if m.getch().decode('ASCII') != 'y':
                continue
            print('Parent folder set to ' + parent_folder['name'] + '\n')
            break
        except ValueError:
            print('Not a number')
            continue
        except HttpError:
            print('Access to this folder is denied. Please close this program and restart using start.bat if you have logged in to the wrong account.')
            continue

    

    queue = list()

    for f in files:
        print('Trying to upload ' + f)
        # Debug tool
        # if m.getch().decode('ASCII') == 'N':
        #     break

        # Make an initial full match query
        full_name = f.split(sep='-')[0].rstrip()
        query = ("name = '" + full_name + "' and " + "mimeType = 'application/vnd.google-apps.folder' and '" + 
                parent_id + "' in parents and trashed = False")
        folders = search(query, service)
        
        if len(folders) == 1:
            print('Found perfect match with file name. Uploading to ' + service.files().get(fileId=folders[0].get('id')).execute()['name'] + '...')
            upload_root = folders[0]
        
        else:
            tokens = full_name.split()
            if len(tokens) > 1:
                query = ("name contains '" + tokens[0] + "' and name contains '" + tokens[1] + "' and "
                    + "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + "' in parents and trashed = False")
            elif len(tokens) == 1:
                query = ("name contains '" + tokens[0] + "' and "+ "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + 
                        "' in parents and trashed = False")
            else:
                query = ("name = '" + f + "' and " + "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + 
                "' in parents and trashed = False")
                
            folders = search(query, service)

            if len(folders) == 0:
                print('Could not find a match for ' + f + '. Adding to queue and moving on...\n')
                queue.append(f)
                continue
            
            elif len(folders) == 1:
                print('Found one partial match for ' + f + '. Adding to queue and moving on...\n')
                queue.append(f)
                continue
        
            else:
                print('Found multiple matches for ' + f + '. Adding to queue and moving on...\n')
                queue.append(f)
                continue

        upload(upload_root, f, parent_folder, query, service)
        print()
    
    if len(queue) > 0:
        print('In queue...')

    for item in queue:
        full_name = item.split(sep='-')[0].rstrip()
        tokens = full_name.split()
        
        if len(tokens) > 1:
            query = ("name contains '" + tokens[0] + "' and name contains '" + tokens[1] + "' and "
                + "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + "' in parents and trashed = False")
        else:
            query = ("name contains '" + tokens[0] + "' and "+ "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + 
                    "' in parents and trashed = False")
        
        folders = search(query, service)

        if len(folders) == 0:
            print('There are no matches for ' + item)
            print('Do you still want to upload the file? <y to confirm, any other key to cancel>')
            if m.getch().decode('ASCII') != 'y':
                print('Upload of ' + item + ' was cancelled by user.\n')
                man_upload.append(item)
                continue
            
            upload_root = create_new_student_folder(parent_id, item, service)
        
        elif len(folders) == 1:
            print('There is one partial match for ' + item + ' with name ' +
                service.files().get(fileId=folders[0].get('id')).execute()['name'])
            
            print('Do you still want to upload the file? <y to confirm, any other key to cancel>')
            if m.getch().decode('ASCII') != 'y':
                print('Upload of ' + item + ' was cancelled by user.')
                man_upload.append(item)
                continue
            
            print('Do you want to upload to ' + service.files().get(fileId=folders[0].get('id')).execute()['name'] + '? <y to confirm, n to cancel, any other key to upload to a new folder>')
            pressedKey = m.getch().decode('ASCII')
            
            if pressedKey == 'y':
                upload_root = folders[0]
            elif pressedKey == 'n':
                print('Upload of ' + item + ' was cancelled by user.')
                man_upload.append(item)
                continue
            else:
                upload_root = create_new_student_folder(parent_id, f, service)
        
        else:
            print('There are ' + str(len(folders)) + ' matches for ' + item + ' in the present root.')
            
            for i in range(len(folders)):
                possibility = service.files().get(fileId=folders[i].get('id')).execute()
                print(str(i+1) + ': ' + possibility['name'])
            
            print('Do you still want to upload the file? <y to confirm, any other key to cancel>')
            if m.getch().decode('ASCII') != 'y':
                print('Upload of ' + item + ' was cancelled by user.')
                man_upload.append(item)
                continue
            
            print('Please choose ID of the folder (1, 2, 3...) to upload to. Please type -1 and press Enter if you wish to create a new folder.')
            
            while True:
                try: 
                    choice = int(input('Choice: '))
                    if choice == -1:
                        upload_root = create_new_student_folder(parent_id, f, service)
                        break
                    if choice >= 1 and choice <= len(folders):
                        upload_root = folders[choice-1]
                        break
                    else:
                        print('Choice is not within range. Please try again.')                                    
                except:
                    print('Not a number. Try again.')

        upload(upload_root, item, parent_folder, query, service)
        print('\n')
        
    # Print uploads which have been cancelled by user.
    if len(man_upload) > 0:
        print('You have decided to not upload the following files.')
        for item in man_upload:
            print(item)

        if os.path.exists('skipped uploads.txt'):
            print('A skipped uploads.txt file already exists. Please back up the information in the file if needed.'
                + 'WARNING: The file will be overwritten if continued, and this is irreversible.')

            print('\n<y to continue, n to skip writing>\n')
            pressedKey = m.getch().decode('ASCII')
            while True:
                if pressedKey == 'y':
                    break
                if pressedKey == 'n':
                    return
                pressedKey = m.getch().decode('ASCII')                    

        with open('manual_upload.txt', 'w') as file:
            for item in man_upload:
                file.write(item + '\n')

        print('A list of these files has been generated in manual_upload.txt\n')

    # Print new folders made by the script
    if len(new_folders) > 0:
        print('New folders added to the Drive:')
        for item in new_folders:
            print(item)

        with open('new_folders.txt', 'w') as file:
            for item in new_folders:
                file.write(item + '\n')

        print('Attempting to share new folders with email addresses.\n')
        change_permissions.main()

    if len(man_upload) > 0:
        print('These files could not be uploaded:')
        for item in man_upload:
            print(item)
                    

        
def upload(upload_root, file_name, parent_folder, query, service):
    upload_root_id = upload_root.get('id')
    query = "name = 'MOCKS' and '" + upload_root_id + "' in parents and trashed = False"
    mock_folder_list = search(query, service)
    try:
        upload_folder = create_mock_folder(mock_folder_list, service, upload_root_id)
    except Exception:
        error()
        return

    upload_folder_id = upload_folder.get('id')
    # Search for preexisting files with given name and delete
    query = "name = '" + file_name + "' and '" + upload_folder_id +"' in parents and trashed = False"
    file_duplicates = search(query, service)
    if len(file_duplicates) > 0:
        print('Duplicates found for ' + file_name + '. Deleting duplicates...')
        for file in file_duplicates:
            service.files().delete(fileId=file.get('id')).execute()

    file_metadata = {
        'name': file_name,
        'parents': [upload_folder_id]
    }
    try:                
        media = MediaFileUpload('Scripts\\' + file_name,
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
        print('An error occurred. File ' + file_name + ' could not be uploaded.')
            

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
        print('Are you sure you want to name the new folder ' + folder_name + '? <y to confirm, any other key to retry>')
        if m.getch().decode('ASCII') == 'y':
            # Check for existing folders with given name
            query = ("name = '" + folder_name +  "' and "
                + "mimeType = 'application/vnd.google-apps.folder' and '" + parent_id + "' in parents and trashed = False")
            possible_duplicates = search(query, service)

            if len(possible_duplicates) == 0:
                # Let user choose whether they want to try again
                print('The folder name you entered does not currently exist in Drive. Do you want to confirm or try again? <y to confirm, any other key to try again>')
                if m.getch().decode('ASCII') != 'y':
                    continue
                break

            if len(possible_duplicates) == 1:
                print('There seems to be a folder with the specified name. Do you want to upload to the existing folder? <y to confirm, any other key to skip>')
                if m.getch().decode('ASCII') == 'y':
                    upload_root = possible_duplicates[0]
                    return upload_root

            elif len(possible_duplicates) > 1:
                print('Oops. There seems to be multiple folders with the specified name. Too lazy to implement this. Upload manually for now. :p')
                man_upload.append(file_name)
                return
    
    file_metadata = {
        'name': folder_name,
        'parents': [parent_id],
        'mimeType': 'application/vnd.google-apps.folder'
        }

    try:
        upload_root = service.files().create(body=file_metadata, fields='id').execute()
        new_folders.append(folder_name)
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
