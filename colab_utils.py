from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import io, os

def googledrive_auth():
    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    return drive, gauth

def upload(filename):
    """
        upload a file 'filename' to google drive
    """
    drive, gauth = googledrive_auth()

    file_upload = drive.CreateFile()
    file_upload.SetContentFile(filename)
    file_upload.Upload() # Upload the file.
    
    print('title: %s, mimeType: %s' % (file_upload['title'], file_upload['mimeType']))

def download(filename, dest_file=None):
    """
        download a file 'filename' from google drive to a specific directory 'dest_file'

        example : download('kaggle.json', dest_file='/content/.kaggle/')
    """
    drive, gauth = googledrive_auth()

    drive_service = build('drive', 'v3')
    results = drive_service.files().list(
            q="name = '{}'".format(filename), fields="files(id)").execute()
    results_files = results.get('files', [])

    if dest_file is not None:
        filename_dest = dest_file + filename
        os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
    else:
        filename_dest = filename
        
    request = drive_service.files().get_media(fileId=results_files[0]['id'])
    fh = io.FileIO(filename_dest, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    os.chmod(filename_dest, 600)