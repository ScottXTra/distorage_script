
import requests
import json
import sys
import argparse
import os
import json
from random import randint, randrange
import hashlib
import json
import urllib
from urllib.parse import urlparse



def get_sha256(file_path):
    with open(file_path, 'rb') as file:
        sha256 = hashlib.sha256()
        while True:
            data = file.read(8192)
            if not data:
                break
            sha256.update(data)
        return sha256.hexdigest()

def split_binary_file(file_path, nitro_level):
    MAX_FILE_SIZE = 7500000
    if nitro_level == '0':
        MAX_FILE_SIZE = 7500000
    elif nitro_level == '1':
        MAX_FILE_SIZE = 45000000
    elif nitro_level == '2':
        MAX_FILE_SIZE = 99000000

    #num_parts = os.path.getsize(file_path) // MAX_FILE_SIZE
    CHUNK_SIZE = MAX_FILE_SIZE
    #print(os.path.getsize(file_path))
    file_name = os.path.basename(file_path)
    file_number = 1
    list_of_files =[]
    with open(file_path, "rb") as f:
        chunk = f.read(CHUNK_SIZE)
        while chunk:
            new_file_name =file_name + str(file_number)
            list_of_files.append(new_file_name)
            with open(new_file_name, 'wb+') as chunk_file:
                chunk_file.write(chunk)
            file_number += 1
            chunk = f.read(CHUNK_SIZE)
    return list_of_files
    




def get_upload_url(channel_id, file_path, auth_token):
    url = "https://discord.com/api/v9/channels/"+channel_id+"/attachments"
    file_name = os.path.basename(file_path)
    file_size = os.stat(file_name).st_size
    payload = json.dumps({
    "files": [
        {
        "filename": file_name,
        "file_size": file_size,
        "id": "36"
        }
    ]
    })
    headers = {
    'authorization': auth_token,
    'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    #print(response.text)
    responce_json = json.loads(response.text)
    upload_url = responce_json['attachments'][0]['upload_url']
    upload_filename = responce_json['attachments'][0]['upload_filename']
    return upload_file(upload_url,auth_token,file_path,channel_id,file_name,upload_filename)

def upload_file(url,auth_token,file_path,channel_id,file_name,upload_filename):
    f = open(file_path, "rb")
    payload= f.read()
    headers = {
    'authorization': auth_token,
    'Content-Type': 'application/zip'
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    return get_accesse_url(channel_id,file_name,upload_filename,auth_token)

def get_accesse_url(channel_id,file_name,upload_filename,auth_token):
    url = "https://discord.com/api/v9/channels/"+channel_id+"/messages"

    payload = json.dumps({
    "content": "xx",
    "nonce": str(randint(1000000000000000000, 9999999999999999999) ),
    "channel_id": channel_id,
    "type": 0,
    "sticker_ids": [],
    "attachments": [
        {
        "id": "0",
        "filename": file_name,
        "uploaded_filename": upload_filename
        }
    ]
    })
    headers = {
    'authorization': auth_token,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    
    responce_json = json.loads(response.text)
    url = str(responce_json['attachments'][0]['url'])
    return url

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-t', '--token', help='Discord auth token', required=True)
    parser.add_argument('-f', '--file_path', help='Path to the file you want to upload', required=True)
    parser.add_argument('-c', '--channel', help='ID of the channel that is used for storage', required=True)
    parser.add_argument('-n', '--nitro_level', help='0 = no nitro (8 MB limit per file), 1 = nitro basic (50MB limit per file), 2 = nitro pro (100MB limit per file)', required=True)
    
    # Parse command line arguments
    args = parser.parse_args()
    auth_token = args.token
    file_path = args.file_path
    channel_id = args.channel
    nitro_level = args.nitro_level


    file_metadata = {
        "file_name": os.path.basename(file_path),
        "file_size": os.path.getsize(file_path),
        "file_hash_sha256":get_sha256(file_path),
        "file_part_urls":[]
    }
    files = split_binary_file(file_path,nitro_level)
    for file in files:
        url = get_upload_url(channel_id, file, auth_token)
        file_metadata['file_part_urls'].append(url) 
        os.remove(file)

    json_object = json.dumps(file_metadata, indent=4)
    with open('file_metadata/' + str(file_metadata['file_name']) + '.json', 'w') as outfile:
        outfile.write(str(json_object))

    