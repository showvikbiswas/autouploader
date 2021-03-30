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

To use the program, download **autouploader_mocks_2021.py** and **credentials.json** and place them in a single folder. Now in **this** folder, create another folder named **Scripts**, and place all the checked papers inside the folder. Run **autouploader_mocks_2021.py**. When run, a browser window will ask you to sign in to the required Google account (i.e. the one with the student folders).

The program will then ask for the **ID** of the **parent directory**. The parent directory is the folder where all the folders for the students are placed. For example, **OLP MAY 2021** is a parent directory. Open this folder, and copy the ID into the command prompt window. The ID is the weird stuff at the end of the URL of the parent directory. For example, if **OLP MAY 2021** has an address https://drive.google.com/drive/u/6/folders/1Gbc8HwWG5soUBkAa33kM_PAOlwbT9L_L, the ID for the directory is **1Gbc8HwWG5soUBkAa33kM_PAOlwbT9L_L**. Once this is set up, you are ready to go. The rest of the program should be pretty self explanatory.
