from langchain.prompts import PromptTemplate
from bing_callback3 import bing_callback
from requery import judge_requery
from typing import List,Tuple
import concurrent.futures
#需添加的prompt部分
template = """
用中文回答
你需要根据提供的证据来回答问题,如果
证据为空
或
提供的证据对问题没有帮助
或
证据不完整(如证据中缺少关键信息，有题目但无答案解析)
则凭自身能力来回答问题，且附上证据中对解决问题有帮助的部分,和链接对应的网站名字，而非链接名
**证据开始位置**
{context}
**证据结束位置**
"""
template2 = """
用中文回答问题
"""
import random
from http import HTTPStatus
import dashscope


def call_with_messages(template,query)->str:
    messages = [
        {'role': 'system', 'content': f"{template}"},
        {'role': 'user', 'content': f"{query}"}]
    response = dashscope.Generation.call(
        'qwen-plus',
        messages=messages,
        # set the random seed, optional, default to 1234 if not set
        seed=random.randint(1, 10000),
        result_format='message',  # set the result to be "message" format.
    )
    if response.status_code == HTTPStatus.OK:
        output=response["output"]["choices"][0]["message"]["content"]
        print(output)
        return output
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))

def generate_answer(id,recall_result,query):
     #有添加召回信息的模板
    prompt_template_with_recall = PromptTemplate(
    input_variables = ["context"],
    template = template
    )
    P_With_Recall = prompt_template_with_recall.format(context=recall_result)
    result_With_Recall=call_with_messages(P_With_Recall,query)
    return result_With_Recall

def helpfulness_detect(query,question)->Tuple[List[str],List[str],str]:
    
    tools=bing_callback()
    recall_results=tools.get_top_k_recall(query=question,max_search=20,top_k=10)
    result_With_Recalls=[]
    print(len(recall_results))
    #删除选项，以防止造成幻觉
    futures=[]
    query=judge_requery(question,query)
    #无添加召回信息的模板
    prompt_template_without_recall = template2
    result_Without_Recall=call_with_messages(prompt_template_without_recall,query)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # 提交多个任务到线程池
        for id,recall_result in enumerate(recall_results):
            futures.append(executor.submit(generate_answer,id,recall_result,query))
        for future in concurrent.futures.as_completed(futures):
            result_With_Recall=future.result()
            result_With_Recalls.append(result_With_Recall)
    for id,result_With_Recall in enumerate(result_With_Recalls):
        print(id)
        print("注入召回信息的回答结果")
        print(result_With_Recall,"\n\n")
        print("不注入召回信息的回答结果")
        print(result_Without_Recall,"\n\n")
    # return result_With_Recalls,result_Without_Recalls
    return recall_results,result_With_Recalls,result_Without_Recall

if __name__=="__main__":
 query=input("输入你的问题:")
 r_r,r_w_r,r_nw_r=helpfulness_detect(query)
#  for id,r in enumerate(r_w_r):
#      print(id,r)
    
