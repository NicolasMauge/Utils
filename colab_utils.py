from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

import os

def googledrive_auth():
    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    return drive, gauth

def upload(filename):
    drive, gauth = googledrive_auth()

    file_upload = drive.CreateFile()
    file_upload.SetContentFile(filename)
    file_upload.Upload() # Upload the file.
    
    print('title: %s, mimeType: %s' % (file_upload['title'], file_upload['mimeType']))

def download(filename, dest_file=None):
    drive, gauth = googledrive_auth()

    if dest_file is not None:
        # choose a local (colab) directory to store the data.
        local_download_path = os.path.expanduser(dest_file)
        try:
          os.makedirs(local_download_path)
        except: pass
        filename_with_directory = os.path.join(local_download_path, filename)
    else:
        filename_with_directory = filename

    #results = drive.files().list(q="name = '"+filename+"'", fields="files(id)").execute()
    results = drive.ListFile({'q': "title = '{}' and trashed=false".format(filename)}).GetList()
    #file_id = results.get('files', [])
    #file_id = results[0]['id']

    # Initialize GoogleDriveFile instance with file id.
    file_download = drive.CreateFile({'id': results[0]['id']})
    file_download.GetContentFile(filename_with_directory) # Download file as 'catlove.png'.

    print('title: {}, mimeType: {}, id: {}'.format(file_download['title'], file_download['mimeType'], file_download['id']))


def download_v2(filename, dest_file=None):
    drive, gauth = googledrive_auth()

    drive_service = build('drive', 'v3')
    results = drive_service.files().list(
            q="name = '{}'".format(filename), fields="files(id)").execute()
    results_files = results.get('files', [])

    if dest_file is not None:
        filename_dest = dest_file + filename
    else:
        filename_dest = filename
        
    #filename = "/content/.kaggle/kaggle.json"
    os.makedirs(os.path.dirname(filename_dest), exist_ok=True)
    request = drive_service.files().get_media(fileId=results_files[0]['id'])
    fh = io.FileIO(filename_dest, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    os.chmod(filename_dest, 600)