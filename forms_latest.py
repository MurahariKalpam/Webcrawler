import crawl_new_classifier.py_m_connect as db_handler
import os , random, time, re , string
import pandas as pd

from random import choice
from string import ascii_letters

from collections import OrderedDict
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException

from bs4 import BeautifulSoup
from crawl_new_classifier import Form_Interactive_Elems_Scrap
from crawl_new_classifier.Form_Interactive_Elems_Scrap import Xpath_Util as xpathscrap
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
#     print('return type of elm attributes',type(elm_dict))
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
        #return 'checkbox',data_store
        return data_store
    except Exception as e:
        print('Unknown checkbox exception occurred')
        print(e)
        #return 'checkbox',data_store
        return data_store

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
        text = ''.join(choice(ascii_letters) for _ in range(random.randint(10, 500)))
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
    #attr_list_copy = attr_list
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
#===============================================================================
# def filter_details (driver, url, form_elm, data_frame, data_set, logger):
# #     labels = zip(data_set[data_set.columns[0]],data_set[data_set.columns[1]])
#     #base_priority_list - first the programs look into this list. 
#     #if the none of these attributes are present as a part of the element, then the rest of the attributes are considered to move ahead.
#     priority_list = ['type','id','class','name','placehlder','alt']
#     print('inside filter details')
#     data_store = dict()
#     labels = data_set[data_set.columns[0]].values.tolist()
#     values = data_set[data_set.columns[1]].values.tolist()
#     data_set_ = [labels , values]
#     filter_df = data_frame[data_frame['page_url']== url]
#     if not filter_df.empty :
#         print("Page already visited")
#         elm_sttr_list = filter_df['element_attributes'].values.tolist()
#     else:
#         print("New page visited")
#         elm_sttr_list = list()
#     elms = find_elements(form_elm)    
#     print('dataframe shape before processing form elms : ',data_frame.shape,type(filter_df))
#     data_frame_list = filter_df.values.tolist()
#     print('filtered data frame list is',data_frame_list)
#     print('number of elements',len(elms))
#     while len(elms) :
#         print('remaining iterations is ',len(elms))
#         i = elms.pop(0)
#         if i.is_displayed():
#             atrs = get_all_elm_attrs(driver, i)
#             atrs1 = str(atrs)
#             elm_xpath = get_locator(driver, i)
#             filter_attrs = filter_df[(filter_df['element_attributes'] == atrs1) & (filter_df['element_xpath'] == elm_xpath)]
#             list_attrs = [[driver.current_url,elm_xpath,i.tag_name,atrs1,None]]
#             if not filter_attrs.empty or list_attrs in data_frame_list:
#                 print('has same attributes type ,',filter_attrs.shape)
#                 demo_df = filter_df.loc[(filter_df['element_attributes'] ==  atrs1) & (filter_df['element_xpath'] == elm_xpath)] # returns a dataframe
#                 ind = demo_df.index.values.tolist() #check this
#                 print('after filter details in for loop \n', demo_df.shape, demo_df)
#             else:
#                 print(' the selected attribute {} is not found in the data set. hence adding a new row')
#                 demo_df = pd.DataFrame(list_attrs,columns=['page_url','element_xpath','tagname','element_attributes','matching_label'])
#                 data_frame = data_frame.append(demo_df,ignore_index = True).reset_index()
#                 data_frame = data_frame.iloc[:,1:]
#             elm_label,data_store, elms = process_elm(driver,priority_list, elms, i, atrs, data_set_, data_store, logger)
#             logger.write_log_data('element label is {}'.format(elm_label))
#             print('len of elms after each iteration :',len(elms))
#         else:
#             print(i.get_attribute('outerHTML'))
#             continue
#     print('dataframe shape after processing form elms : ',data_frame.shape)
#     print(data_store)
#     write_prop_file(data_frame, logger.url)
#     logger.write_log_data(str(data_store))
#     od = OrderedDict(data_store)
#     elm = od.popitem()
#     return [driver.current_url, elm[1], elm[0], driver.title, 50]
# 
# 
# #===============================================================================
# # url = 'https://www.myntra.com/register?referer=https://www.myntra.com/login'
# # logger = ManualLogger(url,550)
# # data_store = dict()
# # data_frame = read_prop_file(url)
# # data_set = pd.read_excel('D://props//DataSet.xlsx')
# # data_set = data_set.apply(lambda x: x.astype(str).str.lower())
# # driver = webdriver.Chrome(executable_path = "D:\\ChromeDriver\\chromedriver.exe")
# # driver.get(url)
# # frm = driver.find_elements_by_tag_name('form')
# # f1 = [i for i in frm if i.get_attribute('action')!= 'search']
# # frm1 = choice(f1)
# # print(frm1.get_attribute('action'))
# # print(filter_details(driver, url, frm1, data_frame, data_set, logger))
# # # retur type is -- return [driver.current_url, elm[1], elm[0], driver.title, len()]
# # logger.write_log_data()
# # print('finish')
# #===============================================================================
#===============================================================================


#===============================================================================
# Importing required packages

# from string import ascii_letters,ascii_uppercase
#===============================================================================


#data_dict = {0: "infosys@gmail.com", 1: "Infy1234*", 2: "Infosys", 3:"Solution", 4: "7800 Smith Rd", 5: "Denver", 6: "CO - Colorado", 7: "80022", 8: "3035612794", 9: "567", 10: "Standard", 11: "5555555555554444" , 12: "Mastercard", 13: "xyz", 14: "07", 15: "21", 16: "656", 17: "01", 18:"01"} 
data_dict = {0: "infosys@gmail.com", 1: "Infy1234*", 2: "Infosys", 3:"Solution", 4: "7800 Smith Rd", 5: "Denver", 6: "CO - Colorado", 7: "80022", 8: "3035612794", 9: "567", 10: "Standard", 11: "5555555555554444" , 12: "Mastercard", 13: "xyz", 14: "07", 15: "21", 16: "656", 17: "01", 18:"01"}
res = db_handler.get_data_for_test_field()
 
infotype = list()
for each in res[0]:
    try:
        infotype.extend(res[0])#listoflists
        each = ''.join(e for e in each)
#         attributes(0).append(each)
        infotype.append(each)
    except:
        pass 
 

iporder=[]
dict_attrib={}
len_res=len(res)
for index in range(0,len_res-1):
    list_temp=[]
    for each in res[index+1]:
        try:
            each = ''.join(e for e in each)
            list_temp.append(each)
        except:
            pass 
    dict_attrib[index]= list_temp

for keys in dict_attrib:
    iporder.append(dict_attrib[keys])
form_data = {}
#===============================================================================
#input - driver, selenium webelm | output - dictionary containing element attributes as contained in the HTML DOM
def Check_Autofill(driver,elm):
    print('inside check autofill fn')
    prop_flag=False
    afil=False
    elm_prop_val=''
    print(elm.get_attribute('outerHTML'))
    if elm.get_attribute('aria-owns')!=None:
        elm_prop_val=elm.get_attribute('aria-owns')
        prop_flag=True
    count=0
    print('prop flag is ',prop_flag)
    if not prop_flag:
        return ''
    while prop_flag and (not afil) and count < 3:
        print('inside while of auto complete')
        print('prop_flag is :',prop_flag)
        print('afil flag status : ',not(afil))
        print('counter status is : ',count)
        elm.clear()
        text=''.join(random.choice(string.ascii_uppercase) for _ in range(3))
        print(count,text)
        elm.send_keys(text)
        driver.implicitly_wait(4)
        afilelms=driver.find_element_by_id(elm_prop_val) 
#         print(afilelms)
        if afilelms:
            print('inside if')
            try:
                print('inside try of autocomplete')
                child_afil = afilelms.find_elements_by_css_selector("*")
                option=choice(child_afil)
                print(option.get_attribute('outerHTML'))
                option.click()
                afil=True
                value=elm.get_attribute('value')
                return value
            except Exception as e:
                print(e)
                return ''
        count+=1
     
    print('value returned out of while is ',elm.get_attribute('value'))
    return elm.get_attribute('value')


def text_elm(driver, elm, data_store,logger):
    print('text_elm')
    try:
        #if not elm.get_attribute('value'): #sumer: it doesn't undergo if condition if there is any text in the field
            
        flag = 0
        data=Check_Autofill(driver,elm)
#             data=''
        print('data returned from autofill is ',data)
        if data != '':
            print('inside autofill if')
            data_store=save_data(driver,elm,data,data_store,logger)
            return data_store
        else:
            print('else segment of autofill')
            #elm.clear()
            for info in infotype:
                print('info is ', info[0]) #sumer info to info[0] because info is tuple with one element
                val = elm.get_attribute(info[0]).lower() #sumer info to info[0] because info is tuple with one element
              
                print('value is ', val)
                                
                if val!='':
                    for pos, each in enumerate(iporder):
                        print('list that is referred is {}'.format(each))
                        for listelm in each:
                            print('each listelm referred within the main list is ',listelm)
                            try:
                                if re.search('.*' + listelm + '.*', val) is not None:
                                    print('inside form->testem->nested if ')
    #                                 pos=iporder.index(each)
                                    ipval = data_dict[pos]
                                    data_store = save_data(driver, elm, ipval, data_store,logger)
                                    #if elm.get_attribute("value") is '':
                                    elm.send_keys(ipval)
                                    flag = 1
                                    return data_store
                            except Exception as e:
                                print('data not available in data_dict')
                                print('Exception occurred is ', e)
                                
                                logger.write_log_data('data not available in data_dict')
                                continue
                
            # if a field is required and the database doesn't contain relevant data then input a random text to a field and continue
            if flag == 0 and re.search('required', elm.get_attribute('outerHTML')):
                print('inside form->testem->if2 is a required field ')
                text = ''.join(choice(string.ascii_letters) for _ in range(random.randint(2, 4)))
#                 ipval=data_dict[pos]
                data_store = save_data(driver, elm, text, data_store,logger)
                elm.send_keys(text)
                flag = 1
                return data_store
        #sumer    
        #=======================================================================
        # else:
        #     ipval = elm.get_attribute('value')
        #     data_store=save_data(driver,elm,ipval,data_store,logger)
        #     return data_store
        #=======================================================================
        #sumer
    except Exception as e:
        print('Unknown exception occurred in text field.',e)
#         print()
        return data_store

#===============================================================================


def record_errors(driver, url, error_store):
    print('record errors')
    error_list = ['invalid', 'incorrect', 'is required', 'incomplete', 'sorry', 'error', 're-enter', 'not valid', 'try again', 'check', 'not']  # bag of possible words to identify the error messages on that webpage
    # stores the url and the list of errors on that web page for that trial
    errors = []
    innerHTML = driver.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(innerHTML, "lxml")
    data = soup.findAll(text=True)

    def visible(element):
        if element.parent.name not in['span', 'p', 'div'] and element.parent.class_attribute not in [ 'visually-hidden' , 'item' ]:
            return False
        elif re.match('<!--.*-->', str(element.encode('utf-8'))):
            return False
        return True
    
    result = filter(visible, data)
    result = set(result) 
    for i in error_list:
        for j in result:
            if i in j.lower() and j not in errors:
                errors.append(j)
                print(j)
    error_store[url] = errors            
    return error_store

#===============================================================================

def check_out_button(driver,button,data_store,logger):
    count = 0
#     curr_url=driver.current_url
    val=button.get_attribute('innerHTML').strip()
    count+=1
    print(val)
    if button.is_displayed():
        elm=button.get_attribute('outerHTML')
        print('Selected button is :',val,'=',elm)
        try:
            button.click()
            #time.sleep(30)
            
            if re.search('.*Add To Bag*.', val) is not None:
                #self.driver.get("https://uat.ulta.com/bag/")
                link_checkout=driver.find_elements_by_partial_link_text("CHECKOUT")
                print(link_checkout)
                if link_checkout:
                    randomlink_checkout=random.choice(link_checkout)
                    if elm.get_attribute('innerHTML')!= None: #sumer name to elm
                        name1=elm.get_attribute('innerHTML') #sumer name to elm
                    else:
                        name1=elm.get_attribute('value') #sumer name to elm
                    ipval = 'click on '+name1
                    data_store = save_data(driver, elm, ipval, data_store, logger)
                    randomlink_checkout.click() 
                    return 'Clicked',data_store
                return 'None',data_store
        except Exception as err:
            print("error: ", err)
            print("error in clicking button..hence selecting other button")
            return 'None',data_store
#         if curr_url!=driver.current_url:
#             return []
    print("count: ",count)

'''
to generate random date between a specific interval
'''
#===============================================================================
def strTimeProp(start, end, frmt, prop):
    """Get a time at a proportion of a range of two formatted times.
    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """
    stime = time.mktime(time.strptime(start, frmt))
    etime = time.mktime(time.strptime(end, frmt))
    ptime = stime + prop * (etime - stime)
    return time.strftime(frmt, time.localtime(ptime))

#===============================================================================
def randomDate(start, end, prop):
#     return strTimeProp(start, end, '%m/%d/%Y %I:%M %p', prop)
    return strTimeProp(start, end, '%m/%d/%Y', prop)

#===============================================================================
'''
functions for reordering the elements starts here
'''
    
def format_html_soup(i):
#     print('inside formatting tags 2')
    i = i.prettify()  # to get the outer HTML code for a bs4 object
    form = i[i.index('<'):i.index('>')]
    return form

#===============================================================================


def format_tags(i):
#     print('formatting tags ')
    form = format_html_soup(i)
    form = sorted(list(set(form.split(' '))))
    form1 = []
    for i in form :
        if '/' in i:
            i = re.sub('/', '', i)
        form1.append(i)
    return form1

#===============================================================================


def get_input_order(driver, url):
    print('extracting the input order of webelements in progress...')
    input_tags_format = []
    input_tags_html = []
    src_code = driver.page_source
    soup = BeautifulSoup(src_code, 'lxml')
    trTag = soup.findAll(['input' , 'select', 'button', 'textarea', 'a'])  # trTag is of class bs4.webelement.Resultset
    for data  in trTag:
        data1 = data
        if data.has_attr('type'):
            if data['type'] not in [ 'hidden' , 'file']:  # filtering the hidden elements 
                data = format_tags(data)
                input_tags_format.append(data)
                input_tags_html.append(format_html_soup(data1))
            
        else:
            data = format_tags(data)
            input_tags_format.append(data)
            input_tags_html.append(format_html_soup(data1))
    print('while extracting length,below no of elements are obtained')      
    print(len(input_tags_format), len(input_tags_html))
    return input_tags_format, input_tags_html

#===============================================================================
def grp_elms(driver, frmelm, url):
    print('inside grp_elms')
    input_dict = dict()  # dictionary based on the type of inputs input_dict={ele_type(key) : list_of_elements(value)}
    #elm_dict = list()
    print(frmelm.get_attribute('action'))
    elms = [elm for elm in frmelm.find_elements_by_tag_name("input") if (elm.get_attribute("type") not in [ 'hidden','file'])]
    for elm in elms:
        try:
            elm_type = elm.get_attribute('type')
            if  elm_type in input_dict.keys():
                elm = [elm]
                temp = input_dict[elm_type]
                temp.extend(elm)
                input_dict[elm_type] = temp
            elif  elm_type not in input_dict.keys():
                elm = [elm]
                input_dict[elm_type] = elm
#             else:
#                 print(elm.get_attribute('outerHTML'))
        except Exception as e:
            print('exception encountered ' + str(e))
    print('len of elms initial before buttons etc' + str(len(elms)))
    tagnames = ['select', 'button', 'textarea' , 'a']  # possible input options on a web-page 
    for i in tagnames:
        print(i)
        temp = [elm for elm in frmelm.find_elements_by_tag_name(i) if elm.get_attribute("type") not in [ 'hidden' , 'file' ] ]
        if temp != []:
            input_dict[i] = temp
            elms.extend(temp)
            print(i, len(elms))
    print('len of elms final'+str(len(elms))) #sumer: just for print
    return elms    #change 05nov bindiya
    '''
    to get the links inside the form
    '''

'''
functions for re-ordering the elements ends here
'''
#=======================================================================
# To extract the form elements of the current web page

def get_form_elms(driver, url,logger, formelm):
    try:
        print('inside get_form_elms')
        logger.write_log_data(url)
        data_store = dict() #has the data entered for that form
        error_store = dict() # has the list of errors captured after the submission
        err_list = []
        #sumer
        print("all forms: ", formelm)#sumer
        form=random.choice(formelm)
        print("selected form: ", form)
        formelm.remove(form)
        a="check form"
        while a == "check form":
            els = [el for el in form.find_elements_by_tag_name("input") if (el.get_attribute("type") not in [ 'hidden','file'])]
            if len(els)==0:
                print("selected form has all input type as hidden or files..hence selecting another form if available")
                if formelm:
                    form=random.choice(formelm)
                    formelm.remove(form)
                    print("selected form: ", form)
                    a="check form"
                else:
                    return "No relevant form"
            else:
                a="continue"
            for el in form.find_elements_by_tag_name("input"):
                input_type=el.get_attribute("type").lower()
                input_id=el.get_attribute("id").lower()
                if(re.search('.*search.*', input_type) is not None) or (re.search('.*search.*', input_id) is not None and (input_type not in ['hidden'])):
                    continue
                    print("selected form performs search task..hence selecting another form")
                    if formelm:
                        form=random.choice(formelm)
                        formelm.remove(form)
                        a="check form"
                        break
                    else:
                        return "No relevant form"
        print("final selected form: ", form) #sumer
        #sumer
    
        if form is not None :
            print('selected form is not none')
#             selected_forms.append(formelm)
            print(form.get_attribute('action'))
#             global webelm_list
            
            xpath_obj = xpathscrap()
            page = driver.execute_script("return document.body.innerHTML").encode('utf-8') #returns the inner HTML as a string
            soup = BeautifulSoup(page, 'html.parser')
            if xpath_obj.generate_xpath(soup, driver) is False:
                print("No XPaths generated for the URL:%s"%url)
            
            webelm_list = grp_elms(driver, form, url)
            print('The number of inputs possible on this page is ' + str(len(webelm_list)))
            no_visible_counter = 0
            if len(webelm_list) != 0: 
                print('form has interactive elements',len(webelm_list))
                while webelm_list or len(webelm_list):
                    print('inside while for')
                    elm=webelm_list.pop(0)
                    try:
                        print('inside webelement try :iterations remaining : elem focused no',len(webelm_list) ,elm.get_attribute('outerHTML'))
                        #time.sleep(4)
                        if elm.is_displayed():
                            print('elm is displayed',elm.get_attribute('outerHTML'))
                            if elm.get_attribute('type') == 'radio':
                                data_store , webelm_list = radio_elm(driver, elm, webelm_list, data_store,logger)
                                continue
                            
                            elif elm.get_attribute('type') == 'checkbox':
                                #data_store , webelm_list = checkbox_elm(driver, elm, webelm_list, data_store,logger)
                                data_store = checkbox_elm(driver, elm, webelm_list, data_store,logger)
                                continue
                            
                            elif elm.tag_name == 'select': 
                                data_store = select_elm(driver, elm, data_store,logger)
                                continue
                            
                            elif elm.get_attribute('type') == 'textarea':
                                data_store = textarea_elm(driver, elm, data_store,logger)
                                continue
                            
                            elif elm.get_attribute('type') in ['text', 'password', 'email', 'tel']: #sumer 'email' added
                                data_store = text_elm(driver, elm, data_store,logger) 
                                continue      
                            
                            elif elm.tag_name == 'button' or elm.get_attribute("type") == 'submit':        
                                if elm.get_attribute('id')!= None  and elm.get_attribute('id').lower() != 'addvgmblock' :
                                    print('id is not none and not an add block')
                                    val = elm.get_attribute('innerHTML')
                                    if elm.get_attribute('type')!= None and elm.get_attribute('type') == 'submit' :#or re.search('*add*',val) is None :
                                        print('calling buttons') 
                                        status,data_store = check_out_button(driver,elm,data_store,logger)
                                        if status == 'Clicked':
                                            url_new = driver.current_url
                                            pass
                                        elif status == 'None':
                                            url_new, data_store = submit_btns(driver, elm, data_store,logger)
            #                                 if status:
                                            
                                        err_list = record_errors(driver, url, error_store)
                                        logger.write_log_data(err_list)
                                        print('random_url: ', url_new)
    #                                     if url_new is None:
    #                                         print(5)
    #                                         continue
                #                             return None,data_store,error_store
    #                                     if webelm_list.index(elm)==(len(webelm_list)-1):
                                        if isinstance(url_new, str) and url_new != url and len(webelm_list)==0:
                                            print('is instance')
                                            od=OrderedDict(data_store)
                                            elm=od.popitem()
                                            return [driver.current_url, elm[1], elm[0], driver.title,len(err_list.values())]
#                                     else: continue
                                else:
                                    print('8b')
                                    elm_text=elm.get_attribute('innerHTML')
                                    if elm_text!= None :
                                        elm_text = elm_text.lower()
                                        if elm_text.startswith('erase') or elm_text.startswith('remove') or elm_text.startswith('delete') or elm_text.startswith('close'):
                                            logger.write_log_data('Button named with erase / remove / delete / close  is encountered. Hence ignored')
                                            continue
                                    xpath = get_locator(driver, elm)
                                    name = driver.find_element_by_xpath(xpath)
                                    name1=name.text
                                    val = 'click on ' + str(name1)
                                    data_store = save_data(driver, elm,val, data_store,logger)
                                    elm.click()
                                    continue
                                
                            elif elm.tag_name == 'a':
                                print('link is encountered')
                                print(elm.get_attribute('href'))
                                try: 
                                    print('inside try block of link')
                                    etext = elm.text
                                    elink_flag=False
                                    
                                    print(etext,elink_flag)
                                    if etext != None:
                                        elm_title=etext.lower()
                                        if elm_title.startswith('delete') or elm_title.startswith('modify') or elm_title.startswith('remove') or elm_title.startswith('close'):
                                            elink_flag = True
                                        if not elink_flag :
                                            print('has no delete .. hence clicked')
                                            link = get_locator(driver, elm)
                                            name = driver.find_element_by_xpath(link)
                                            name1 = name.get_attribute('innerHTML')
                                            val = 'click on ' + str(name1)
                                            print(val)
                                            data_store = save_data(driver, elm,val, data_store,logger)
                                            logger.write_log_data(val)
                                            elm.click()
                                            continue
                                        else:
                                            print('Has  delete. Hence ignored')
                                            link = get_locator(driver, elm)
    #                                         driver.find_element_by_xpath(link).click()
                                            name = driver.find_element_by_xpath(link)
                                            name1 = name.get_attribute('innerHTML')
                                            val = 'click on ' + str(name1) + ' is ignored as it contains delete/remove/modify/erase'
                                            print(val)
    #                                         data_store[link] = val
#                                             data_store = save_data(driver, elm,val, data_store,logger)
                                            logger.write_log_data(val)
    #                                         elm.click()
                                            continue
                                        
                                    else:
                                        print('other link')
                                        link = get_locator(driver, elm)
                                        name = driver.find_element_by_xpath(link)
                                        name1 = name.get_attribute('innerHTML')
                                        val = 'click on ' + str(name1)
                                        print(val)
                                        data_store = save_data(driver, elm,val, data_store,logger)
#                                         logger.write_log_data(val)
                                        elm.click()
                                        continue
                                        
                                except Exception as e:
                                    print('Link has no title')
                            elif elm.get_attribute('type')== 'submit' : #sumer added or elm.get_attribute('type')== 'button'
                                    
                                    url_new, data_store = submit_btns(driver, elm, data_store,logger)
        #                                 if status:
                                        
                                    err_list = record_errors(driver, url, error_store)
                                    logger.write_log_data(err_list)
                                    print('random_url: ', url_new)
    #                                     if url_new is None:
    #                                         print(5)
    #                                         continue
            #                             return None,data_store,error_store
    #                                     if webelm_list.index(elm)==(len(webelm_list)-1):
                                    if isinstance(url_new, str) and url_new != url and len(webelm_list)==0:
                                        print('is instance')
                                        od=OrderedDict(data_store)
                                        elm=od.popitem()
                                        return [driver.current_url, elm[1], elm[0], driver.title,len(err_list.values())]
                                            
                        else:
                            print(2)
                            print('element is not visible. Hence cannot perform an action. Hence increasing no visible counter')
                            no_visible_counter +=1
                            continue
                    except StaleElementReferenceException as se:
                        print('se1 inside a while loop')
                        print(se)
                        continue
                    except Exception as e:
                        print('Exception occurred inside try within while loop as ' + e)
                        continue
                
#                 if driver.current_url == url:
#                     print('link is within a form - hence continued')
#                     continue
#                 else:
#                 logger.write_log_data('all the webelements are interacted. hence considered to be a new state : ',driver.current_url)
                print('all the webelements are interacted. hence considered to be a new state : ',driver.current_url)
                logger.write_log_data(data_store)
                
                if data_store != {}:#change !alter this condition
                    print('No submit elements are found on that page ')
                    od=OrderedDict(data_store)
                    elm=od.popitem()
                    return [driver.current_url, elm[1], elm[0], driver.title,len(err_list)] #sumer err_list.values to err_list
                
                if no_visible_counter == len(webelm_list) or data_store == {}:
                    logger.write_log_data(data_store)
                    return 'No visible form found!'
                
                #===============================================================
                # if no_visible_counter == len(webelm_list):
                #     logger.write_log_data(data_store)
                #     
                #     return 'No visible form found!'
                #===============================================================
                print('Data used for the current session is as follows \n' + str(data_store))
    #             print('Total number of errors encountered in the current session is {} .\n Errors encountered are as follows :{}'.format(len(err_list), err_list))
            try:
                logger.write_log_data(data_store)
                od=OrderedDict(data_store)
                elm=od.popitem()
                return [driver.current_url, elm[1], elm[0], driver.title,0]
            except Exception as ex:
                print('in 3 lines')
                print(ex)
            #else of (len(webelmlist)!=0
            return 'No visible form found!'
            
        else:
            return 'No visible form found!'
#             logger.write_log_data(data_store)
#             return [driver.current_url, data_store.values()[-1], data_store.keys()[-1], driver.title]
#     
    except StaleElementReferenceException as se:
        print('se2')
        print(se)
        logger.write_log_data(str(se))
         
    except Exception as e:
        print('Exception occurred as {}'.format(e))
        logger.write_log_data(str(e))
        return 'Could not handle form'
        


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from crawl_new_classifier.properties import DAProperties
from crawl_new_classifier.logg import ManualLogger as m
driver=webdriver.Chrome(executable_path=DAProperties.CHROME_DRIVER.value)
urls=['https://www.petstore.com/ps_login.html',
     #'https://www.petstore.com/ps_homepage.aspx',
     #'https://www.petstore.com/Dog_Beds-DGBD-ct.html',
    # 'https://www.petstore.com/Mid_West_Metal_Ombre_Swirl_Fur_Bed_Dog_Lounger_Cuddler_Beds-Midwest_Metal_Products_Co._(Midwest_Homes)-MS00978-DGBDLO-vi.html',
     'https://www.petstore.com/ps_checkout_addresses.html',
     #'https://www.petstore.com/ps_checkout_payment.aspx'
     ]

for url in urls:
    driver.get(url)
    WebDriverWait(driver, 10)
    formElements=driver.find_elements_by_tag_name("form")
    logger = m(url, 999)
    status=get_form_elms(driver, url, logger, formElements)
    print(status)
