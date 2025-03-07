import time
from bs4 import BeautifulSoup
from urllib import parse, request

def _get_google_query_url(keyword, file_type, cdr):
    url = None
        
    query = dict(q = keyword, 
                 tbm = 'isch',
                 tbs = cdr+',ift:'+file_type,

                 sca_esv='1c09b98d33921ce0',
                sxsrf='ADLYWILOkI0IE3ZV9k9lrC3cUTqhpd42mA:1728931684412',
                udm=2,
                fbs='AEQNm0DbD-6Ra7hdAYjSdHa3yn9y1CSPL8wbnEGUWdo563X5tJmgOfqKHgsoc3CPoh2k-sBVqemMdPhFVn8-WDJrsp46kl3GU4XYS04ya3CjwxwlLpguzjI_iqV3Ho7qqI122iCHwqAal0ytm5WCC006Kzwe69P7qc-7vv-dAWkLJ49NnnWnbHitZYkBJvuroncc2P9Y_leMlmQdtabeqJ4ZPUCfBgLnxw',
                sa='X',
                ved='2ahUKEwiGp4-3xI6JAxW8B9sEHSEwEYwQtKgLegQIDRAB',
                biw=1728,
                bih=993,
                dpr=2,
                 )
    
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
    soup = BeautifulSoup(page, 'html.parser')
    images_tags = soup.find_all("img")
    image_urls = [image_tag.get("src") for image_tag in images_tags if image_tag.has_attr("src") and image_tag.get("src").startswith("http")]
    return image_urls if len(image_urls) < 20 else image_urls[:20]

def _get_images_source_sites(page):
    soup = BeautifulSoup(page, 'html.parser')

    image_to_containing_a_tag = {}
    for a_tag in soup.find_all('a'):
        descendants = a_tag.find_all(True, recursive = True)
        
        for desc in descendants:
            if desc.name == 'img':
                if len(desc.find_parents()) - len(a_tag.find_parents()) == 2:
                    image_to_containing_a_tag[desc.get("src")] = a_tag
                    break

    low_quality_image_url_to_source = {}
    for low_quality_image, a_tag in image_to_containing_a_tag.items():
        if a_tag.has_attr("href") and a_tag.get("href"):
            a_href = a_tag.get("href")
            source = parse.parse_qs(parse.urlparse(a_href).query).get('url', [None])[0]
            low_quality_image_url_to_source[low_quality_image] = source
    
    return low_quality_image_url_to_source

def get_image_urls(keyword, file_type, cdr):
    query_url = _get_google_query_url(keyword, file_type, cdr)
    raw_html =  (_download_page(query_url))
    # with open('/Users/ofirelias/blabla.html', 'wb') as f:
    #     f.write(raw_html.encode())
    low_quallity_image_to_source_sites = _get_images_source_sites(raw_html)
    low_quallity_image_to_high_quality_candidates = {}
    for low_quallity_image, source_site in low_quallity_image_to_source_sites.items():
        try:
            source_site_raw_html =  (_download_page(source_site))
            time.sleep(0.1)
            low_quallity_image_to_high_quality_candidates[low_quallity_image] = _extract_image_urls_from_page(source_site_raw_html)    
        except Exception:
            pass

    return {low_quallity: high_quallity_candidates
            for low_quallity, high_quallity_candidates
            in low_quallity_image_to_high_quality_candidates.items()
            if len(high_quallity_candidates) > 0}
