import os
import uuid
from bs4 import BeautifulSoup
import time
import os
import os.path as osp
import fnmatch
from urllib import request
import datetime

from get_images_urls import get_image_urls

NAMES_PATH = "/Users/ofirelias/Downloads/Celebrity Faces Dataset"
DEST_PATH = "/Users/ofirelias/Downloads/Masked Celebrities"

def list_folders_in_path(path):
    folders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
    return folders

save_dir= DEST_PATH 
num_downloads_for_each_class= 10 
search_file_type= "jpg" 
search_keywords_dict= {
        "animal": [
            "cat", 
            "dog"
        ]
    }
search_cdr_days= 60,
output_prefix= "download_urls",
output_suffix= "google"


########### CONFIGS ###########
# Path to config_file
config_file = './config.json'

########### Default CONFIGS ###########
CONFIGS = {}

# How many images you want to download for each class. Google will only return 100 images at most for one search
CONFIGS[u'num_downloads_for_each_class'] = 200

# image type to search
CONFIGS[u'search_file_type'] = 'jpg'

# Because google only returns at most 100 results for each search query,
# we must send many search queries to get more than 100 results.
# We need to set cdr (date range, in the form of "tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}") to tell google
# we want to search images in some date range (start_date, end_date),
# so as to get different results for each search query.
# CONFIGS[u'search_cdr_days'] is the days between cd_min and cd_max.
CONFIGS[u'search_cdr_days'] = 60

# This dict is used to search keywords. You can edit this dict to search for google images of your choice. You can simply add and remove elements of the list.
# {class1:[list of related keywords], class2:[list of related keywords]...}
CONFIGS[u'search_keywords_dict'] = {'animal':['cat', 'dog'],
                                    'fruit':[u'apple', u'banaba']}

CONFIGS[u'output_prefix'] = 'download_urls'
CONFIGS[u'output_suffix'] = 'google'

########### End of Default CONFIGS ###########

CONFIGS[u'save_dir'] = save_dir + '/'
if not osp.exists(CONFIGS[u'save_dir']):
    os.mkdir(CONFIGS[u'save_dir'])

########### End of CONFIGS ###########

########### Functions to Load downloaded urls ###########
def load_url_files(_dir, file_name_prefix):
    url_list = []
    
    ttl_url_list_file_name = osp.join(_dir, file_name_prefix +'_all.txt')
    if osp.exists(ttl_url_list_file_name):
        fp_urls = open(ttl_url_list_file_name, 'r')        # Open the text file called database.txt
        
        i = 0
        for line in fp_urls:
            line = line.strip()
            if len(line)>0:
                splits = line.split('\t')
                url_list.append(splits[0].strip())
                i=i+1
                
        fp_urls.close()             
    else:
        url_list = load_all_url_files(_dir, file_name_prefix)
            
    return url_list     

def load_all_url_files(_dir, file_name_prefix):
    url_list = []
    
    for file_name in os.listdir(_dir):
        if fnmatch.fnmatch(file_name, file_name_prefix +'*.txt'):
            file_name = osp.join(_dir, file_name)
            fp_urls = open(file_name, 'r')        #Open the text file called database.txt
            
            for line in fp_urls:
                line = line.strip()
                if len(line) > 0:
                    splits = line.split('\t')
                    url_list.append(splits[0].strip())
            fp_urls.close()
            
    return url_list         
########### End of Functions to Load downloaded urls ###########

############## Functions to get date/time strings ############       
def get_current_date():
    tm = time.gmtime()
    date = datetime.date(tm.tm_year, tm.tm_mon, tm.tm_mday)   
    return date
    
def get_new_date_by_delta_days(date, delta_days):
    delta = datetime.timedelta(delta_days)
    new_date = date+delta
    return new_date
    
# Make a string from current GMT time
def get_gmttime_string():
    _str = time.strftime("GMT%Y%m%d_%H%M%S", time.gmtime())
    return _str
 
# Make a string from current local time
def get_localtime_string():
    _str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    return _str
############## End of Functions to get date/time strings ############          
    
############## Functions to get real urls and download images ############       
def download_image(url, save_dir, loaded_urls=None):
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
    with request.urlopen(req) as response:
        real_url = response.geturl()
        
        if loaded_urls and real_url in loaded_urls:
            return None, None
        
        img_name = str(uuid.uuid4())
        save_image_name = f"{save_dir}/{img_name}.{CONFIGS['search_file_type']}"
        with open(save_image_name, 'wb') as output_file:
            data = response.read()
            output_file.write(data)
        return real_url, save_image_name

############## End of Functions to get real urls and download images ############         
    
def main():
    t0 = time.time()

    i = 0

    cur_date = get_current_date()

    time_str = get_gmttime_string()

    celebrity_names = list_folders_in_path(NAMES_PATH)
    
    class_urls_file_prefix = CONFIGS[u'output_prefix'] + '_' + "celebs"
    
    items = load_url_files(CONFIGS[u'save_dir'], class_urls_file_prefix)    
    loaded_urls_num = len(items)

    # load pre-saved download parameters, actually cd_min for date range
    cd_max = cur_date

    params_file = osp.join(CONFIGS[u'save_dir'], class_urls_file_prefix + '_params_' + CONFIGS[u'output_suffix'] + '.txt')
    params_list = []
    fp_params = open(params_file, 'a+')
    for line in fp_params:
        line = line.strip()
        if line!='':
            params_list.append(line)
            
    if len(params_list)>0:
        splits = params_list[-1].split('/')
        if len(splits)==3:
            cd_max = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
    
    cd_min = get_new_date_by_delta_days(cd_max, -CONFIGS[u'search_cdr_days'])   
    
    output_all_urls_file  = osp.join(CONFIGS[u'save_dir'], class_urls_file_prefix +'_all.txt')        
    fp_all_urls = open(output_all_urls_file, 'a+')
    
    output_urls_file = osp.join(CONFIGS[u'save_dir'], class_urls_file_prefix + '_' + time_str + '_' + CONFIGS[u'output_suffix'] + '.txt')
    fp_urls = open(output_urls_file, 'a+')
    
    cdr_enabled = False
    
    while True:
        if cdr_enabled:
            cdr = 'cdr:1,cd_min:{},cd_max:{}'.format(cd_min.strftime('%m/%d/%Y'), cd_max.strftime('%m/%d/%Y') + ' and ' + cd_max.strftime("%Y/%m/%d"))
        else:
            cdr = ''
                
        # Google only return 100 images at most for one search. So we may need to try many times
        for celeb_name in celebrity_names:
            keyword = "{} wearing mask".format(celeb_name)
            celeb_name = osp.join(CONFIGS[u'save_dir'], keyword)
            if not osp.exists(celeb_name):
                os.mkdir(celeb_name)
            
            new_items = get_image_urls(keyword, CONFIGS[u'search_file_type'], cdr)
            print(keyword)
            print(new_items)

            for url in new_items:
                real_url, save_name = download_image(url, celeb_name, items)
                if real_url and real_url not in items:
                    items.append(real_url)
                    fp_all_urls.write(real_url + '\t' + save_name + "\n")
                    fp_urls.write(real_url + '\t' + save_name + "\n")
                    print("Succeed to download {}", url)

            fp_all_urls.flush()                    
            fp_urls.flush()

        if cdr_enabled:
            fp_params.write('{}/{}/{}\n'.format( cd_min.year, cd_min.month, cd_min.day))
            cd_max = cd_min
            cd_min = get_new_date_by_delta_days(cd_max, -CONFIGS[u'search_cdr_days'])               
        else:
            fp_params.write('{}/{}/{}\n'.format( cd_max.year, cd_max.month, cd_max.day))
            cdr_enabled = True

        fp_params.flush()
            
        if len(items) >= loaded_urls_num + CONFIGS[u'num_downloads_for_each_class']:          
            break

    fp_params.close()
    fp_all_urls.close()
    fp_urls.close()

    i = i + 1

    print("end loop {}", i)
    t1 = time.time()    # stop the timer
    total_time = t1 - t0   # Calculating the total time required to crawl, find and download all the links of 60,000 images

if __name__ == "__main__":
    main()