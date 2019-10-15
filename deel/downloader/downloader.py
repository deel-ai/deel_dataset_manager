from __future__ import division
from __future__ import print_function

import argparse
import gzip
import zipfile
import os
import sys
import shutil

import requests
DEEL_BASE_DIR = os.path.join(os.getenv("HOME"), ".deeldataset")

try:
    from urllib.error import URLError
    from urllib.request import urlretrieve
except ImportError:
    from urllib2 import URLError
    from urllib import urlretrieve

def download_progress(file_name, url):
    print("Downloading %s from %s" % (file_name, url))

    with open(file_name, 'wb') as f:
        print(url)
        response = requests.get(url, stream=True, verify=True,
                                auth=("deel-datasets", "e]{qE/Pc65z'Nt?zLe-cK!_y?6f6"))
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                sys.stdout.flush()

def download(file_name, url, forceDownload):
    if os.path.exists(file_name) and not forceDownload:
        print('{} already exists, skipping ...'.format(file_name))
    else:
        try:
            download_progress(file_name, url)
        except Exception as err:
            print(err)
            raise RuntimeError('Error downloading resource!')
        finally:
            # Just a newline.
            print()

def removeArchiveAndExtracted(datasetFolder, archiveName):
    localArchivePath = os.path.join(datasetFolder, archiveName)
    localArchivePathExtracted = localArchivePath + "_extracted"

    if (os.path.exists(localArchivePath)):
        os.remove(localArchivePath)
    if (os.path.exists(localArchivePathExtracted)):
        shutil.rmtree(localArchivePathExtracted)

def downloadDataset(datasetName, urlList, forceDownload=False):
    datasetFolder = os.path.expanduser(os.path.join(DEEL_BASE_DIR, datasetName))
    os.makedirs(datasetFolder, exist_ok=True)
    pathExtracted = []

    for url in urlList:
        archiveName = url.rsplit('/', 1)[-1]
        if forceDownload or not os.path.exists(os.path.join(datasetFolder, archiveName + "_extracted")):
            removeArchiveAndExtracted(datasetFolder, archiveName)
            downloadPath = os.path.join(datasetFolder, archiveName)
            download(downloadPath, url, False)
            unzipped_path = unzip(downloadPath, archiveName)
            pathExtracted.append(unzipped_path)
        else:
            pathExtracted.append(os.path.join(datasetFolder, archiveName + "_extracted"))

    return pathExtracted

def unzip(zipped_path, archiveName, quiet=False):
    unzipped_path = zipped_path + "_extracted"
    if os.path.exists(unzipped_path):
        if not quiet:
            print('{} already exists, skipping ... '.format(unzipped_path))
        return
    compressionType = zipped_path.split(".")[-1]
    if (compressionType == "zip"):
        with zipfile.ZipFile(zipped_path, 'r') as zip_ref:
            zip_ref.extractall(unzipped_path)

        zip_ref.close()
    elif (compressionType == "gz"):
        with gzip.open(zipped_path, 'rb') as zipped_file:
            os.makedirs(unzipped_path)
            with open(os.path.join(unzipped_path, os.path.splitext(archiveName)[0]), 'wb') as unzipped_file:
                unzipped_file.write(zipped_file.read())
                if not quiet:
                    print('Unzipped {} ...'.format(zipped_path))

    else:
        os.makedirs(unzipped_path)
        shutil.move(zipped_path, os.path.join(unzipped_path, archiveName))

    return unzipped_path
