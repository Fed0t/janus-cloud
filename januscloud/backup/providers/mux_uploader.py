import mux_python
import requests
import os
import time
from mux_python.rest import ApiException


def backup_event(event):

    historical_size = -1
    while historical_size != os.path.getsize(event['event'].src_path):
        historical_size = os.path.getsize(event['event'].src_path)
        time.sleep(1)
    print("File finished modifying - %s." % event['event'].src_path)

    configuration = mux_python.Configuration()
    configuration.username = event['config']['janus']['mux_api_token']
    configuration.password = event['config']['janus']['mux_api_secret']

    try:
        uploads_api = mux_python.DirectUploadsApi(mux_python.ApiClient(configuration))
        create_asset_request = mux_python.CreateAssetRequest(playback_policy=[mux_python.PlaybackPolicy.PUBLIC],
                                                             mp4_support="standard",
                                                             passthrough=str(event['event'].src_path))
        create_upload_request = mux_python.CreateUploadRequest(timeout=3600, new_asset_settings=create_asset_request)
        create_upload_response = uploads_api.create_direct_upload(create_upload_request)
        url = str(create_upload_response.data.url)
        upload(event['event'].src_path, url)
        delete_file(event['event'].src_path)

    except ApiException as e:
        print("Exception when uploading file to Mux Api: %s\n" % e)


def upload(file, url):
    content_path = os.path.abspath(file)
    content_size = os.stat(content_path).st_size

    if content_size == 0:
        return False

    f = open(content_path, "rb")

    index = 0
    offset = 0
    headers = {}
    chunk_size = 6000000

    for chunk in read_in_chunks(f, chunk_size):
        offset = index + len(chunk)
        headers['Content-Range'] = 'bytes %s-%s/%s' % (index, offset-1, content_size)
        index = offset
        try:
            file = {"file": chunk}
            r = requests.put(url, files=file, headers=headers, verify=False)
            print("r: %s, Content-Range: %s" % (r, headers['Content-Range']))
        except Exception as e:
            print('Upload error:  %s\n' % e)


def read_in_chunks(file_object, chunk_size):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def delete_file(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        print("The file does not exist")
