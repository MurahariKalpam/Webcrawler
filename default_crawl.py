from concurrent.futures.thread import ThreadPoolExecutor
import queue, time, glob, os, pandas as pd, tensorflow as tf, re, tldextract
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

from crawl_new_classifier import forms_latest as scraping
from crawl_new_classifier.logg import ManualLogger
from crawl_new_classifier.predictor import Predictor
from crawl_new_classifier.properties import DAProperties
from crawl_new_classifier import interactive_elements_grouping as grouping

from keras import models as model

def scraper_(id_, base_url_, smodel, tgraph, logger):
    # To flatten the url to filter out the special chars
    def flatten_(url_):
        return "".join(x for x in url_ if x.isalnum()) + ".txt"
    
    display_ = False
    # Put the base url into the queue first
    urls_yet_to_be_scraped_.put(base_url_)
    try:
        print('scrapper id  is : {}'.format(id_))
        # Start the chrome browser 
        driver = webdriver.Chrome(executable_path=DAProperties.CHROME_DRIVER.value)
        # Load the base url
        driver.get(url=base_url_)
        # Enforcing signin on each driver instance
        if signin_xpath == "":
            print(signin_xpath)
            print('first signin done')
            _ , driver = check_default_signin(driver, base_url_, signin_xpath)
        else:
            print(signin_xpath)
            elm = driver.find_element_by_xpath(signin_xpath)
            if elm:
                print('//has logged out. hence signing in again')
                _, driver = check_default_signin(driver, base_url_, signin_xpath)
        try:
            num_iterations_ = 0
            while True:
                try:
                    #Return the url from top of the queue and remove it from the queue
                    url_ = urls_yet_to_be_scraped_.get_nowait()
                    running_scrapers_.put_nowait(1)
                    display_ = True
                    print("scraper_ :: {} :: 1 :: {}".format(id_, url_))
                    
                    #Flatten url
                    modified_url = flatten_(url_)
                    # check if a file exist already in the current directory                                    
                    if modified_url not in glob.glob(modified_url):
                        try:
                            print("scraper_ :: {} :: 2 :: {}".format(id_, url_))
                            tag = ''
                            # Load the url
                            
                            driver.get(url_)
                            cocitation_status = validate_page_revisit(url_, driver)
                            if not cocitation_status : continue
                            links_in_page = list()
                            
                            # Adding timeout period to makesure the webpage load totally before we do scraping.
                            WebDriverWait(driver, 5)
                            curr_domain = tldextract.extract(driver.current_url).domain
                            # classify current webpage
#                             if str(driver.current_url).startswith(BASE_URL_): 
                            if curr_domain == WEB_DOMAIN: 
                                classify = Predictor(driver, smodel, tgraph)
                                classifier(url_, classify)
                            
                            #Get the all href links from the current webpage                
                            links_partial = driver.find_elements_by_partial_link_text('')
                            if links_partial:
                                for i in links_partial:
                                    test_url = i.get_attribute('href')
                                    if i is not None and test_url \
                                    and tldextract.extract(test_url).domain == WEB_DOMAIN \
                                    and test_url not in URL_TRACKER and test_url not in REPEATED_PAGES_:
#                                     and i.get_attribute('href').startswith(base_url_): # url should be start with base url. So that we will not end up landing in to out of the current website
                                        print("scraper_ :: {} :: 3a :: {}".format(id_, test_url))
                                        #Add the all founded links to list
                                        links_in_page.append(test_url)
                                    else:
                                        
                                        print("scraper_ :: {} :: 3b :: {}".format(id_, "#"))
                            
                            # Get the DIV elements            
                            for div_class in driver.find_elements_by_tag_name("div"):
                                tag += str(div_class.get_attribute("class") + " ")

                            # Writes the retrieved div elements data into the file  
                            with open(modified_url, 'w') as f:
                                print("file operations")
                                f.write(url_ + "\n" + tag)
                            
                            # Scrap input elements    
                            if str(driver.current_url).startswith(BASE_URL_): # To make sure we are in current website
                                scrap_input_elements(url_, driver, logger)
                                group_interactive_elms(driver)
                                
                            
                            # From all the retrieved href links from the current webpage check whether urls are already scraped (by checking whether flatten of url exist) and add it to the queue if not.
                            for new_url_ in links_in_page:  # get links
                                if not(glob.glob(flatten_(new_url_))):
                                    urls_yet_to_be_scraped_.put_nowait(new_url_)
                                    URL_TRACKER.append(new_url_)
                            
                            # add the  current url to scraped list       
                            urls_already_scraped_.put_nowait(url_)                            
                        except Exception as ex:
                            print("Error in scraping the webpage in default_crawl.scraper_ :" , ex)
                            driver.get(url_)
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

def validate_page_revisit(url_, driver):
    '''
    this method avoids the page revisit data with a different url loaded
    '''
    
    global PAGE_DATAFRAME_
    cols = ['URL','PAGE_SOURCES']
    if not PAGE_DATAFRAME_.empty:
        if url_ not in REPEATED_PAGES_:
            curr_page_src = driver.find_element_by_tag_name('body').text
            check_df = PAGE_DATAFRAME_.loc[PAGE_DATAFRAME_['PAGE_SOURCES'] == curr_page_src]
            if check_df.empty:
                dummy_df = pd.DataFrame([[url_,curr_page_src]],columns= cols)
                PAGE_DATAFRAME_ = PAGE_DATAFRAME_.append(dummy_df,ignore_index=True)
                return True # TRUE : fresh page
            else:
                print('repeated')
                REPEATED_PAGES_.append(url_)
                return False #False: co-citation
    else:
        curr_page_src = driver.find_element_by_tag_name('body').text
        dummy_df = pd.DataFrame([[url_,curr_page_src]],columns= cols)
        PAGE_DATAFRAME_ = PAGE_DATAFRAME_.append(dummy_df,ignore_index=True)
        return True
    #print(df.shape)

def scrap_input_elements(url, driver, logger):
    """
    Method to scrap all input elements of a html page.
    """
    global SCRAP_DATA_FRAME
    page_df = scraping.read_prop_file(url, logger)
    raw_input_html_eles = find_elements(driver)
    if len(raw_input_html_eles) > 0:
        filter_df = page_df[page_df['page_url'] == url]
        data_frame_list = filter_df.values.tolist()
        while len(raw_input_html_eles) :
#             print('remaining iterations is ', len(raw_input_html_eles))
            i = raw_input_html_eles.pop(0)
            if i.is_displayed():
                atrs = scraping.get_all_elm_attrs(driver, i)
                atrs1 = str(atrs)
                elm_xpath = scraping.get_locator(driver, i)
                filter_attrs = page_df[(page_df['element_attributes'] == atrs1) & (page_df['element_xpath'] == elm_xpath)]
                list_attrs = [[driver.current_url, elm_xpath, i.tag_name, atrs1, None]]
                if not filter_attrs.empty or list_attrs in data_frame_list:
#                     print('has same attributes type ,', filter_attrs.shape)
                    demo_df = filter_df.loc[(filter_df['element_attributes'] == atrs1) & (filter_df['element_xpath'] == elm_xpath)]  # returns a dataframe
#                     print('after filter details in for loop \n', demo_df.shape, demo_df)
                else:
#                     print(' the selected attribute {} is not found in the data set. hence adding a new row')
                    demo_df = pd.DataFrame(list_attrs, columns=['page_url', 'element_xpath', 'tagname', 'element_attributes', 'matching_label'])
                    page_df = page_df.append(demo_df, ignore_index=True).reset_index()
                    page_df = page_df.iloc[:, 1:]
            else:
                print('hidden element:',i.get_attribute('outerHTML'))
                continue
        print('dataframe shape after processing form elms : ', page_df.shape)
        SCRAP_DATA_FRAME = SCRAP_DATA_FRAME.append(page_df, ignore_index=True)
#         formelm = check_forms(driver,url)
#         if formelm == "NOForms": return
#         else:
#             form_values = scraping.get_form_elms(driver, url, logger, formelm)
#             logger.write_log_data(str(form_values))

# def check_forms(driver, url):   
#     formElements=driver.find_elements_by_tag_name("form")
#     if formElements:
#         print('Number of form elements found on this page is {}'.format(len(formElements)))
#         return formElements
#     else:
#         print('No elements in check_forms')
#         return "NOForms"

def write_to_prop_file(data_frame, base_url, remove_dupilates):
    """
    Method to write input elements to excel file from dataframe
    """
    try:
        url_ = ''.join(i for i in base_url if i.isalnum())
        url_path_ = DAProperties.INPUT_ELEMENTS_FILE_DIRECTORY.value + url_ + '.xlsx'
        #engine and options are used here to make sure no dataloss/error while writing the long line into a file
        writer = pd.ExcelWriter(url_path_, engine='xlsxwriter', options={'strings_to_urls': False})
        #Remove duplicates if any
        if remove_dupilates & len(data_frame) > 0:
            data_frame.drop_duplicates(keep="first", inplace=True)
        data_frame.to_excel(writer)
        writer.close()
    except Exception as ex:
        print('Error in writing input elements into excel file in playground.write_to_prop_file', ex)

# input - selected form element | output - list of elements in the form
def find_elements(webdriver):
    """
    Method to scrap html elements
    """
    tagnames = ['input', 'select', 'textarea', 'button']  # possible input options on a web-page 
    elms = list()
    for i in tagnames:
        temp = [elm for elm in webdriver.find_elements_by_tag_name(i) if elm.get_attribute("type") not in [ 'hidden', 'file', 'search'] ]
        if temp != []:
            elms.extend(temp)
        else:
            continue
    return elms

def load_saved_model():
    """
    Method to load the existing model.
    Below are being used to handle the loaded model by multiple threads. Otherwise it gives the issue while predicting. 
    _make_predict_function
    get_default_graph
    
    """
    sgraph = list()
    try:
        smodel = [model.load_model(DAProperties.MODEL.value) for _ in range(NUM_SCRAPERS_)]
        for i in range(len(smodel)):
            smodel[i]._make_predict_function()
            sgraph.append(tf.get_default_graph())
        log_thread = list()
        urldata = ''.join(e for e in BASE_URL_ if e.isalnum())
        for scrap in range(NUM_SCRAPERS_):
            url = urldata + str(scrap)
            lobj = ManualLogger(url , 999)
            log_thread.append(lobj) #add trial number here
            
        return sgraph, smodel, log_thread
    except Exception as ex:
        print("Error in loading the model in playground.load_saved_model :", ex)

def dataframe_to_excel(dataframe, cols, url):
    """
    Method to write dataframe into excell
    """
    try:
        for i in dataframe:
            dataframe[i] = str(dataframe[i])
        df = pd.DataFrame.from_dict(dataframe, orient='index').reset_index()
        df.rename(columns={'index': cols[0], 0: cols[1]}, inplace=True)
        flatternurl = ''.join(i for i in url if i.isalnum())
        url_path_ = DAProperties.INPUT_ELEMENTS_FILE_DIRECTORY.value + flatternurl + '-CLASSIFICATION' + '.xlsx'
        writer = pd.ExcelWriter(url_path_, engine='xlsxwriter', options={'strings_to_urls': False})
        df.to_excel(writer)
        writer.close()
    except Exception as ex:
        print("Error in converting ", type(dataframe), "to Dataframe in method : dataframe_to_excel", ex) 
        
def remove_duplicates(data_frame):
    return data_frame.drop_duplicates(keep="first", inplace=True)


def classifier(url_, classify):
    """
    Method to call the Predictor.classifier to predict the categeory of given webpage 
    """
    if url_ not in classified_URLs:
        url_classification = classify.classifier()
        print(url_, ':', url_classification)
        classified_URLs[url_] = url_classification
    else:
        print('URL already classified')

def enter_values(driver, elm):
    inputs={ 0: "infosys@gmail.com", 1: "Infy1234*"}
    elminfo = ['type','id','name','placeholder','title','alt','value']
    mail = ['mail', 'user', 'logon', 'name', 'login', 'emailaddressshippingAddressForm', 'usename', 'emailAddress', 'emailaddress', 'confirmLogin']
    credentials = ['password']
    iporder=[mail,credentials]
    inputelms=[element for element in driver.find_elements_by_tag_name("input") if element.get_attribute("type") in ["text", "email" , "password", "submit"]]# and element.get_attribute("type")!="submit"]
    print('before adding buttons'+" "+str(len(inputelms)))
    inputelms.extend(ele for ele in driver.find_elements_by_tag_name("button") if ele.get_attribute("type")!="hidden")
    submitkeywords=["submit","signin","login","signinsubmit"]
    '''
     filter the input tags
    '''
    status_done = False
    combined_list = mail + credentials + submitkeywords
    filtered_list = list()
    for elm in inputelms:
        elm_attr = scraping.get_all_elm_attrs(driver, elm)
        for attr in elm_attr.values():
            for celm in combined_list :
                attr = attr.replace(' ','').lower()
                flatten_attr = "".join(x for x in attr if x.isalpha())
                if celm in flatten_attr and elm.is_displayed():
                    filtered_list.append(elm)
                    print(elm.get_attribute('outerHTML'))
                    status_done = True
                    break
            if status_done: break
    print('filtered_elm list us ',len(filtered_list))
    submit_status = False
    for interactive_elm in filtered_list:
        done = False
        try:
            if interactive_elm.is_displayed():
                print(interactive_elm.get_attribute("outerHTML"))
                for infotype in elminfo: #elm info has the classes against which the values of the program and tags are matched
                    print("Infotype is {} and {}".format(infotype,interactive_elm.get_attribute(infotype)))
                    for key in iporder: #iporder is the list which contains the order of the keys to the dictionary which contains the values
#                         print('key in input list is {}'.format(key))
                        for eachkey in key: #key is a list containing the bad of possible labels for each input section
                            print(eachkey)
                            if re.search(".*" + eachkey + ".*" , interactive_elm.get_attribute(infotype).lower()) is not None:
                                print("individual key in input list is {} and value is {} ".format(eachkey,interactive_elm.get_attribute(infotype).lower()))
                                key1=iporder.index(key)
                                print(inputs.get(key1))
                                interactive_elm.send_keys(inputs.get(key1))
                                done = True
                                break
                            elif re.match(".*submit.*", interactive_elm.get_attribute(infotype).lower().replace(" ", "")) is not None:# or re.match(".*button.*",elm.get_attribute(infotype).lower().replace(" ","")) is not None :
                                print(1111)
                                interactive_elm.click()
                                done= True
                                submit_status = True
                                break 
                        if done : 
                            break      
                    if done : 
                        break
            else: break   
        except StaleElementReferenceException as _:
            pass   
        except Exception as _ :
            return False
    return submit_status

def check_default_signin(driver, url_, signin_xpath):
    print(1)
    signin_list_ = ['signin','login', 'logon']
#     driver.get(url_)
    if signin_xpath  == "":
        print('empty string')
        elm = driver.find_element_by_tag_name("body") #body of the webpage
        child_elms = elm.find_elements_by_xpath(".//*") #all the child elements within the body tag
        elm_flag, done = False, False
        
        try:
            for base_elm in child_elms:
                if base_elm.tag_name in ['a','button']:
                    print(1)
                    elm_attr_list = scraping.get_all_elm_attrs(driver, base_elm)
                    for attr in elm_attr_list.values():
                        attr = attr.replace(' ','')
                        flatten_attr = "".join(x for x in attr if x.isalpha())
                        for signin_elm in signin_list_:
                            if signin_elm in flatten_attr:
                                print(11)
                                if base_elm.is_displayed():
                                    print('a')
                                    signin_xpath = scraping.get_locator(driver, base_elm)
                                    print(signin_xpath)
                                    base_elm.click()
                                    print('ELement clicked')
                                    status_ = enter_values(driver, base_elm)
                                    if status_:
                                        print('login successful')
                                        elm_flag = True
                                        done= True
                                        break
                                elif base_elm.tag_name == 'a':
                                    print('q')
                                    driver.get(base_elm.get_attribute("href"))
                                    done= True
                        if done: break
                    if done: break
                else: continue
            if elm_flag or signin_xpath != "":
                print('Page has signin')
            else:
                print('page has no signin')
        except StaleElementReferenceException as _:
            print(_)
            
    #     signed_url = driver.current_url 
        return elm_flag, driver
    
    else:
        print('signin path captured already')
        driver.find_element_by_xpath(signin_xpath).click()
        print('ELement clicked')
        status_ = enter_values(driver, base_elm)
        if status_:
            print('login successful')
            elm_flag = True
        return elm_flag, driver
    

def createDirectoryWithURL():
    """
    Method to create a directory with the name of the url passed
    """
    try:
#         urldata = ''.join(e for e in base_url_ if e.isalnum())
#         dirpath = DAProperties.OUTPUT_FOLDER_FOR_CRAWL_DIV_ELEMENTS.value + urldata + '\\'
        dirpath = DAProperties.OUTPUT_FOLDER_FOR_CRAWL_DIV_ELEMENTS.value + WEB_DOMAIN + '\\'
        os.mkdir(dirpath)
        print(dirpath)
        os.chdir(dirpath)
    except Exception as ex:
        print("Error in creating and setting current directory in playground.createDirectoryWithURL", ex)
        
def group_interactive_elms(driver):
    global GROUPING_ELMS
    grouped_elements = grouping.grouping_main(driver)
    df = pd.DataFrame.from_dict(grouped_elements, orient='index').reset_index()
    GROUPING_ELMS = GROUPING_ELMS.append(df, ignore_index=True)

def export_grouping_to_file(df, url):
    try:
        cols = ['Group', 'url', 'Elements', 'Xpath']
        #url = driver.current_url
        #df = pd.DataFrame.from_dict(dataframe, orient='index').reset_index()
        df.rename(columns={'index': cols[0], 0: cols[1], 1: cols[2], 2: cols[3]}, inplace=True)
        flatternurl = ''.join(i for i in url if i.isalnum())
        url_path_ = DAProperties.INPUT_ELEMENTS_FILE_DIRECTORY.value + flatternurl + '-GROUPING_ELEMENTS' + '.xlsx'
        writer = pd.ExcelWriter(url_path_, engine='xlsxwriter', options={'strings_to_urls': False})
        df.to_excel(writer)
        writer.close()
    except Exception as ex:
        print(ex)
    
def init(base_url, no_of_scrapers):
    """
    Method to initialize variables and to make them global to make sure the values exist throught. 
    """
    print(base_url)
    global SCRAP_DATA_FRAME
    global urls_yet_to_be_scraped_
    global urls_already_scraped_
    global classified_URLs
    global running_scrapers_
    global BASE_URL_
    global WEB_DOMAIN
    global NUM_SCRAPERS_
    global signin_xpath
    global PAGE_DATAFRAME_
    global URL_TRACKER
    global REPEATED_PAGES_
    global GROUPING_ELMS
    SCRAP_DATA_FRAME = pd.DataFrame()
    PAGE_DATAFRAME_ = pd.DataFrame()
    GROUPING_ELMS = pd.DataFrame()
    urls_yet_to_be_scraped_ = queue.Queue()
    urls_already_scraped_ = queue.Queue()
    running_scrapers_ = queue.Queue()
    classified_URLs = dict()
    BASE_URL_ = base_url
    WEB_DOMAIN = tldextract.extract(base_url).domain
    NUM_SCRAPERS_ = no_of_scrapers
    signin_xpath = ""
    createDirectoryWithURL()
    URL_TRACKER = list()
    REPEATED_PAGES_ = list()
    
def main(base_url, no_of_scrapers = DAProperties.DEFAULT_NO_OF_THREADS_FOR_CRAWLING.value):
    """
    This is the main method which needs to be called to start web crawling.
    
    parameters : 1. base url of the website which needs to be crawled.
                 2 (optional). Number of threads to do the crawling asynchronously
    """
    init(base_url , no_of_scrapers)
    start_time_ = time.time()
    with ThreadPoolExecutor() as executor_:
        scraper_ids_ = [_ for _ in range(NUM_SCRAPERS_)]
        scraper_base_urls_ = [BASE_URL_ for _ in range(NUM_SCRAPERS_)]
        tgraph, smodel, logger = load_saved_model()
        for scraper_index_, scraper_final_status_ in zip(scraper_ids_, executor_.map(scraper_, scraper_ids_, scraper_base_urls_, smodel, tgraph, logger)):
            print('scraper_index_: ', scraper_index_)
            print('scraper_final_status_: ', scraper_final_status_)
    write_to_prop_file(SCRAP_DATA_FRAME, BASE_URL_, True)
    export_grouping_to_file(GROUPING_ELMS, BASE_URL_)
    dataframe_to_excel(classified_URLs, ["WebpageURL", "Categeory"], BASE_URL_)
    logger[0].write_log_data(str(REPEATED_PAGES_))
    end_time_ = time.time()
    print("{} seconds consumed for {} titles using recursive-multithreaded access".format(end_time_ - start_time_, urls_already_scraped_.qsize()))
    
main('https://www.petstore.com/')
