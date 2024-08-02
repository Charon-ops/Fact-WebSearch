
import json
import os 
from pprint import pprint
import requests
# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "v7.0/search"
from typing import Dict,Any,Optional,Tuple,List
from base import net_callback
import os
import requests
import concurrent.futures
import trafilatura
import json
import time
current_file_path = os.path.abspath(__file__)
current_folder = os.path.dirname(current_file_path)

def extract_url_content(url):
    downloaded = trafilatura.fetch_url(url)
    content =  trafilatura.extract(downloaded)
                                                                               
    return {"url":url, "content":content}

class bing_callback(net_callback):
    def __init__(self) -> None:
        super().__init__()
    def bing_query(self,query:str,max_result:Optional[int]=10)->List[str]:
        urls = []
        titles=[]
        items=[]
        headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
        # 构建查询参数
        params = {'q':query, 'responseFilter': 'webPages','mkt': 'zh-CN','count': max_result,}
        max_retries=5
        for attempt in range(max_retries):
            try:
                response = requests.get(endpoint, headers=headers, params=params)
                response.raise_for_status()
                print(response.json())

                for item in response.json()["webPages"]["value"]:
                    urls.append(item["url"])
                    titles.append(item["name"])
                    print(item["name"])
                    items.append({"url": item["url"], "title": item["name"]})

                return urls, titles, items  # 如果成功则返回结果

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP 错误 {http_err.response.status_code}:", http_err)
            except requests.exceptions.ConnectionError as conn_err:
                print(f"连接错误:", conn_err)
            except requests.exceptions.Timeout as timeout_err:
                print(f"请求超时:", timeout_err)
            except Exception as ex:
                print(f"其他错误:", ex)

            # 重试之前的延迟
            if attempt < max_retries - 1:
                print(f"重试次数 {attempt + 1}/{max_retries}，等待 {5} 秒...")
                time.sleep(5)
            else:
                print("达到最大重试次数，无法完成请求。")

        # 如果所有尝试都失败了，抛出最后捕获的异常
        raise
    def recall(self, query:str,max_result:Optional[int]=30,top_k:Optional[int]=10)->None:
        urls,self.titles,items=self.bing_query(query,max_result=max_result)
        print(len(urls))
        self.top_k_web_contents=[]
        id=0
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for top_k_url in urls:
                futures.append(executor.submit(extract_url_content,top_k_url))
                # result=extract_url_content(url=top_k_url)
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result['content'] is not None and not result['content'].startswith('网络不给力') and not result['content'].startswith("We're sorry"):
                    self.top_k_web_contents.append(f"链接:{top_k_url}"+'\n'+"内容:"+result['content'])
                    id+=1
                    if id==top_k:
                        break
    def get_top_k_recall(self,query:str,max_search:int=30,top_k:int=10)->List[str]:
        self.recall(max_result=max_search,query=query)
        return self.top_k_web_contents
        
if __name__=="__main__":
    qery=input("输入query:")
    tool=bing_callback()
    for id,content in enumerate(tool.get_top_k_recall(query=qery,max_search=20,top_k=10)):
        print(f"top-{id}:",content)