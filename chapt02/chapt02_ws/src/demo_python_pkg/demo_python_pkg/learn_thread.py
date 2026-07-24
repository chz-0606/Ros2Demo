import threading
import requests

class Download:
    def download(self, url, callback_word_count):
        print(f'线程：{threading.get_ident()} 开始下载：{url}')
        response = requests.get(url)
        response.encoding = 'utf-8'
        callback_word_count(url, response.text)  #调用回调函数 


    def start_download(self, url, callback_word_count):
        thread = threading.Thread(target=self.download, args=(url, callback_word_count))
        thread.start()

def word_count(url,result):
    print(f"{url}: {len(result)}->{result[0:5]}")


def main():
    download = Download()
    download.start_download('http://0.0.0.0:8080/novel1.txt', word_count)
    download.start_download('http://0.0.0.0:8080/novel2.txt', word_count)
    download.start_download('http://0.0.0.0:8080/novel3.txt', word_count)
