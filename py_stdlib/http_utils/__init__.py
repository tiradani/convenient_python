import os
import urllib2
import urlparse

def wget(url, saveas=""):
    u = urllib2.urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded.file'
    if saveas:
        filename = saveas

    with open(filename, 'wb') as f:
        block_sz = 8192
        while True:
            read_buffer = u.read(block_sz)
            if not read_buffer: break
            f.write(read_buffer)

    return filename
