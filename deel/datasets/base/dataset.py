from deel.downloader import downloadDataset

class Dataset():
    def __init__(self, urls=[]):
        self.urls = urls
        self.unzippedPaths = []

    def load(self, name, forceDownload=False):
        print("Loading dataset %s @URLs %s" % (name, self.urls) )
        self.unzippedPaths = downloadDataset(name, self.urls, forceDownload)
    
    def getDownloadPAth(self):
        return self.unzippedPaths