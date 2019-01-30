
#===============================================================================
# Importing required packages

import datetime , random , time , re ,string, pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from crawl_new_classifier.logg import ManualLogger as m
from bs4 import BeautifulSoup
from random import choice
# from string import ascii_letters,ascii_uppercase
from selenium.webdriver.support.ui import Select
from collections import OrderedDict
#===============================================================================


import random
from selenium import webdriver
import crawl_new_classifier.py_m_connect as db_handler
from configparser import ConfigParser
from crawl_new_classifier.properties import DAProperties
#ivsohinfy@gmail.com
'''
data_dict = {0: "infyivsoh@gmail.com", 1: "infyivsoh!123", 2:'241EDW',3:'ECMU1234567',4:'LHV1762853',5:2230,6:32000,7:'testname'} #3 is reserved for vesselreference
res = db_handler.get_data_for_test_field()
#create new list =
# attributes=["infotype","mail","credentials","voyage","vessel","container"]

infotype=list()
mail=list()
credentials=list()
voyage=list()
container=list()
booking=list()
tareweight=list()
maxgrossweight=list()
name=list()
# vgm0=list()
# grossw0=list()

 
for each in res[0]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        infotype.append(each)
    except:
        pass

for each in res[1]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        mail.append(each)
    except:
        pass
for each in res[2]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        credentials.append(each)
    except:
        pass

for each in res[3]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        voyage.append(each)
    except:
        pass

for each in res[4]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        container.append(each)
    except:
        pass    

for each in res[5]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        booking.append(each)
    except:
        pass

for each in res[6]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        tareweight.append(each)
    except:
        pass
    
for each in res[7]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        maxgrossweight.append(each)
    except:
        pass
    
for each in res[8]:
    try:
        each = ''.join(e for e in each if e.isalnum())
        name.append(each)
    except:
        pass
    
#===============================================================================
# for each in res[9]:
#     try:
#         each = ''.join(e for e in each if e.isalnum())
#         vgm0.append(each)
#     except:
#         pass
#     
# for each in res[10]:
#     try:
#         each = ''.join(e for e in each if e.isalnum())
#         grossw0.append(each)
#     except:
#         pass
#===============================================================================
    


form_data = {}

# input_dict = dict()  # dictionary based on the type of inputs input_dict={ele_type(key) : list_of_elements(value)}
iporder=[mail,credentials,voyage,container,booking,tareweight,maxgrossweight,name]
'''

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
import os
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

#input - driver, selenium webelm | output - dictionary containing element attributes as contained in the HTML DOM
def get_all_elm_attrs(driver, elm):
    '''
    returns a dictionary object of all the attributes from the DOM structure for a particular web element
    '''
    elm_dict = (driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',elm))
    elm_dict = (dict((k.lower(),v.lower()) for k,v in elm_dict.items()))
    print('return type of elm attributes',type(elm_dict))
    return elm_dict


def get_locator(driver, element):
    # returns the xpath of the element for the future use
    print('inside get locator forms_latest')
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
                            return gPt(arguments[0]);""", element)
    return element_xpath

#===============================================================================

def save_data(driver, elm, ipval, data_store,logger):
    print('inside save_data')
    xpath = get_locator(driver, elm)
    print('input value in save_data is ',str(ipval))
    action = 'Enter ' + str(ipval) + ' to element ' + str(xpath) 
    data_store[xpath] = action
    logger.write_log_data(action)
    return data_store

#===============================================================================

def find_parent(driver,elm,elmtype):
    print('finding parents')
    options_len={'radio':2,'checkbox':2}
    print('=2=3=4=5=6=7=8=9=9=0=')
    if elmtype in options_len.keys():
        min_opt_len=options_len[elmtype]
    print(min_opt_len)
#     if elmtype=='checkbox':
#         td_p_input = elm.find_element_by_xpath('../..')
#     else:
    td_p_input = elm.find_element_by_xpath('..')
    options = [elm for elm in  td_p_input.find_elements_by_tag_name("input") if elm.get_attribute('type') not in ['hidden','file'] and elm.get_attribute('type')==elmtype]
    if len(options)>=min_opt_len:
#         print(options)
        print('number of available options are :',len(options))
        return options
    else:
        return find_parent(driver, td_p_input,elmtype)
    
#===============================================================================

def radio_elm(driver, elm, welms, data_store,logger):
    print('radio elms')
    try:
        options = find_parent(driver,elm,elm.get_attribute('type')) 
        for i in options:
            if i in welms:
                welms.remove(i)
        option = random.choice(options)
        data_store = save_data(driver,elm, option.get_attribute('value'), data_store,logger)
        option.click()
        return data_store , welms
    except Exception as e:
        print('Unknown radio button exception occurred',e)
        return data_store , welms

#===============================================================================


def checkbox_elm(driver, elm, welms, data_store,logger):
    print('checkbox elements')
    try:
        options = find_parent(driver,elm,elm.get_attribute('type')) 
        if len(options) == 1:
            welms.remove[options[0]]
            option = options[0]
            option.click()
            time.sleep(3)
            options.remove(option)
            print('selected checkbox option is ' + str(option.get_attribute('innerHTML')))
            data_store = save_data(driver, elm, str(option.get_attribute('title')), data_store, logger)
            return data_store , welms
        for i in options:
            if i in welms:
                welms.remove(i)
        no_of_checks, random_option  = random.randint(1, len(options)),[]
        for i in range(no_of_checks):
            try:
                option = random.choice(options)
                if (not option.is_selected) or (option not in random_option):
                    option.click()
                    time.sleep(3)
                    options.remove(option)
                    print('selected checkbox option is ' + str(option.get_attribute('innerHTML')))
                    data_store = save_data(driver, elm, str(option.get_attribute('title')), data_store, logger)
                else:
                    pass
                random_option.append(option)
            except:
                print('element not visible or some unexpected error encountered')
                print(option.get_attribute('outerHTML'))
                return data_store , welms
#         print('selected checkbox option is ' + str(option.get_attribute('innerHTML')))   
    except Exception as e:
        print('Unknown checkbox exception occurred: \t\t' ,e)
        
    return data_store , welms
#===============================================================================

     
        
def select_elm(driver, elm, data_store,logger):
    print('drop downs')
    try:
        select = Select(driver.find_element_by_xpath(get_locator(driver, elm)))
        time.sleep(2)
        print('element located')
        print('no of options avaiable are' + str(len(select.options)))
        print('#######################################################')
        options1 = [o.text for o in select.options]
        
        default_op=options1[0].lower()
        if default_op.startswith('select') or default_op.startswith('choose') or default_op in ['','-']:
            options = options1[1:]
        else:
            options = options1[:]
        option = random.choice(options)
        select.select_by_visible_text(option)
        print('element selected is ' + option)
#             data_store = save_data(driver, elm, option, data_store,logger)
        ipval = elm.get_attribute('value')
        data_store = save_data(driver, elm, ipval, data_store, logger)
#         return option
    except Exception as e:
        print('Drop down cannot be located')
        print(e)
#         return None
    return data_store
#===============================================================================

  
def textarea_elm(driver, elm, data_store,logger):
    print('textarea')
    try:
        text = ''.join(choice(string.ascii_letters) for i in range(random.randint(1, 50)))
        elm.send_keys(text) 
        data_store = save_data(driver, elm, text, data_store,logger)
        print(text)
    except Exception as e:
        print('Unknown exception occurred in textarea')
        print(e)
#         return None
    return data_store
#===============================================================================
#===============================================================================

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
#===============================================================================

#===============================================================================
# def vgminput(driver, elm, data_store,logger):
#     print('inside form->testem->if3 ')
# #     pos=iporder.index('tareweight')
# #     print('vgm pos is ',pos)
#     tarewgt=data_dict[5]
#     print('tareweight is ',tarewgt)
#     vgmval=str(random.randint(tarewgt,99999))
#     print('vgmvalue is ',vgmval)
#     data_store = save_data(driver, elm, vgmval, data_store,logger)
#     elm.send_keys(vgmval)
#     return data_store
#===============================================================================

#===============================================================================
# def grosswinput(driver, elm, data_store,logger):
# #     pos=iporder.index('maxgrossweight')
# #     print('maxwgt pos is ',pos)
#     maxwgt=data_dict[6]
#     tareweight=data_dict[5]
#     print('maxwgt is',maxwgt)
#     grossval=str(random.randint(2300,maxwgt))
#     print('gross weight entered is ',grossval)
#     data_store = save_data(driver, elm, grossval, data_store,logger)
#     elm.send_keys(grossval)
#     return data_store
#===============================================================================

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
            if str(elm.get_attribute('type')).lower() == "text":
                if re.search('email', elm.get_attribute('outerHTML')) is not None:
                    elm.send_keys("sampleemail123@gmail.com")
                elif re.search('mobile', elm.get_attribute('outerHTML')) is not None or re.search('phone', elm.get_attribute('outerHTML')) is not None:
                    elm.send_keys("0987654321")
                else:
                    elm.send_keys("Sample text data")
            elif str(elm.get_attribute('type')).lower() == "email":
                elm.send_keys("sampleemail123@gmail.com")
            elif re.search('mobile', elm.get_attribute('outerHTML')) is not None or re.search('phone', elm.get_attribute('outerHTML')) is not None:
                elm.send_keys("0987654321")
            elif str(elm.get_attribute('type')).lower() == "password":
                elm.send_keys("Infy@1234")


            """
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
                text = ''.join(choice(string.ascii_letters) for i in range(random.randint(2, 4)))
#                 ipval=data_dict[pos]
                data_store = save_data(driver, elm, text, data_store,logger)
                elm.send_keys(text)
                flag = 1
                return data_store
            """
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
            print('button clicked')
            time.sleep(10)
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

def submit_btns(driver, elm, data_store,logger):
    
    print('Proceeding with the normal buttons snippet')
    print('submit buttons')
    try:
        print('inside try of submit')
        print(elm)
        xpath = get_locator(driver, elm)
        name = driver.find_element_by_xpath(xpath)
        print(elm.get_attribute('innerHTML'))
        if name.get_attribute('innerHTML')!= None: #sumer name to elm
            name1=elm.get_attribute('innerHTML') #sumer name to elm
        else:
            name1=elm.get_attribute('value') #sumer name to elm
        ipval = 'click on '+name1
        print('val is ' ,ipval,type(ipval))
        data_store = save_data(driver, elm, ipval, data_store, logger)
        elm.click()
#         if driver.current_url != url:
#             return True, driver.current_url , data_store
#         return False, url , data_store
        print('exiting from the submit buttons function')
        return driver.current_url,data_store
    except Exception as e:
        print('Error occurred while submitting a form')
        print(e)
        return None

#===============================================================================
#===============================================================================
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


def re_order_elms(driver, url, elm_dict, welm_dict,elm_dict_values_temp):
    print('reordering web elements in progress')
    iporder, iporderhtml = get_input_order(driver, url)
    print('length of ordered elements ',len(iporder))
    ipops = zip(iporder, iporderhtml)
    elm_order = []
#     print('elm values in reorder elms ',elm_dict.values())

    for i in ipops:
        temp = sorted(i[0])
#         if temp in elm_dict_values:
#             for key, value in elm_dict.items():
#                 if temp == value:
#                     pos=elm_dict_values.index(temp)
#                     htmlkey = key
#                     print(htmlkey)
#                     break
        if temp in elm_dict_values_temp:
            for position,element in enumerate(elm_dict):
#                 print(type(element))
    #             print('\n\n',element)
                if temp == element[1]:
                    htmlkey = element[0] 
                    print('####################')
                    print(type(element),htmlkey)            
    #             elm_order.append(welm_dict[htmlkey])            
                    welm=welm_dict[position]                
                    elm_order.append(welm[1])
                    print('welm details after each iteration is ',welm)
                    print('elm order length after each iteration is ',len(elm_order))
                    print('####################')   
                    break     
    print('len of elm orders is ' + str(len(elm_order)))
    return elm_order


def grp_elms(driver, frmelm, url):
    print('inside grp_elms')
    input_dict = dict()  # dictionary based on the type of inputs input_dict={ele_type(key) : list_of_elements(value)}
    elm_dict = list()
    print(frmelm.get_attribute('action'))
    elms = [elm for elm in frmelm.find_elements_by_tag_name("input") if (elm.get_attribute("type") not in [ 'hidden','file'])]
    print(len(elms))
    for elm in elms:
        try:
            elm_type = elm.get_attribute('type')
            print(elm_type)
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
    tagnames = ['select', 'button', 'textarea']  # possible input options on a web-page 
    print(input_dict.keys())
    for i in tagnames:
        print(i)
        temp = [elm for elm in frmelm.find_elements_by_tag_name(i) if elm.get_attribute("type") not in [ 'hidden' , 'file' ] ]
        print(len(temp))
        if temp != []:
            input_dict[i] = temp
            elms.extend(temp)
            print(i, len(elms))
    print(elms)
    print('len of elms final'+str(len(elms))) #sumer: just for print
    return elms    #change 05nov bindiya
    '''
    to get the links inside the form
    '''
#sumer: to ignore links in forms
#===============================================================================
#     print('len of elms initial after buttons etc before links' + str(len(elms)))
#     links_in_page = []
#     links_partial = frmelm.find_elements_by_partial_link_text('')
#     if links_partial:
#         for i in links_partial:
#             links_in_page.append(i.get_attribute('href'))
#             elms.append(i)
#         input_dict['a'] = links_in_page
# #         elms.extend(links_in_page)
#     
#     print('len of links in elms'+str(len(links_in_page)))
#     print('len of elms final'+str(len(elms)))
#===============================================================================
#sumer
''' this segment can be ignored as of now for all the ecom sites
    for elm in elms:
        try:
            print(elm.tag_name)
            ohtml = elm.get_attribute('outerHTML')
            ohtml = ohtml[ohtml.index('<'):ohtml.index('>')]
            temp_list=[ohtml,elm]
#             elm_dict[ohtml] = elm
            elm_dict.append(temp_list)
        except Exception as e:
            print(e)
    print('after formatting the tags',len(elm_dict))
    elm_dict_keys_temp = []  # temp keys. not used anywhere in the program
    shufelm = list()
#     shufelm={}
#     for i in elm_dict.keys():
    print(elm_dict)
    #sumer
    elem_list=[]
    for i in elm_dict:
        print('elmtype inn elm_dict is ',type(i),len(i),i)
        elem_list.append(i[1])
    if elem_list !=[]:    
        return elem_list
    return []
    #sumer
'''
#sumer
#===============================================================================
#         j = i[0]
#         i1=i[0]
#         print(j,i1)
#         oh = sorted(list(set(i1.split(' '))))
#         oh1 = []
#         for i1 in oh:
#             i1 = re.sub('/', '', i1)
#             oh1.append(i1)
#         elm_dict_keys_temp.append(oh1)
#         temp_lis=[j,oh1]
#         shufelm.append(temp_lis)
#         
# #         shufelm[j] = oh1
# #     print('elm dict order is html:webelm')
# #     print('shufelm order is html:sorted')
#     print('outside all for loops in forms_latest')
#     print(len(shufelm),len(elm_dict))
#     
# #     print(shufelm.keys())
# #     print(shufelm.values())
#     
# #     webelementlist = re_order_elms(driver, url, shufelm, elm_dict)
#     webelementlist = re_order_elms(driver, url, shufelm, elm_dict,elm_dict_keys_temp)
#     print(len(webelementlist))
#     if webelementlist !=[]:    
#         return webelementlist
#     return []
#===============================================================================
#sumer
'''
functions for re-ordering the elements ends here
'''
#=======================================================================
# To extract the form elements of the current web page

def get_form_elms(driver, url,formelm):
    try:
        logger = m(url, 999)
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
            print("action :" , form.get_attribute('action'))
#             global webelm_list
            
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
                                data_store , webelm_list = checkbox_elm(driver, elm, webelm_list, data_store,logger)
                                continue
                            
                            elif elm.tag_name == 'select': 
                                data_store = select_elm(driver, elm, data_store,logger)
                                continue
                            
                            elif elm.get_attribute('type') == 'textarea':
                                data_store = textarea_elm(driver, elm, data_store,logger)
                                continue
                            
                            elif elm.get_attribute('type') in ['text', 'password', 'email', 'number']: #sumer 'email' added
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
                                elif elm.get_attribute('id')!=None and elm.get_attribute('id').lower() == 'addvgmblock':
                                    print('addvgm block')
                                    logger.write_log_data('ADD vgm block encountered and hence skipped')
                                    continue
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
#                                     data_store[xpath] = val
                                    data_store = save_data(driver, elm,val, data_store,logger)
#                                     logger.write_log_data(val)
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

#===============================================================================
# #===============================================================================
driver=webdriver.Chrome(executable_path=DAProperties.CHROME_DRIVER.value)
# # url='http://www.cma-cgm.com/ebusiness/schedules/voyage'
# url='https://www.cma-cgm.com/ebusiness/schedules'
url='https://www.myntra.com/register?referer=https://www.myntra.com/'
WebDriverWait(driver, 5)
# # # url="https://m.costco.com/LogonForm"
# # # url='https://lenskartinc.freshdesk.com/support/login'
# # url='https://www.cma-cgm.com/ebusiness/tarifs/insurance_request'
# # # url='https://auth.cma-cgm.com/idp/prp.wsf?wctx=WsFedOwinState%3DeAXD3QB4EbAaxsAtGwkKHq-hdaXnDrjNz26aE6yFW1HK9ixJ56RUI47rptz9gh23iIql8gdkdHSt1PdUbx75SekRi4aU9gmCDAAWVwE7En1-KAhZ7LmAxp7jgDkcfeHruMZKwn-87mFy-AYUiAao5A%26Language%3Den-US%26actas%3Dfalse%26Site%3Dcmacgm&wa=wsignin1.0&wtrealm=https%3A%2F%2Fwww.cma-cgm.com&wauth=urn%3Aoasis%3Anames%3Atc%3ASAML%3A1.0%3Aam%3Apassword'
# # # url='https://www.jcpenney.com/signin
#logobj = m()
driver.get(url)
formElements=driver.find_elements_by_tag_name("form")
status=get_form_elms(driver,url,formElements)
print(status)
# print (randomDate("1/1/2005", datetime.date.today().strftime('%m/%d/%Y'), random.random()))
#===============================================================================
