'''
Created on Apr 23, 2018

@author: sachin.nandakumar
'''
from crawl_new_classifier.python_mysql_connection import read_db_config
import MySQLdb, datetime
 
conn = None

def get_data():
    """ Connect to MySQL database """
    global conn
    db_config = read_db_config()
    try:
        print('Connecting to MySQL database...')
        conn = MySQLdb.connect(**db_config)
        cur = conn.cursor()
        cur.execute('SELECT testid, test_url, testtype FROM queue_data')
        row = cur.fetchone()
        
        if row is not None:
            print('in get_data')
            return row
    finally:
        conn.close()
        print('Connection closed.')
        
def get_data_for_test_field():
    """ Connect to MySQL database """
    global conn
    db_config = read_db_config()
    try:
        print('Connecting to MySQL database...')
        conn = MySQLdb.connect(**db_config)
        cur1 = conn.cursor()
        cur1.execute('SELECT eleminfo FROM attributes')
        row1 = cur1.fetchall()
        cur1.execute('SELECT mail FROM attributes')
        row2 = cur1.fetchall()
        cur1.execute('SELECT credentials FROM attributes')
        row3 = cur1.fetchall()
        cur1.execute('SELECT firstname FROM attributes')
        row4 = cur1.fetchall()
        cur1.execute('SELECT lastname FROM attributes')
        row5 = cur1.fetchall()
        cur1.execute('SELECT addressline FROM attributes')
        row6 = cur1.fetchall()
        cur1.execute('SELECT city FROM attributes')
        row7 = cur1.fetchall()
        cur1.execute('SELECT state FROM attributes')
        row8 = cur1.fetchall()
        cur1.execute('SELECT zipcode FROM attributes')
        row9 = cur1.fetchall()
        cur1.execute('SELECT phonenumber FROM attributes')
        row10 = cur1.fetchall()
        cur1.execute('SELECT phonenumber_split FROM attributes')
        row11 = cur1.fetchall()
        cur1.execute('SELECT shippingtype FROM attributes')
        row12 = cur1.fetchall()
        cur1.execute('SELECT cardnumber FROM attributes')
        row13 = cur1.fetchall()
        cur1.execute('SELECT cardtype FROM attributes')
        row14 = cur1.fetchall()
        cur1.execute('SELECT cardname FROM attributes')
        row15 = cur1.fetchall()
        cur1.execute('SELECT expirymonth FROM attributes')
        row16 = cur1.fetchall()
        cur1.execute('SELECT expiryyear FROM attributes')
        row17 = cur1.fetchall()
        cur1.execute('SELECT securitycode FROM attributes')
        row18 = cur1.fetchall()
        cur1.execute('SELECT bday_month FROM attributes')
        row19 = cur1.fetchall()
        cur1.execute('SELECT bday_day FROM attributes')
        row20 = cur1.fetchall()
        cur1.execute('SELECT search FROM attributes')
        row21 = cur1.fetchall()
        cur1.execute('SELECT coupons FROM attributes')
        row22 = cur1.fetchall()
        cur1.execute('SELECT giftcertificate FROM attributes')
        row23 = cur1.fetchall()
        return [row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12, row13, row14, row15, row16, row17, row18, row19, row20, row21, row22, row23]
    finally:
        conn.close()
        print('Connection closed.')        

def check_default(url):
    print('validating for the default run')
    global conn
    db_config = read_db_config()
    try:
        print('connecting to crawlschedule db')
        conn = MySQLdb.connect(**db_config)
        cur = conn.cursor()
        sql = "Select count(test_url) from crawlschedule where test_url = %s"
        atr = (str(url),)
        cur.execute(sql,atr)
        row1 = cur.fetchall()
        if row1[0] != 0:
            print('Default run is completed for this url')
            return False
        return True
    except Exception as _:
        print('Exception while checking the default run',_)
            
def insert_startdatetime(testId):
    """ Connect to MySQL database """
    global conn
    db_config = read_db_config()
    try:
        print('insert_startdatetime')
        print('Connecting to MySQL database...')
        date = datetime.date.today()
        time = datetime.datetime.now().time()
        conn = MySQLdb.connect(**db_config)
        conn.set_character_set('utf8')
        cur = conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute ("""
           UPDATE crawlschedule
           SET start_date=%s, start_time=%s
           WHERE testid=%s
        """, (date.strftime('%d-%b-%Y'),time.strftime('%H:%M:%S'), str(testId)))
        conn.commit()
        print('committed')
    finally:
        conn.close()
        print('Connection closed.')

def insert_enddatetime(testId):
    """ Connect to MySQL database """
    global conn
    db_config = read_db_config()
    try:
        print('insert_enddatetime')
        print('Connecting to MySQL database...')
        date = datetime.date.today()
        time = datetime.datetime.now().time()
        conn = MySQLdb.connect(**db_config)
        conn.set_character_set('utf8')
        cur = conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute ("""
           UPDATE crawlschedule
           SET end_date=%s, end_time=%s
           WHERE testid=%s
        """, (date.strftime('%d-%b-%Y'),time.strftime('%H:%M:%S'), str(testId)))
        conn.commit()
        print('committed')
        
    finally:
        conn.close()
        print('Connection closed.')
        
        
def put_data(paths, error, testId, states,urls_visited, status):
    """ Connect to MySQL database """
    global conn
    print(str(paths))
    print(str(error))
    print(str(testId))
    print(status)
    db_config = read_db_config()
    try:
        print('in put_data')
        print('Connecting to MySQL database...')
        conn = MySQLdb.connect(**db_config)
        cur = conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute ("""
           UPDATE crawlschedule
           SET test_paths=%s, test_error=%s, test_states=%s, test_status=%s , urls_visited=%s
           WHERE testid=%s
        """, (str(paths), str(error), str(states), status,str(urls_visited), str(testId)))
        conn.commit()
        print('committed')
    finally:
        conn.close()
        print('Connection closed.')
        
def insert_webpage_errors(testId, url, error):
    """ Connect to MySQL database """
    global conn
    print('blabla')
    db_config = read_db_config()
    try:
        print('in insert_webpage_errors')
        print('Connecting to MySQL database...')
        conn = MySQLdb.connect(**db_config)
        conn.set_character_set('utf8')
        cur = conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute ("""INSERT INTO webpage_errors VALUES (%s,%s, %s)""",(str(testId),url, str(error)))
        conn.commit()
        print('committed')
    finally:
        conn.close()
        print('Connection closed.')

def delete_data(testId):
    """ Connect to MySQL database """
    global conn
    db_config = read_db_config()
    try:
        print('Connecting to MySQL database...')
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()
        delstatmt = "DELETE FROM queue_data WHERE testid = %s"
        cursor.execute(delstatmt, (testId,))
        conn.commit()
        
        
    finally:
        conn.close()
        print('Connection closed.')

def insert_webpage_classification(testId, url, categeory, image, conn):
    """ Connect to MySQL database """
    try:
        conn.set_character_set('utf8')
        cur = conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute ("""INSERT INTO webpage_classification VALUES (%s, %s, %s, %s)""",(testId, url, str(categeory), image))
        conn.commit()
        print('committed')
    except Exception as ex:
        print(ex)


def make_db_connection():
    global conn
    db_config = read_db_config()
    try:
        print('Connecting to MySQL database...')
        conn = MySQLdb.connect(**db_config)
        conn.set_character_set('utf8')
        return conn
    except Exception as ex:
        print(ex)
"""        
CREATE TABLE idas.webpage_classification
(
   testId INT NOT NULL,
   pageUrl TEXT,
   pageClassification VARCHAR(50),
   pageImage LONGBLOB
);
"""
