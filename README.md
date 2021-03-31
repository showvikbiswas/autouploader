# AutoUploader v1.0

This simple Python scripts lets you upload your checked scripts to Google Drive with ease. To use this, you will need the following prerequisites:

1. Python
2. pip
3. Google Drive API

We'll look at how to properly configure your computer so that you can run the Python script. If you have these installed, please skip to **Using the Script**.

## Python ##
Download the latest version of Python from https://www.python.org/downloads/ and install. This should not be a problem. Restart your computer to ensure that .py files are associated with the Python interpreter.

## pip ##
Download pip from https://bootstrap.pypa.io/. You should download the get-pip.py file. Once downloaded, run the file to install pip. (Note: This step depends on proper completion of the last step.)

## Google Drive API ##
To install the Google Drive API, open Command Prompt and run the following command:
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Using the Script ##
The script is currently designed for handling the May 2021 mocks only. The script presently works as follows: it reads the answer papers present on your machine, and looks for folders in the specified parent Google Drive folder. Upon successfully finding a match, it automatically uploads the paper in a subfolder called "MOCKS". There are a couple of measures implemented for cases where there are no matches for a name, or multiple matches for a single name. You'll get to the hang of it, don't worry.

To use the program, download all the files and place them in a single folder. Now in **this** folder, create another folder named **Scripts**, and place all the checked papers inside the folder. Run **start.bat**. When run, a browser window will ask you to sign in to the required Google account (i.e. the one with the student folders). The rest of the program is pretty self-explanatory, and I hope you will not run into any problems. For reference, the work-flow of the program is listed below.

1. You have to choose the parent directory where all the student folders are placed.
2. The script then searches the "Scripts" folder in your computer and tries to upload each PDF to the designated folder only if it finds a perfect match of a folder name with the file name.
3. If not, the script skips that PDF and keeps track of it.
4. Once all the perfect matches are uploaded, the skipped ones are then handled. You can choose to upload these or not. The ones that you plan to not upload at all are listed in a file named **manual_upload.txt** which you can use for future reference.
5. Once these are handled, the script then tries to share the **newly created folders** with email addresses. If you don't know any email address, you can simply skip the sharing process for that folder. However, if you skip sharing a folder, you will have to share that folder manually later.

**Important:** Do not delete any files that are automatically created by the script. Altering any of these might cause the script to crash.

**Important:** In the case of connectivity issues, close the program and restart once you have ensured a proper internet connection. I have not dealt with connectivity issues properly. I intend to, in the future.
