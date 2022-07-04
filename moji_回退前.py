import re

import pandas
import requests
from bs4 import BeautifulSoup as bs4, BeautifulSoup
import json

from lxml import etree
from lxml.etree import HTML

from selenium import webdriver

driver = webdriver.PhantomJS(r"C:\soft\phantomjs-2.1.1-windows\bin\phantomjs.exe")
class Moji_old(object):
    word=None
    # words=None
    wordID=list()
    worddict=dict()
    examples=list()
    hd = {'content-type': 'text/plain',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19551'}
    
    target_tts = 'https://api.mojidict.com/parse/functions/fetchTts_v2'#TTS
    tts_data={#这个是单词的,102单词,103例句
        "tarId": '', 
        "tarType": 102, 
        "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
        "_ClientVersion": "js2.12.0"
    }
    
    target_search = 'https://api.mojidict.com/parse/functions/search_v3' #查询单词ID
    data={#单词列表
        'searchText':"",
        "needWords": True,
        "langEnv": "zh-CN_ja",
        "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
        "_ClientVersion": "js2.12.0",
    }

    target_fetch = 'https://api.mojidict.com/parse/functions/fetchWord_v2'#查询单词详细内容
    word_data={#单词详细数据
    "wordId":"",
    "_ApplicationId":"E62VyFVLMiW7kvbtVq3p",
    "_ClientVersion":"js2.12.0"
    }


    target_fetch_html = 'https://www.mojidict.com/details/'#查询单词详细内容
    word_data={#单词详细数据
    "wordId":"",
    "_ApplicationId":"E62VyFVLMiW7kvbtVq3p",
    "_ClientVersion":"js2.12.0"
    }

    def Post_Word(self):
        self.data['searchText'] = self.word
        r = requests.post(self.target_search, data=json.dumps(self.data), headers=self.hd)  # POST请求
        ans = r.json()['result']
        words=ans['words']
        count=0
        for word in words:
            if word['spell']==self.word or word['pron']==self.word:
                self.wordID.append(word['objectId'])
                self.worddict[word['objectId']]=word
                count+=1
        
        if not count and len(words):
            self.wordID.append(words[0]['objectId'])
            self.worddict[words[0]['objectId']]=words[0]
        # self.words=words
    def __init__(self,word):
        self.word=word
        self.Post_Word()
        self.get_selenium_html()

    def Get_TTS(self,wordID,wordtts=True):#取单词/例句发音
        self.tts_data['tarId']=wordID
        if not wordtts:
            tts_data["tarType"]=103
        r_tts = requests.post(self.target_tts, data=json.dumps(self.tts_data), headers=self.hd)#取单词/例句发音地址
        tts=r_tts.json()['result']['result']['url']
        return tts

    def mean_simple(self,wordID=None):
        if wordID==None:
            wordID=self.wordID[0]
        word=self.worddict[wordID]
        word_Part_of_speech='['+''.join(re.findall(r'\[(.*?)\]',word['excerpt']))+']'
        word_val=re.sub(r"\[(.*?)\]", "",word['excerpt']).split()
        result={
            'wordID':word['objectId'],
            'spell':word['spell'],
            'pron':word['pron'],
            'excerpt':word['excerpt'],
            'word_Part_of_speech':word_Part_of_speech,
            'word_val':word_val,
        }
        return result

    def get_selenium_html(self,wordID=None):
        if wordID == None:
            wordID = self.wordID[-1]
        self.word_data['wordId'] = wordID
        worddict = self.worddict[wordID]
        target_fetch_html = self.target_fetch_html + wordID
        driver.get(target_fetch_html)
        # 获取页面名为 wrapper的id标签的文本内容
        selenium_htmls = driver.find_elements_by_xpath("//div[@class=\"el-collapse\" ] ")
        text = ""

        for selenium_html in selenium_htmls:
            outerHTML = selenium_html.get_attribute("outerHTML")
            soup = BeautifulSoup(outerHTML, "lxml")

            tar_text = soup.text
            # 洗う出す
            index1 = tar_text.find("熟练度")
            if index1 > -1 :
                tar_text = tar_text.replace("熟练度","")
            index = tar_text.find("选择其它文件夹")
            if index > -1:
                tar_text=tar_text.replace("选择其它文件夹", "")
            index = tar_text.find("认识模糊不认识")
            if index > -1:
                tar_text = tar_text.replace("认识模糊不认识", "")
            index = tar_text.find("()")
            if index > -1:
                tar_text=tar_text.replace("()", "")
            index = tar_text.find("。")
            if index > -1:
                tar_text=tar_text[:index1] + tar_text[index1:].replace("。", "。\n")

            text += tar_text + "\n"
            text += "=======================================================================\n"
        print(text)

        worddict['outerHTML'] = tar_text
        worddict['url'] = target_fetch_html

    def Get_Word(self,wordID=None):
        if wordID==None:
            wordID=self.wordID[0]
        self.word_data['wordId']=wordID
        r= requests.post(self.target_fetch, data=json.dumps(self.word_data), headers=self.hd) #取单词详细内容
        text=r.json()['result']
        # print(json.dumps(text))
        bad=list()
        word_spell=text['word']['spell']+' | '+text['word']['pron']+' '+text['word']['accent']
        ret=u'<div class="mojidict-helper-card"><div class="word-detail-container"><div class="word-spell">{word}</div>'.format(word=word_spell)
        for details in text['details']:
            detailsID=details['objectId']
            i=1
            for subdetails in text['subdetails']:
                subdetailsID=subdetails['objectId']
                if (detailsID==subdetails['detailsId']):
                    if details['title'] not in bad:
                        ret+='''<div class="word-detail"><span class="detail-title">{details}</span>'''.format(details=details['title'])
                        bad.append(details['title'])
                    if subdetails['title'] not in bad:
                        ret+='<p>{i_count}.{subdetails}</p>'.format(i_count=i,subdetails=subdetails['title'])
                        i=i+1
                        bad.append(subdetails['title'])
        ret+='</div>'*3
        return ret
    
    def Get_URL(self,wordID=None):
        if wordID==None:
            wordID=self.wordID[0]
        return u'<a href="{url}" one-link-mark="yes">{word}</a>'.format(url=u'https://www.mojidict.com/details/{wordID}'.format(wordID=wordID),\
            word=self.worddict[wordID]['spell'])
        

    # def Get_Word2(self,wordID=None):
    #     if wordID==None:
    #         wordID=self.wordID[0]
    #     self.word_data['wordId']=wordID
    #     r= requests.post(self.target_fetch, data=json.dumps(self.word_data), headers=self.hd) #取单词详细内容
    #     text=r.json()['result']
    #     word=dict()
    #     bad=list()
    #     for details in text['details']:
    #         detailsID=details['objectId']
    #         i=1
    #         for subdetails in text['subdetails']:
    #             subdetailsID=subdetails['objectId']
    #             for examples in text['examples']:
    #                 examplesID=examples['objectId']
    #                 a=[detailsID,subdetailsID]
    #                 b=[subdetails['detailsId'],examples['subdetailsId']]
    #                 if a==b:
    #                     if i==1:
    #                         print(details['title'])
    #                         print('1.',subdetails['title'])
    #                     else:
    #                         print(i,'.',subdetails['title'])
    #                     i+=1
    #                     # str_='{details}\t{subdetails}\n{examples}\t{trans}'.format(\
    #                     #     details='\t' if details['title'] in bad else details['title'],
    #                     #     subdetails='\t' if subdetails['title'] in bad else str(i)+subdetails['title'],
    #                     #     examples=examples['title'],
    #                     #     trans=examples['trans'],
    #                     #     )
    #                     # i=i if subdetails['title'] in bad else i+1
    #                     # bad.append(details['title'])
    #                     # bad.append(subdetails['title'])
    #                     # print(str_)

    #     # return word

### 载入 xlsx
file_path = "C:\\360\\日语N1核心副词300.csv"

result = pandas.read_csv(file_path)

## 循环
records = result.to_dict("records")
for record in records:
    print(record)
    word = record["日文"]
    moji_word = Moji_old(word)


print(moji_word.worddict.values())
values = moji_word.worddict.values()
df = pandas.DataFrame(values)

df.to_excel(file_path + "2.xlsx")


