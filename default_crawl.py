from concurrent.futures.thread import ThreadPoolExecutor
import queue, time, glob, os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from crawl_new_classifier import forms_latest as scraping
from crawl_new_classifier.logg import ManualLogger
from crawl_new_classifier.predictor import Predictor
import pandas as pd

#http://edmundmartin.com/multi-threaded-crawler-in-python/
BASE_URL_ = "https://www.mightymatcha.com/"
NUM_SCRAPERS_ = 2
os.chdir('D:\\test')
SCRAP_DATA_FRAME = pd.DataFrame()
urls_yet_to_be_scraped_ = queue.Queue()
urls_already_scraped_ = queue.Queue()
urls_yet_to_be_scraped_.put(BASE_URL_)
classified_URLs = dict()
running_scrapers_ = queue.Queue()


def scraper_(id_, base_url_):

    def flatten_(url_):
        return "".join(x for x in url_ if x.isalnum()) + ".txt"

    display_ = False
    
    def eval_class(classify, url):
        print('in eval_class: ', url)
        if url not in classified_URLs:
            url_classification = classify.classifier()  
            print('url_classification: ', url_classification)
            classified_URLs[url] = url_classification
        else:
            print('URL already classified')
    
    try:
        print('scrapper id  is : {}'.format(id_))
#        options = Options()
#        options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path='D:\\IVSSOLH\\Deep_Assurance\\pythoncode\\Crawler\\chromedriver.exe')
        driver.get(url=BASE_URL_)
        try:
            num_iterations_ = 0
            while True:
                try:
#                     print("scraper_ :: {} :: 0 :: {} :: {}".format(id_, running_scrapers_.qsize(), urls_yet_to_be_scraped_.qsize()))
                    url_ = urls_yet_to_be_scraped_.get_nowait()
                    running_scrapers_.put_nowait(1)
                    display_ = True
#                     print("scraper_ :: {} :: 1 :: {}".format(id_, url_))
                    
                    modified_url = flatten_(url_)                                     
                    if modified_url not in glob.glob(modified_url):
                        try:
#                             print("scraper_ :: {} :: 2 :: {}".format(id_, url_))
                            tag = ''
                            driver.get(url_)
                            links_in_page = set()
                            # Adding timeout period to makesure the webpage loaded totally so that it fetches links
                            WebDriverWait(driver, 10)
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
                                tag += str(div_class.get_attribute("class") + " ")

                            # Writes the retrieved webpage scraping elements data into the file  
                            with open(modified_url, 'w') as f:
                                print("file operations")
                                f.write(url_ + "\n" + tag)
                                
                            scrap_input_elements(url_, driver)
                            
                            for new_url_ in links_in_page:  # get links
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


def scrap_input_elements(url, driver):
    """
    Method to scrap all the input elements of a html page.
    """
    global SCRAP_DATA_FRAME
    logger = ManualLogger(url, 550)
    page_df = scraping.read_prop_file(url, logger)
    #raw_input_html_eles = driver.find_elements_by_xpath('//input')
    raw_input_html_eles = scraping.find_elements(driver.find_elements_by_tag_name(''))
    if len(raw_input_html_eles) > 0:
        filter_df = page_df[page_df['page_url'] == url]
        data_frame_list = filter_df.values.tolist()
        while len(raw_input_html_eles) :
            print('remaining iterations is ', len(raw_input_html_eles))
            i = raw_input_html_eles.pop(0)
            if i.is_displayed():
                atrs = scraping.get_all_elm_attrs(driver, i)
                atrs1 = str(atrs)
                elm_xpath = scraping.get_locator(driver, i)
                filter_attrs = page_df[(page_df['element_attributes'] == atrs1) & (page_df['element_xpath'] == elm_xpath)]
                list_attrs = [[driver.current_url, elm_xpath, i.tag_name, atrs1, None]]
                if not filter_attrs.empty or list_attrs in data_frame_list:
                    print('has same attributes type ,', filter_attrs.shape)
                    demo_df = filter_df.loc[(filter_df['element_attributes'] == atrs1) & (filter_df['element_xpath'] == elm_xpath)]  # returns a dataframe
                    print('after filter details in for loop \n', demo_df.shape, demo_df)
                else:
                    print(' the selected attribute {} is not found in the data set. hence adding a new row')
                    demo_df = pd.DataFrame(list_attrs, columns=['page_url', 'element_xpath', 'tagname', 'element_attributes', 'matching_label'])
                    page_df = page_df.append(demo_df, ignore_index=True).reset_index()
                    page_df = page_df.iloc[:, 1:]
            else:
                print(i.get_attribute('outerHTML'))
                continue
        print('dataframe shape after processing form elms : ', page_df.shape)
        SCRAP_DATA_FRAME = SCRAP_DATA_FRAME.append(page_df, ignore_index=True)
        print('*********************============************************* : ', SCRAP_DATA_FRAME.shape)


def write_prop_file(data_frame, base_url):
    """
    Method to write input elements to file which are present in dataframe
    """
    url_ = ''.join(i for i in base_url if i.isalnum())
    print(url_)
    url_path_ = 'D:\\props\\' + url_ + '.xlsx'
    writer = pd.ExcelWriter(url_path_, engine='xlsxwriter', options={'strings_to_urls': False})
    data_frame.to_excel(writer)
    writer.close()
    print('check if data written')


start_time_ = time.time()
with ThreadPoolExecutor() as executor_:
    scraper_ids_ = [_ for _ in range(NUM_SCRAPERS_)]
    scraper_base_urls_ = [BASE_URL_ for _ in range(NUM_SCRAPERS_)]
    for scraper_index_, scraper_final_status_ in zip(scraper_ids_, executor_.map(scraper_, scraper_ids_, scraper_base_urls_)):
        print('scraper_index_: ', scraper_index_)
        print('scraper_final_status_: ', scraper_final_status_)
write_prop_file(SCRAP_DATA_FRAME, BASE_URL_)
end_time_ = time.time()
print("{} seconds consumed for {} titles using recursive-multithreaded access".format(end_time_ - start_time_, urls_already_scraped_.qsize()))
