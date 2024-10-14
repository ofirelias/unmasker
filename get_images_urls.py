import time
from bs4 import BeautifulSoup
from urllib import parse, request

def _get_google_query_url(keyword, file_type, cdr):
    url = None
        
    query = dict(q = keyword, 
                 tbm = 'isch',
                 tbs=cdr+',ift:'+file_type)
    
    url = 'https://www.google.com/search?' + parse.urlencode(query)
			
    return url
    
def _download_page(url):
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    req = request.Request(url, headers = headers)
    resp = request.urlopen(req)
    respData = str(resp.read())
    return respData

def _extract_image_urls_from_page(page):
    soup = BeautifulSoup(page)
    images_tags = soup.find_all("img")
    return [image_tag.get("src") for image_tag in images_tags if image_tag.has_attr("src") and image_tag.get("src").startswith("http")]
   
def get_image_urls(keyword, file_type, cdr):
    query_url = _get_google_query_url(keyword, file_type, cdr)
    raw_html =  (_download_page(query_url))
    time.sleep(0.1)
    image_url_list = _extract_image_urls_from_page(raw_html)    
    return image_url_list
