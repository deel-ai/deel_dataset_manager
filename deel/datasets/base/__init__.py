from deel.datasets.base.dataset import Dataset
import requests
import re

def load(name, forceDownload=False):
    url = 'https://datasets.deel.ai/' + name + "/latest/"
    pattern = "<a href=\"(.*?)\">"
    resRequest = requests.get(url, verify=True,
                              auth=("deel-datasets", "e]{qE/Pc65z'Nt?zLe-cK!_y?6f6")).text

    filesToDownload = re.findall(pattern, resRequest)
    if not filesToDownload:
        raise Exception('Remote "{}" dataset does not exist.'.format(name))

    urls = [url + '/' + file for file in filesToDownload if not file.startswith('/')]
    if not urls:
        raise Exception('Remote "{}" dataset folder is empty.'.format(name))

    aDataset = Dataset(urls=urls)
    aDataset.load(name, forceDownload)

    return aDataset.unzippedPaths
