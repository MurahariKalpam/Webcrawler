import os , math, random, time
import pandas as pd

from random import choice
from string import ascii_letters
from selenium import webdriver
from collections import OrderedDict
from selenium.webdriver.support.ui import Select
from crawl_new_classifier.logg import ManualLogger

#input - testurl | #output - dataframe (existing / empty)

def read_prop_file(url,logger):
    '''
    check if the properties file of the element exists (already visited domain) or a new domain check
    '''
    url_ = ''.join(i for i in url if i.isalnum())
    print(url_)
    url_path_ = 'D://props//' + url_ + '.xlsx'
    if os.path.exists(url_path_):
        logger.write_log_data("Property file already exists for this domain")
        df = pd.read_excel(url_path_)
    else:
        logger.write_log_data("New domain visited. Hence creating a new property file")
        cols = ['page_url','element_xpath','tagname','element_attributes','matching_label'] 
        #page_url | webelement_pos (co-ordinates) |web_elm_distance from the page origin | elm_tag_name | webelement_attrs (dictionary datatype)
        df = pd.DataFrame(columns = cols)
    return df

def write_prop_file(data_frame, base_url):
    url_ = ''.join(i for i in base_url if i.isalnum())
    print(url_)
    url_path_ = 'D://props//' + url_ + '.xlsx'
    data_frame.to_excel(url_path_)
    print('check if data written')
    
#input - url, df | output - df (frame of elements present on that page
def get_page_attrs(url,df):

    if url in df.values()[0]:
        print('page history exists')
        dummy_df = df[df[0] == url]
        return dummy_df, True
    else:
        print('no page history.')
    return df, False

#input - driver, selenium webelm | output - dictionary containing element attributes as contained in the HTML DOM
def get_all_elm_attrs(driver, elm):
    '''
    returns a dictionary object of all the attributes from the DOM structure for a particular web element
    '''
    elm_dict = (driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',elm))
    elm_dict = (dict((k.lower(),v.lower()) for k,v in elm_dict.items()))
    print('return type of elm attributes',type(elm_dict))
    return elm_dict

#input - existing elm_attr , new_elm_attr | output - boolean
def check_attrs(eelm, nelm):
    '''
    checks if the current element attribute is the same as that from the excel
    '''
    if eelm == nelm:
        return True
    return False

def get_locator(driver, elm):
    # returns the xpath of the element for the future use
    element_xpath = driver.execute_script("""gPt=function(c){
                                if(c.id!==''){
                                    return'//*[@id="'+c.id+'"]'
                                } 
                                if(c===document.body){
                                    return c.tagName
                                }
                                var a=0;
                                var e=c.parentNode.childNodes;
                                for(var b=0;b<e.length;b++){
                                    var d=e[b];
                                    if(d===c){
                                        return gPt(c.parentNode)+'/'+c.tagName+'['+(a+1)+']'
                                    }
                                    if(d.nodeType===1&&d.tagName===c.tagName){
                                        a++
                                    }
                                }
                            };
                            return gPt(arguments[0]);""", elm)
    return element_xpath

def save_data(driver, elm, ipval, data_store, logger):
    print('inside save data')
    xpath = get_locator(driver, elm)
    action = 'Enter ' + ipval + ' to element ' + str(xpath) 
    print(action)
    data_store[xpath] = action
    logger.write_log_data(action)
    return data_store

def find_parent(driver,elm,elmtype):
    print('finding parents')
    # returns the possible options under a particular div class or a fieldset
    options_len = {'radio':2}
    print(elmtype)
    if elmtype in options_len.keys():
        min_opt_len = options_len[elmtype]
    print(min_opt_len)
    print(elm.get_attribute('outerHTML'))
    td_p_input = elm.find_element_by_xpath('..')
    print(td_p_input.get_attribute('outerHTML'))
#     parent_xpath=get_locator(d,td_p_input)
    options = [elm for elm in  td_p_input.find_elements_by_tag_name("input") if elm.get_attribute('type') != 'hidden' and elm.get_attribute('type') == elmtype]
    if len(options) >= min_opt_len:
        print(options)
        return options
    else:
        return find_parent(driver, td_p_input, elmtype)

def radio_elm(driver, elm, welms, data_store, logger):
    print('radio elms')
    try:
        options = find_parent(driver, elm, elm.get_attribute('type'))
        print('len of options for the radio elements are ', len(options)) 
        for i in options:
            if i in welms:
                print(i.get_attribute('outerHTML'))
                welms.remove(i)
        option = choice(options)
        print('selected option' + option.get_attribute('outerHTML'))
        data_store = save_data(driver, elm, option.get_attribute('id'), data_store, logger)
        print(option.get_attribute('outerHTML'))
        option.click()
        print('option is clicked')
        print('selected option' + option.get_attribute('value'))
        return 'radio',data_store, welms
    except Exception as e:
        print('Unknown radio button exception occurred')
        print(e)
        return 'radio',data_store, welms

def checkbox_elm(driver, elm, welms, data_store, logger):
    print('checkboxes')
    try:
        option = choice([True, False])
        if option : 
            elm.click()
            print('selected checkbox option is ' + str(option.get_attribute('innerHTML')))
            data_store = save_data(driver, elm, option, data_store, logger)
        return 'checkbox',data_store
    except Exception as e:
        print('Unknown checkbox exception occurred')
        print(e)
        return 'checkbox',data_store

def select_elm(driver, elm, data_store, logger):
    print('drop downs')
    try:
        select = Select(driver.find_element_by_xpath(get_locator(driver, elm)))
        options1 = [o.text for o in select.options]
        options = options1[1:]
        if elm.get_attribute('value') == options1[0]:
            option = random.choice(options)
            select.select_by_visible_text(option)
            print('element selected is ' + option)
            data_store = save_data(driver, elm, option, data_store, logger)
    except Exception as e:
        print('Drop down cannot be located')
        print(e)
    return 'select',data_store

def textarea_elm(driver, elm, data_store, logger):
    print('textarea')
    try:
        text = ''.join(choice(ascii_letters) for i in range(random.randint(10, 500)))
        elm.send_keys(text) 
        data_store = save_data(driver, elm, text, data_store, logger)
        print(text)
    except Exception as e:
        print('Unknown exception occurred in textarea')
        print(e)
#         return None
    return 'textarea',data_store

def submit_btns(driver, elm, url, data_store, logger):
    print('submit buttons')
    try:
        xpath = get_locator(driver, elm)
        name = driver.find_element_by_xpath(xpath).text
        val = 'click on ' + str(name)
        data_store[xpath] = val
        logger.write_log_data(val)
        elm.click()
    except Exception as e:
        print('Error occurred while submitting a form')
        print(e)
    return str(name),data_store

#matches data with the input dataset and the attribute property - input - dom_attributes , dataset | output - input text
def match_data(priority_list, attr_list, data_set):
    print('inside match data')
    attr_list_copy = attr_list
    for selector in priority_list: #iterating based on the priority of the attributes to map the right value
        if selector in attr_list.keys():
            prop_value = str(attr_list[selector])
            del attr_list[selector]
            for index,value in enumerate(data_set[0]):
                if str(value) in  prop_value:
                    print(data_set[1][index])
                    return prop_value,data_set[1][index]
    if len(attr_list): #iterating through the rest of the element properties
        print('length of the remaining properties ',len(attr_list))
        for value in attr_list.values():
            for index,label in enumerate(data_set[0]):
                if str(label) in str(value):
                    print(data_set[1][index])
                    return value,data_set[1][index]
    #if the matching labels aren't there in the data set
    print('No data present in the dataset')
    text = ''.join(choice(ascii_letters) for _ in range(random.randint(2, 4)))
    print(text)
    return 'Random',text

# input - driver, elm , elm_attribute_dict, data_set, data_store, log object | output - data-store, errors
def process_elm(driver, priority_list, elm_list,  elm, attr_list, data_set, data_store, logger):
    print('inside process element')
    elm_tag_name = elm.tag_name
    if elm_tag_name in ['input','textarea']:
        if attr_list['type'] in ['text','password','email','number']:
            elm_label,ip_text = match_data(priority_list, attr_list, data_set)
            elm.send_keys(ip_text)
            data_store = save_data(driver, elm, ip_text, data_store, logger)
        elif attr_list['type'] == 'submit' :
            elm_label,data_store = submit_btns(driver, elm, driver.current_url, data_store, logger)
        elif attr_list['type'] == 'radio' :
            elm_label,data_store, elm_list = radio_elm(driver, elm, elm_list, data_store, logger)
        elif attr_list['type'] == 'checkbox':
            elm_label,data_store = checkbox_elm(driver, elm, data_store, logger)
    elif elm_tag_name == 'button' : 
        elm_label,data_store = submit_btns(driver, elm, driver.current_url, data_store, logger)
    elif elm_tag_name == 'select':
        elm_label,data_store = select_elm(driver, elm, data_store, logger)
    return elm_label,data_store, elm_list
    
#input - selected form element | output - list of elements in the form
def find_elements(form_elm):
    print('inside find_elements')
    tagnames = ['input','select','textarea','button']  # possible input options on a web-page 
    elms = list()
    for i in tagnames:
        temp = [elm for elm in form_elm.find_elements_by_tag_name(i) if elm.get_attribute("type") not in [ 'hidden','file','search'] ]
        if temp != []:
            elms.extend(temp)
        else:
            continue
    return elms
#input - full dataframe , dataset | output - result
def filter_details (driver, url, form_elm, data_frame, data_set, logger):
#     labels = zip(data_set[data_set.columns[0]],data_set[data_set.columns[1]])
    #base_priority_list - first the programs look into this list. 
    #if the none of these attributes are present as a part of the element, then the rest of the attributes are considered to move ahead.
    priority_list = ['type','id','class','name','placehlder','alt']
    print('inside filter details')
    data_store = dict()
    labels = data_set[data_set.columns[0]].values.tolist()
    values = data_set[data_set.columns[1]].values.tolist()
    data_set_ = [labels , values]
    filter_df = data_frame[data_frame['page_url']== url]
    if not filter_df.empty :
        print("Page already visited")
        elm_sttr_list = filter_df['element_attributes'].values.tolist()
    else:
        print("New page visited")
        elm_sttr_list = list()
    elms = find_elements(form_elm)    
    print('dataframe shape before processing form elms : ',data_frame.shape,type(filter_df))
    data_frame_list = filter_df.values.tolist()
    print('filtered data frame list is',data_frame_list)
    print('number of elements',len(elms))
    while len(elms) :
        print('remaining iterations is ',len(elms))
        i = elms.pop(0)
        if i.is_displayed():
            atrs = get_all_elm_attrs(driver, i)
            atrs1 = str(atrs)
            elm_xpath = get_locator(driver, i)
            filter_attrs = filter_df[(filter_df['element_attributes'] == atrs1) & (filter_df['element_xpath'] == elm_xpath)]
            list_attrs = [[driver.current_url,elm_xpath,i.tag_name,atrs1,None]]
            if not filter_attrs.empty or list_attrs in data_frame_list:
                print('has same attributes type ,',filter_attrs.shape)
                demo_df = filter_df.loc[(filter_df['element_attributes'] ==  atrs1) & (filter_df['element_xpath'] == elm_xpath)] # returns a dataframe
                ind = demo_df.index.values.tolist() #check this
                print('after filter details in for loop \n', demo_df.shape, demo_df)
            else:
                print(' the selected attribute {} is not found in the data set. hence adding a new row')
                demo_df = pd.DataFrame(list_attrs,columns=['page_url','element_xpath','tagname','element_attributes','matching_label'])
                data_frame = data_frame.append(demo_df,ignore_index = True).reset_index()
                data_frame = data_frame.iloc[:,1:]
            #elm_label,data_store, elms = process_elm(driver,priority_list, elms, i, atrs, data_set_, data_store, logger)
            #logger.write_log_data('element label is {}'.format(elm_label))
            #print('len of elms after each iteration :',len(elms))
        else:
            print(i.get_attribute('outerHTML'))
            continue
    print('dataframe shape after processing form elms : ',data_frame.shape)
    print(data_store)
    write_prop_file(data_frame, logger.url)
    logger.write_log_data(str(data_store))
    od = OrderedDict(data_store)
    elm = od.popitem()
    return [driver.current_url, elm[1], elm[0], driver.title, 50]
    
#===============================================================================
#url = 'https://www.mightymatcha.com/contact/'
#logger = ManualLogger(url,550)
#data_store = dict()
#data_frame = read_prop_file(url, logger)
#data_set = pd.read_excel('D:\\props\\DataSet.xlsx')
#data_set = data_set.apply(lambda x: x.astype(str).str.lower())
#driver = webdriver.Chrome(executable_path = "D:\\IVSSOLH\\Deep_Assurance\\pythoncode\\Crawler\\chromedriver.exe")
#driver.get(url)
#frm = driver.find_elements_by_tag_name('form')
#f1 = [i for i in frm if i.get_attribute('action')!= 'search']
#frm1 = choice(f1)
#print(frm1.get_attribute('action'))
#print(filter_details(driver, url, frm1, data_frame, data_set, logger))
# retur type is -- return [driver.current_url, elm[1], elm[0], driver.title, len()]
#logger.write_log_data()
#print('finish')
#===============================================================================
