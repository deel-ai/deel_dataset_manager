from deel.datasets.base.dataset import Dataset
import requests
import re

def load(name, forceDownload=False):
    url = 'https://datasets.deel.ai/' + name + "/latest"
    pattern = "<a href=\"(.*?)\">"
    resRequest = requests.get(url, verify=False, auth=("deel-datasets", "e]{qE/Pc65z\'Nt?zLe-cK!_y?6f6")).text
    filesToDownload = re.findall(pattern, resRequest)
    if (filesToDownload == []):
        raise Exception("Dataset remote does not exist !")
    urls = list(map(lambda file: url + "/" + file, list(filter(lambda file: file != '/', filesToDownload))))
    if (urls == []):
        raise Exception("Dataset remote folder is empty !")

    aDataset = Dataset(urls=urls)
    aDataset.load(name, forceDownload)
    
    return aDataset.unzippedPaths