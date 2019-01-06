from concurrent.futures.thread import ThreadPoolExecutor
import queue, time, glob, os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from crawl_new_classifier.predictor import Predictor


#from configparser import ConfigParser
#from keras.models import load_model
# from selenium.webdriver.chrome.options import Options
BASE_URL_ = "https://www.mightymatcha.com/"
NUM_SCRAPERS_ = 2
os.chdir('F:\\MachineLearning\\share\\test')

urls_yet_to_be_scraped_ = queue.Queue()
urls_already_scraped_ = queue.Queue()
urls_yet_to_be_scraped_.put(BASE_URL_)
classified_URLs = dict()
running_scrapers_ = queue.Queue()


def scraper_(id_, base_url_):
    def flatten_(url_):
        return "".join(x for x in url_ if x.isalnum()) + ".txt"
    display_ = False
    
    def eval_class(classify,url):
        print('in eval_class: ', url)
        if url not in classified_URLs:
            url_classification = classify.classifier()  
            print('url_classification: ',url_classification)
            classified_URLs[url] = url_classification
        else:
            print('URL already classified')
    
    try:
        print('scrapper id  is : {}'.format(id_))
#        options = Options()
#        options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path='F:\\MachineLearning\\share\\pythoncode\\Crawler\\chromedriver.exe')
        driver.get(url='about:blank')
        try:
            num_iterations_ = 0
            while True:
                try:
#                     print("scraper_ :: {} :: 0 :: {} :: {}".format(id_, running_scrapers_.qsize(), urls_yet_to_be_scraped_.qsize()))
                    url_ = urls_yet_to_be_scraped_.get_nowait()
                    running_scrapers_.put_nowait(1)
                    display_ = True
#                     print("scraper_ :: {} :: 1 :: {}".format(id_, url_))
                    
                    modified_url=flatten_(url_)                                     
                    if modified_url not in glob.glob(modified_url):
                        try:
#                             print("scraper_ :: {} :: 2 :: {}".format(id_, url_))
                            tag=''
                            input_elems=''
                            driver.get(url_)
                            links_in_page = set()
                            # Adding timeout period to makesure the webpage loaded totally so that it fetches links
                            WebDriverWait(driver, 15)
                            links_partial = driver.find_elements_by_partial_link_text('')
                            if links_partial:
                                for i in links_partial:
                                    print("scraper_ :: {} :: 3".format(id_))
                                    if i is not None and i.get_attribute('href') \
                                    and i.get_attribute('href').startswith(base_url_):
                                        print("scraper_ :: {} :: 3a :: {}".format(id_, i.get_attribute('href')))
                                        links_in_page.add(i.get_attribute('href'))
                                    else:
                                        pass
                                        print("scraper_ :: {} :: 3b :: {}".format(id_, "#"))
                                        
                            for div_class in driver.find_elements_by_tag_name("div"):
                                tag+=str(div_class.get_attribute("class")+" ")
                            
                            # Gets the name of the html input elements present in current webpage
                            for div_class in driver.find_elements_by_xpath('//input'):
                                if (div_class.get_attribute("type")).lower() == "submit" or (div_class.get_attribute("type")).lower() == 'hidden':
                                    continue
                                if div_class.get_attribute("title"):
                                    input_elems+=str(div_class.get_attribute("title")+" ")
                                elif div_class.get_attribute("name"):
                                    input_elems+=str(div_class.get_attribute("name")+" ")
                                elif div_class.get_attribute("id"):
                                    input_elems+=str(div_class.get_attribute("id")+" ")
                                else:
                                    input_elems+=str(div_class.get_attribute("class")+" ")
                                
                            # Writes the retrieved webpage scraping elements data into the file  
                            with open(modified_url,'w') as f:
                                print("file operations")
                                f.write(url_+"\n"+tag+"\n"+ "INPUT ELEMENTS OF THE PAGE" + "\n" + "===========================" + "\n" +input_elems)
                            
                            for new_url_ in links_in_page: # get links
                                if not(glob.glob(flatten_(new_url_))):
                                    urls_yet_to_be_scraped_.put_nowait(new_url_)
                                    
                            urls_already_scraped_.put_nowait(url_)                            
                        except Exception as exception_:
                            print(42)
                            print(exception_)
                            pass                        
                    try:
                        print("scraper_ :: {} :: 4a :: {} :: {}".format(id_, running_scrapers_.qsize(), urls_yet_to_be_scraped_.qsize()))
                        _ = running_scrapers_.get_nowait()
                        
                        print("scraper_ :: {} :: 4b :: {} :: {}".format(id_, running_scrapers_.qsize(), urls_yet_to_be_scraped_.qsize()))
                    except queue.Empty as exception_:
                        print("An impossible situation detected - scraper queue found empty")
                        raise exception_
                        
                except queue.Empty as exception_:
                    pass
                except Exception as exception_:
                    raise exception_
                
                num_iterations_ = num_iterations_ + 1
                if running_scrapers_.empty() and urls_yet_to_be_scraped_.empty():
                    if num_iterations_ <= NUM_SCRAPERS_:
                        continue
                    else:
                        print("scraper_ :: {} :: 5a".format(id_))
                        break
                else:
                    if display_:
                        print("scraper_ :: {} :: 5b :: {} :: {}".format(id_, running_scrapers_.qsize(), urls_yet_to_be_scraped_.qsize()))
                    display_ = False
                    continue
            
            return True
        except Exception as exception_:
            print('Exception in scraper with ID {}: {}'.format(id_, str(exception_)))
            return False
    except Exception as exception_:
        print('Exception in scraper with ID {}: {}'.format(id_, str(exception_)))
        return False    

 

start_time_ = time.time()

with ThreadPoolExecutor() as executor_:
    scraper_ids_ = [_ for _ in range(NUM_SCRAPERS_)]
    scraper_base_urls_ = [BASE_URL_ for _ in range(NUM_SCRAPERS_)]
    for scraper_index_, scraper_final_status_ in zip(scraper_ids_, executor_.map(scraper_, scraper_ids_, scraper_base_urls_)):
        print('scraper_index_: ', scraper_index_)
        print('scraper_final_status_: ',scraper_final_status_)
end_time_ = time.time()
#print("{} seconds consumed for {} titles using recursive-multithreaded access".format(end_time_-start_time_,urls_already_scraped_.qsize()))