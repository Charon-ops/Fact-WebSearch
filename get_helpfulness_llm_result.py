from langchain.prompts import PromptTemplate
from helpfulness_pipeline import helpfulness_pipline
from judge_need import  judge_need
import random
from http import HTTPStatus
import dashscope
template1="""
用中文回答
参考内容{context}
你需要回答用户提出的问题且必须从用户输入后的四个选项中选出一个答案,答案必须从选项中选,输出格式为:选项.选项内容
输出样例:D.……
"""
template2 = """
用中文回答
你需要根据提供的证据来回答用户提出的问题,且必须从用户输入问题后的四个选项中选出一个答案,而不是从证据的选项中选出答案,
答案必须从用户输入的问题选项中选,输出格式为:选项.选项内容
输出样例:D.……
**证据开始位置**
{context}
**证据结束位置**
"""
def call_with_messages(template,query)->str:
    messages = [
        {'role': 'system', 'content': f"{template}"},
        {'role': 'user', 'content': f"{query}"}]
    response = dashscope.Generation.call(
        'qwen-plus',
        messages=messages,
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
def get_helpfulness_llm_result(question,query,option):
    #question既包含问题也包含选项
    #query只包含问题
    #option只包含选项
    judge_result=judge_need(query=query,option=option) 
    if judge_result is not None:
        print("该问题不需要证据")
        prompt=PromptTemplate(template=template1, input_variables=["context"])
        prompt=prompt.format(context=judge_result)
        return call_with_messages(template=prompt, query=question)
    else:
        print("该问题需要证据")
    helpfulness_infos=helpfulness_pipline(query=query,question=question)
    Prompt= PromptTemplate(template=template2, input_variables=["context"])
    Prompt=Prompt.format(context=helpfulness_infos)
    return call_with_messages(template=Prompt, query=question)

if __name__ == '__main__':
    # question=input("请输入你的问题:")
    # query=input("请输入你的问题:")
    # option=input("请输入你的选项:")
    question="""
    女性生殖腺是
    A. 卵巢
    B. 前庭大腺
    C. 前庭球
    D. 乳腺
    """
    query="女性生殖腺是"
    option="""
    A. 卵巢
    B. 前庭大腺
    C. 前庭球
    D. 乳腺
    """
    get_helpfulness_llm_result(question=question,query=query,option=option)
