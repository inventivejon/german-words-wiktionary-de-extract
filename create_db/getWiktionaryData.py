import hashlib
import requests
import os.path

def md5Checksum(filePath,url):
    m = hashlib.md5()
    if url==None:
        with open(filePath, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()
    else:
        r = requests.get(url)
        for data in r.iter_content(8192):
             m.update(data)
        return m.hexdigest()

def FileExists(filename):
    if os.path.isfile(filename):
        return True
    else:
        return False

def DownloadNotNeeded(filename, url):
    filename_lastmodified = filename + '_lastmodified'
    # Check based on header field Last-Modified - Tue, 03 Dec 2019 07:02:38 GMT
    lastmodified_remote = ''
    try:
        handle = open(filename_lastmodified, 'r')
        lastmodified_local = handle.read()
        handle.close()
        print("Found local lastmodified information {}".format(lastmodified_local))
        response = requests.head(url)
        lastmodified_remote = response.headers['Last-Modified']
        print("Found remote lastmodified information {}".format(lastmodified_remote))
        if lastmodified_local == lastmodified_remote:
            return True
    except:
        pass
    return False

def DownloadIfNeeded(filename, url):
    print("Check if file needs to be downloaded")
    if FileExists(filename):
        print("File already exists. Checking remote for newer version")
        try:
            if DownloadNotNeeded(filename, url):
                print("Version is the same. No download needed")
                return
        except:
            print("Remote check failed")
            pass
    filename_lastmodified = filename + '_lastmodified'
    try:
        print("Removing old file if necessary")
        os.remove(filename)
        os.remove(filename_lastmodified)
    except:
        pass
    print("Starting download")
    myfile = requests.get(url)
    print("Finished download")
    print("Writing content to file")
    open(filename, 'wb').write(myfile.content)
    print("Finished writing content")
    print("Calculating md5 hash from local file")
    md5_local = md5Checksum(filename,None)
    print("Calculating md5 hash from remote file")
    md5_remote = md5Checksum(None,url)

    print ("checksum_local : {}".format(md5_local))
    print ("checksum_remote : {}".format(md5_remote))

    if md5_local != md5_remote:
        print("md5 test failed. Retry download")
        os.remove(filename)
        DownloadIfNeeded(filename, url)
    else:
        print("File downloaded successfully")
        lastmodified_remote = myfile.headers['Last-Modified']
        print("Updating file information {}".format(lastmodified_remote))
        handle = open(filename_lastmodified, 'w+')
        handle.write(lastmodified_remote)
        handle.close()