# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 14:45:10 2017

@author: prashant_arya
"""

import re
import numpy as np

# from selenium import webdriver

import lxml.html as LH
import lxml.html.clean as clean

from nltk import pos_tag, word_tokenize, WordNetLemmatizer
from nltk.corpus import wordnet as wn, stopwords as sw

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler


class Predictor:
    def __init__(self, driver, model, graph):
        self.browser = driver
#         webdriver.Chrome(executable_path="C:\\Users\\sachin.nandakumar\\Desktop\\AI\\chromedriver.exe")
        self.page_classifier = model
        self.ignore_tags = ('script', 'noscript', 'style')
        self.graph = graph

    def classifier(self):
        try:
            # Navigating to page and extracting text
#             self.browser.get(url)
            content = self.browser.page_source
            cleaner = clean.Cleaner()
            content = cleaner.clean_html(content)
            
            doc = LH.fromstring(content)
            extracted_text = ""
            for elt in doc.iterdescendants():
                if elt.tag in self.ignore_tags: continue
                text = elt.text or ''
#                 print('text.strip().rstrip(): ',text.strip().rstrip())
                extracted_text += " " + text.strip().rstrip()
#             print(extracted_text)
        except Exception as ex:
            print("Unable to access page")
            print(ex)
        
        wnl = WordNetLemmatizer()
        token_lemmatized = []
        for token, tag in pos_tag(word_tokenize(extracted_text)):
            # Changing all tokens to lower case
            token = token.lower()
            
            # Ignoring stop words using Stopwords Corpus and punctuation using string library
            if re.search("[^a-z]", token) is not None: continue
            if token in sw.words('english'): continue
            
            # Dictionary to get POS from Punkt to WordNet for lemmatizing
            tag = {
                    'N': wn.NOUN,
                    'R': wn.ADV,
                    'V': wn.VERB,
                    'J': wn.ADJ
            }.get(tag[0], wn.NOUN)
            
            # Lemmatize token using WordNet and append to array
            token_lemmatized.append(wnl.lemmatize(token, tag))
            
        X_text = " ".join(token_lemmatized)
        
        tokenList = [word for line in open("D:\\IVSSOLH\\Deep_Assurance\\pythoncode\\Crawler\\tokenList_81.71.txt") for word in line.split()]
        tfidf_vect = TfidfVectorizer().fit(tokenList)
        X_tfidf = tfidf_vect.transform([X_text])
        X_tfidf = X_tfidf.todense()
        
        # Normalizing the input matrix
        sc = StandardScaler()
        X = sc.fit_transform(X_tfidf)
        
        with self.graph.as_default():
            y_pred = self.page_classifier.predict(X_tfidf)
            
        y_addCol = np.zeros((1, 1))
        if np.sum(y_pred) == 0:
            y_addCol = 1
        y_absPred = np.append(y_addCol, y_pred, axis = 1)
        labels = ['Home page',
                  'My account pages',
                  'Product category page',
                  'Product listing page',
                  'Product pages',
                  'Shopping cart page',
                  'Static information pages',
                  'Submit order page']
        y_label = labels[y_absPred.argmax()]
        print('classification: ',y_label)
        return y_label
    
    def close_driver(self):
        self.browser.close()
