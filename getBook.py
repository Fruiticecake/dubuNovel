import re
import os
import requests
from bs4 import BeautifulSoup
import time
import threading
from queue import Queue

#lock = threading.RLock()
def get_page(url, headers):
    while (1):
        try:
            response = requests.get(url=url, headers=headers)
            break
        except Exception as e:
            print(e)
            time.sleep(2)
    return response

def download_novel(bookName, bookAuther, headers, q, size, count):
    while True:
        detail_url = q.get()

        if detail_url is None:
            break
        try:
            #lock.acquire()
            print(detail_url)
            detail_page = requests.get(url=detail_url,headers=headers, timeout=10)
            detail_page = detail_page.text.encode('iso-8859-1').decode(detail_page.apparent_encoding)
            #存储文件路径
            path = './novel/'
            if not os.path.exists(path):
                os.mkdir(path)
            detail_soup = BeautifulSoup(detail_page, 'lxml')
            detail_tilte = detail_soup.find('div',class_='content').h1.get_text()
            detail_contents = detail_soup.find('div', id= 'cont-body')
            contents = detail_contents.text
            n_path = path + bookName + ' ' + bookAuther + '.txt'
            with open(n_path, 'a', encoding='utf-8') as f:
                for content in contents:
                    f.write(content)
            print(detail_tilte+'下载完成')
            completed = count / size * 100

            #lock.release()
            print('目前已经完成了%0.2f%%' % completed)
            break
        except Exception as e:
            print(e)
        q.task_done()

def get_url(searchUrl, headers, threads, q):
    ##搜索小说
    page_text = get_page(searchUrl, headers).text
    soup = BeautifulSoup(page_text, 'lxml')
    tbody_list = soup.find('tbody')
    book_path = tbody_list.a.get('href')
    ##获得小说名称和作者
    bookName = tbody_list.a.string
    bookAuther = tbody_list.find_all('td')[1].string
    print(bookName+" 作者："+bookAuther)
    ##获取每个章节的url
    bookUrl = "http://www.dubuxiaoshuo.com" + book_path
    book_page = get_page(bookUrl, headers)
    book_page = book_page.text.encode('iso-8859-1').decode(book_page.apparent_encoding)
    book_soup = BeautifulSoup(book_page, 'lxml')
    # print(book_soup)
    book_body = book_soup.select('.panel-body > div')
    a_list = book_body[3]
    a_list = a_list.find_all('div')
    # print(a_list)
    for A in a_list:
        #title = A.a.string
        detail_url = "http://www.dubuxiaoshuo.com"+A.a['href']
        #print(detail_url)
        q.put(detail_url)
    size = q.qsize()
    print('共有：'+size+"章")
    count =0
    while not q.empty():
        for i in range(10):
            count += 1
            t = threading.Thread(target=download_novel, args=(bookName, bookAuther, headers, q, size, count))
            t.start()

            threads.append(t)
        q.join()
        # for i in range(10):
        #     q.put(None)
        for t in threads:
            t.join()
    print('多线程结束')

#os.makedirs('./'+bookName+'.txt')
#fp = open('./'+bookName+bookAuth+'.txt', 'w', encoding='utf-8')
#fp.write(bookName+' 作者: '+bookAuth + "\n\n")

def main():
    bookName = input("请输入要爬取的书的名称： ")
    searchUrl = "http://www.dubuxiaoshuo.com/plus/search.php?q=" + bookName
    q=Queue()
    count = 0
    threads = []
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.63"
    }
    get_url(searchUrl, headers, threads, q)

if __name__ == '__main__':
    main()
