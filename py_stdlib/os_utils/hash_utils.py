import hashlib

# for reference:  http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
# NOTE: md5 and sha1 are intentionally, and explicity excluded due to known security holes
def get_hasher(algorithm="sha256"):
    hasher = None
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha224":
        hasher = hashlib.sha224()
    elif algorithm == "sha384":
        hasher = hashlib.sha384()
    elif algorithm == "sha512":
        hasher = hashlib.sha512()

    return hasher

def checksum(file_name, algorithm="sha256", blocksize=65536):
    hasher = get_hasher(algorithm)
    with open(file_name, "r+b") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hasher.update(block)
    return hasher.hexdigest()
