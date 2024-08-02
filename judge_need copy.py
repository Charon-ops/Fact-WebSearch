from requery import requery
import random
from http import HTTPStatus
import dashscope
from langchain.prompts import PromptTemplate

def ans(query)->str:
    messages = [
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
def judge(ans_result,option):
    template="""
    用中文回答
    你是一名判断者,接下来你将判断用户输入是否包含以下四个选项中的一个,或是否可转换为其中的某个选项，而不是回答他
    **输出样例开始位置**
    判断:是
    或
    判断:否
    **输出样例结束位置**
    {option}
    """
    template= PromptTemplate(input_variables=["option"], template=template)
    prompt = template.format(option=option)
    messages = [
        {'role': 'system', 'content': f"{prompt}"},
        {'role': 'user', 'content': f"{ans_result}"}]
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

def judge_need(query,option)->bool:
    #query仅包含问题,不包含选项
    ans_result=ans(query)
    while(True):
        judge_result=judge(ans_result,option)
        if judge_result is None:
            return None
        else:
            import re
            match = re.search(r':(\w)', judge_result)

            if match:
                # 如果找到匹配项，提取并打印结果
                result = match.group(1)
                if  result=="是":
                    return ans_result
                elif  result=="否":
                    return None
            else:
                print("回答不符规范，请重新回答")
                continue
        
if __name__ == '__main__':
    query=input("请输入问题:")
    # print(judge_need(query=query))