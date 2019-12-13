import hashlib
import requests
import os.path
import sys

def log(handle, content):
    try:
        handle.write(content.encode(sys.stdout.encoding, errors='replace').decode("utf-8") + '\n')
    except:
        pass
    print(content)
    
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

def DownloadNotNeeded(handle, filename, url):
    filename_lastmodified = filename + '_lastmodified'
    # Check based on header field Last-Modified - Tue, 03 Dec 2019 07:02:38 GMT
    lastmodified_remote = ''
    try:
        handle_lastmodified = open(filename_lastmodified, 'r')
        lastmodified_local = handle_lastmodified.read()
        handle_lastmodified.close()
        log(handle, "Found local lastmodified information {}".format(lastmodified_local))
        response = requests.head(url)
        lastmodified_remote = response.headers['Last-Modified']
        log(handle, "Found remote lastmodified information {}".format(lastmodified_remote))
        if lastmodified_local == lastmodified_remote:
            return True
        else:
            log(handle, "Local version {} is different from remote version {}".format(lastmodified_local, lastmodified_remote))
    except:
        pass
    return False

def DownloadIfNeeded(handle, filename, url):
    log(handle, "Check if file needs to be downloaded")
    if FileExists(filename):
        log(handle, "File already exists. Checking remote for newer version")
        try:
            if DownloadNotNeeded(handle, filename, url):
                log(handle, "Version is the same. No download needed")
                return
        except:
            log(handle, "Remote check failed")
            pass
    log(handle, "Version is not the same or file does not exist.")
    filename_lastmodified = filename + '_lastmodified'
    try:
        log(handle, "Removing old file if necessary")
        os.remove(filename)
        os.remove(filename_lastmodified)
    except:
        pass
    log(handle, "Starting download")
    myfile = requests.get(url)
    log(handle, "Finished download")
    log(handle, "Writing content to file")
    open(filename, 'wb').write(myfile.content)
    log(handle, "Finished writing content")
    log(handle, "Calculating md5 hash from local file")
    md5_local = md5Checksum(filename,None)
    log(handle, "Calculating md5 hash from remote file")
    md5_remote = md5Checksum(None,url)

    log(handle, "checksum_local : {}".format(md5_local))
    log(handle, "checksum_remote : {}".format(md5_remote))

    if md5_local != md5_remote:
        log(handle, "md5 test failed. Retry download")
        os.remove(filename)
        DownloadIfNeeded(handle, filename, url)
    else:
        log(handle, "File downloaded successfully")
        lastmodified_remote = myfile.headers['Last-Modified']
        log(handle, "Updating file information {}".format(lastmodified_remote))
        handle = open(filename_lastmodified, 'w+')
        handle.write(lastmodified_remote)
        handle.close()