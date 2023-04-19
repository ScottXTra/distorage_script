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
import urllib.request



def download_file(meta_file_path):
    f = open(meta_file_path)
    data = json.load(f)
    list_of_files = []
    for file_part_url in data['file_part_urls']:
        url = file_part_url
        r = requests.get(url, allow_redirects=True)
        file_name = os.path.basename(urlparse(file_part_url).path)
        open(os.path.basename(urlparse(file_part_url).path), 'wb').write(r.content)
        list_of_files.append(file_name)
    return list_of_files
    
        
def combine_file_parts(list_of_file_paths,output_file_name):
    with open(output_file_name, "ab") as base_file:
        for file_path in list_of_file_paths:
            base_file.write(open(file_path, "rb").read())        

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='This is a template for a main function')
    parser.add_argument('-m', '--meta_file', help='Path to meta file of the file you want to download from discord CDN', required=True)
    # Parse command line arguments
    args = parser.parse_args()
    meta_file_path = args.meta_file
    file_parts = download_file(meta_file_path)
    combine_file_parts(file_parts,file_parts[0][:-1])
    for file_part in file_parts:
        os.remove(file_part)