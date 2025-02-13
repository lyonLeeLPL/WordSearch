import requests
from bs4 import BeautifulSoup as bs4
import re
import json

def wirte_word(worddict,word):#测试代码,写入
    fileword=json.dumps(worddict)
    _file="json\\English_{word}.json".format(word=word)
    fileObject = open(_file, 'w')
    fileObject.write(fileword)
    fileObject.close()
def WeblioSearch_English(word):
    result={
        'mean':u'',
        'eg':[],
        'similar':[],
        'Der':[],
        
    }
    try:
        url=u'https://ejje.weblio.jp/content/{word}'.format(word=word)
        get_requests=requests.get(url,timeout=5)#设置超时
        # text = get_requests.content.decode('utf-8')
        soup=bs4(get_requests.content,'html.parser')
    except:
        print("見つからない")
        return result
        # import sys
        # sys.exit(0) 

    result['mean']=soup.find('td',attrs={'class':['content-explanation je','content-explanation ej']}).text #主要意思
    if soup.find('span',attrs={'class':'qotHS'}).text==u'例文': #例句
        for soup_eg in soup.find_all('div',attrs={'class':'qotC'}):
            ret_jp=re.search(r'.*?(?=例文帳に追加)',soup_eg.find('p',attrs={'class':['qotCJJ','qotCE']}).text).group()
            ret_jp=ret_jp.replace('発音を聞く','').strip()   
            ret_us=re.search(r'.*?(?=-)',soup_eg.find('p',attrs={'class':['qotCJE','qotCJ']}).text).group()  
            ret_us=ret_us.replace('発音を聞く','').strip()      
            result['eg'].append(ret_jp+u'<br>'+ret_us)
    for soup_word in soup.find_all('div',attrs={'class':'sideRWordsL'}):#相似单词,可增加内容:HTML
        ret=re.sub(u"\\(.*?\\)", "", soup_word.text.strip()).strip()
        result['similar'].append(ret)
    soup_Der= soup.find('div',attrs={'class':'agltCnt'})#判断是否有派生词
    if soup_Der  is not None:#有的话
        for Der in soup_Der.find_all('li'):#可增加内容:HTML
            ret=re.sub(u"\\(.*?\\)", "", Der.text)
            result['Der'].append(ret)
    result.update()
    wirte_word(result,word)#测试代码
    return result

# word='one'
# fileword=WeblioSearch_English(word)
# print(fileword)