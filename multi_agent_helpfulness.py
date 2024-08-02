from langchain.prompts import PromptTemplate
import re
import random
from http import HTTPStatus
from requery import requery
import dashscope
import concurrent.futures
import time
def call_with_messages(template,query)->str:
    messages = [
        {'role': 'system', 'content': f"{template}"},
        {'role': 'user', 'content': f"{query}"}]
    response = dashscope.Generation.call(
        'qwen-plus',
        messages=messages,
        # set the random seed, optional, default to 1234 if not set
        seed=random.randint(1, 10000),
        temperature=0.5,
        result_format='message',  # set the result to be "message" format.
    )
    if response.status_code == HTTPStatus.OK:
        output=response["output"]["choices"][0]["message"]["content"]
        # print(output)
        return output
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))

template1="""
请用中文回答,您是一名投票者,请仔细分析信息1和信息2的内容,考虑历史辩论结果,并从**证据来源角度**这个方面判断提供的证据与**问题**{question}是否有关系
如果信息1说明了提供的证据来源，且信息1说明了证据材料中证据的信息对解决问题有帮助，则投票结果为1，否则投票结果为2
同时你需要分析上轮辩论，根据上轮投票者的投票原因分析投票结果是否正确，纠正不正确的投票结果并写在原因中
**输出样例开始位置**
投票结果:1
原因:………………
**输出样例结束位置**

**信息1开始位置**:<p>{message1}</p>**信息1结束位置**

**信息2开始位置**:<p>{message2}</p>**信息2结束位置**

**历史辩论结果**:<p>{historical_debate_results}</p>**历史辩论结果结束**

投票结果不是1就是2,请根据按照输出样例的格式,(注意你只需学习输出样例格式而不是利用输出样例信息回答问题)，输出内容
"""

template2="""
请用中文回答,您是一名投票者,请仔细分析信息1和信息2的内容,考虑历史辩论结果,并从**证据信息文本有效性**上确定哪条信息更能解决这个**问题**{question}
如果信息1说明证据文本信息为正常中文文本信息或英文文本信息则投票结果为1,否则投票为2
同时你需要分析上轮辩论，根据上轮投票者的投票原因分析投票结果是否正确，纠正不正确的投票结果并写在原因中
**输出样例开始位置**
投票结果:1
原因:………………
**输出样例结束位置**

**信息1开始位置**:<p>{message1}</p>**信息1结束位置**

**信息2开始位置**:<p>{message2}</p>**信息2结束位置**

**历史辩论结果**:<p>{historical_debate_results}</p>**历史辩论结果结束**

投票结果不是1就是2,请根据按照输出样例的格式,(注意你只需学习输出样例格式而不是利用输出样例信息回答问题)，输出内容
"""
template3="""
请用中文回答,您是一名投票者,请仔细分析信息1和信息2的内容,考虑历史辩论结果,并从**证据与问题相关性**上确定哪条信息更能解决这个**问题**{question}
如果信息1说明提供的证据材料与问题有关则投票结果为1，否则为投票结果为2。
同时你需要分析上轮辩论，根据上轮投票者的投票原因分析投票结果是否正确，纠正不正确的投票结果并写在原因中
**输出样例开始位置**
投票结果:1
原因:………………
**输出样例结束位置**

**信息1开始位置**:<p>{message1}</p>**信息1结束位置**

**信息2开始位置**:<p>{message2}</p>**信息2结束位置**

**历史辩论结果**:<p>{historical_debate_results}</p>**历史辩论结果结束**

投票结果不是1就是2,请根据按照输出样例的格式,(注意你只需学习输出样例格式而不是利用输出样例信息回答问题)，输出内容
"""
# message1="""1+1=2"""
message2="""人之所以会在悲伤、快乐或者其他强烈的情感体验时哭泣，主要是因为眼泪在生理和心理层面上都扮演着调节情绪的重要角色。

当人们感到悲伤时，哭泣可以释放积聚的情绪压力，有助于恢复内心的平静。另一方面，在幸福或激动的时刻，哭泣可能是因为无法用言语完全表达内心的感受，眼泪作为一种无声的语言，传达了情感的深度。

因此，无论是悲伤还是快乐，哭泣都是一种自然的情感宣泄方式，两者之间的联系在于，都是人类情绪复杂性的体现。"""
message1="""1+1=1"""

def multiAgent_debate_helpfuless(message1:str,message2:str,question:str)->bool:
    historical_debate_results=""
    num1=0
    num2=0
    for turn in range(3):
        prompt_template_with_recall_detect_Source= PromptTemplate(
            input_variables = ["message1","message2","question","historical_debate_results"],
            template = template1
            )
        
        prompt_template_with_recall_detect_Validity = PromptTemplate(
            input_variables = ["message1","message2","question","historical_debate_results"],
            template = template2
        )
        prompt_template_with_recall_detect_Relevance = PromptTemplate(
            input_variables = ["message1","message2","question","historical_debate_results"],
            template = template3
            )
        historical_debate_results+=f"第{turn+1}轮辩论结果\n"
        prompt_template_with_recall_detect_Source=prompt_template_with_recall_detect_Source.format(
                turn=turn,
                message1=message1,
                message2=message2,
                question = question,
                historical_debate_results=historical_debate_results
            )
        prompt_template_with_recall_detect_Consistency =prompt_template_with_recall_detect_Consistency.format(
                turn=turn,
                message1=message1,
                message2=message2,
                question = question,
                historical_debate_results=historical_debate_results
        )
        prompt_template_with_recall_detect_Relevance = prompt_template_with_recall_detect_Relevance.format(
                turn=turn,
                message1=message1,
                message2=message2,
                question = question,
                historical_debate_results=historical_debate_results
        )
        query="请输出结果"
        max_retries = 5
        for attempt in range(max_retries):
            try:
                detect_Source_result = call_with_messages(prompt_template_with_recall_detect_Source, query=query)
                detect_Validity_result = call_with_messages(prompt_template_with_recall_detect_Validity, query=query)
                detect_Relevance_result = call_with_messages(prompt_template_with_recall_detect_Relevance, query=query)
                break
            except Exception as e:
                print(f"捕获到异常：{e}，正在重试，已尝试 {attempt + 1} 次...")
                time.sleep(5) 

        # 使用正则表达式搜索数字
        for agent_result in [detect_Source_result,detect_Validity_result,detect_Relevance_result]:
            pattern = r"投票结果:(\d+)"
            match = re.search(pattern, agent_result)
            print(match)
            if match:
                # 如果找到匹配项，输出数字
                result_number = int(match.group(1))
                print(result_number)
                if result_number==1:
                    num1+=1
                elif result_number==2 :
                    num2+=1
            else:
                print("没有找到数字")
            
        historical_debate_results+="\n"
        print(num1,num2)
        print(historical_debate_results)
        if num1>num2:
            return True
        else:
            return False
    
if __name__=="__main__":
    query=input("输入你的问题:")
    result=multiAgent_debate_helpfuless(message1,message2,query)