#!/usr/bin/env python

import os
import ssl
import urllib.request
import zipfile

import certifi


def download_file(url: str, filepath: str) -> bool:
    # print(f'Downloading {url} to {filepath}...', flush=True)
    try:
        if url.startswith('https://'):
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(url, context=ssl_context) as resp, open(filepath, 'wb') as file:
                file.write(resp.read())
        else:
            urllib.request.urlretrieve(url, filepath)

        # If the download file was a zip, extract the contents
        if filepath.endswith('.zip'):
            extract_dir = os.path.dirname(filepath)
            # print(f'Extracting files from {filepath} to {extract_dir}...', flush=True)
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            os.remove(filepath)
        return True
    except Exception:
        print(f'ERROR: Failed to download {url}', flush=True)
    return False
