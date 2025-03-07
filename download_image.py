from urllib import request
from PIL import Image
import imagehash

def download_image(url, path):
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
    with request.urlopen(req) as response:
        real_url = response.geturl()
        with open(path, 'wb') as output_file:
            data = response.read()
            output_file.write(data)
    image_pil = Image.open(path)
    image_hash = hash1 = imagehash.average_hash(image_pil)
    return image_hash

def is_same_image(hash1, hash2):
    difference = hash1 - hash2
    return difference < 0.1