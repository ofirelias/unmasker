import os
import uuid
import time
import os
import os.path as osp
import fnmatch
import datetime
import uuid
import shutil

from download_image import download_image, is_same_image
from get_images_urls import get_image_urls

NAMES_PATH = "mask_detection_from_kaggle/input/celebrity-face-image-dataset"
DEST_PATH = "mask_detection_from_kaggle/output/masked-celebs"

def list_folders_in_path(path):
    folders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
    return folders

save_dir = DEST_PATH 

########### Default CONFIGS ###########
CONFIGS = {}

# How many images you want to download for each class. Google will only return 100 images at most for one search
CONFIGS[u'num_downloads_for_each_class'] = 100

# image type to search
CONFIGS[u'search_file_type'] = 'jpg'

# Because google only returns at most 100 results for each search query,
# we must send many search queries to get more than 100 results.
# We need to set cdr (date range, in the form of "tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}") to tell google
# we want to search images in some date range (start_date, end_date),
# so as to get different results for each search query.
# CONFIGS[u'search_cdr_days'] is the days between cd_min and cd_max.
CONFIGS[u'search_cdr_days'] = 60

CONFIGS[u'output_prefix'] = 'download_urls'
CONFIGS[u'output_suffix'] = 'google'

########### End of Default CONFIGS ###########

CONFIGS[u'save_dir'] = save_dir + '/'
if not osp.exists(CONFIGS[u'save_dir']):
    os.mkdir(CONFIGS[u'save_dir'])

########### End of CONFIGS ###########
############## Functions to get date/time strings ############       
def get_current_date():
    tm = time.gmtime()
    date = datetime.date(tm.tm_year, tm.tm_mon, tm.tm_mday)   
    return date
    
def get_new_date_by_delta_days(date, delta_days):
    delta = datetime.timedelta(delta_days)
    new_date = date + delta
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
    
def main():
    t0 = time.time()

    i = 0

    cur_date = get_current_date()

    celebrity_names = list_folders_in_path(NAMES_PATH)
    
    class_urls_file_prefix = CONFIGS[u'output_prefix'] + '_' + "celebs"

    # load pre-saved download parameters, actually cd_min for date range
    cd_max = cur_date

    params_file = osp.join(CONFIGS[u'save_dir'], class_urls_file_prefix + '_params_' + CONFIGS[u'output_suffix'] + '.txt')
    params_list = []
    fp_params = open(params_file, 'a+')
    for line in fp_params:
        line = line.strip()
        if line!='':
            params_list.append(line)
            
    if len(params_list) > 0:
        splits = params_list[-1].split('/')
        if len(splits) == 3:
            cd_max = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
    
    cd_min = get_new_date_by_delta_days(cd_max, -CONFIGS[u'search_cdr_days'])   
    
    cdr_enabled = False
    
    hashes = []
    while True:
        if cdr_enabled:
            cdr = 'cdr:1,cd_min:{},cd_max:{}'.format(cd_min.strftime('%m/%d/%Y'), cd_max.strftime('%m/%d/%Y') + ' and ' + cd_max.strftime("%Y/%m/%d"))
        else:
            cdr = ''
                
        # Google only return 100 images at most for one search. So we may need to try many times
        total = 0
        for celeb_name in celebrity_names:
            count = 0
            keyword = "{} wearing mask".format(celeb_name)
            celeb_path = osp.join(CONFIGS[u'save_dir'], keyword)
            if not osp.exists(celeb_path):
                os.mkdir(celeb_path)
            
            lq_image_to_hq_image_candidates = get_image_urls(keyword, CONFIGS[u'search_file_type'], cdr)

            #####
            temp_dir = f"{celeb_path}/temp"
            if not osp.exists(temp_dir):
                os.mkdir(temp_dir)
            lq_path = f"{temp_dir}/lq_image"
            if not osp.exists(lq_path):
                os.mkdir(lq_path)
            candidates_path = f"{temp_dir}/candidates"
            if not osp.exists(candidates_path):
                os.mkdir(candidates_path)
            for lq_image, hq_image_candidates in lq_image_to_hq_image_candidates.items():
                try:
                    save_image_name = f"{lq_path}/lq_image.{CONFIGS['search_file_type']}"
                    lq_hash = download_image(lq_image, save_image_name)
                    has_image_downloaded_already = any([is_same_image(hash, lq_hash) for hash in hashes])
                    if has_image_downloaded_already:
                        continue
                    for hq_image_candidate in hq_image_candidates:
                        img_name = str(uuid.uuid4())
                        candidate_path = f"{candidates_path}/{img_name}.{CONFIGS['search_file_type']}"
                        candidate_hash = download_image(hq_image_candidate, candidate_path)
                        if is_same_image(lq_hash, candidate_hash):
                            final_path = f"{celeb_path}/{img_name}.{CONFIGS['search_file_type']}"
                            os.rename(candidate_path, final_path)
                            count += 1
                            # print(f"Succeed to download {final_path} from {hq_image_candidate}")
                            continue
                except Exception:
                    pass
            shutil.rmtree(temp_dir)
            print(f"Downloaded {count} images for {keyword}")
            total += count
            ####

        if cdr_enabled:
            fp_params.write('{}/{}/{}\n'.format( cd_min.year, cd_min.month, cd_min.day))
            cd_max = cd_min
            cd_min = get_new_date_by_delta_days(cd_max, -CONFIGS[u'search_cdr_days'])               
        else:
            fp_params.write('{}/{}/{}\n'.format( cd_max.year, cd_max.month, cd_max.day))
            cdr_enabled = True

        fp_params.flush()
            
        if (total / len(celebrity_names)) >= CONFIGS[u'num_downloads_for_each_class']:
            break

    fp_params.close()
    i = i + 1

    print("end loop {}", i)
    t1 = time.time()    # stop the timer
    total_time = t1 - t0   # Calculating the total time required to crawl, find and download all the links of 60,000 images

if __name__ == "__main__":
    main()