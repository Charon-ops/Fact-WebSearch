template1 = """
用中文回答问题
你需要将用户输入的选择题改写,**不用回答该题**,将其改写为更简短的问题以适合获取信息
"""
template2 = """
用中文回答
你需判断用户输入是否含有对选项的需求，你只需输出"是"或"否"，**不用回答该题**
**输出样例开始位置**
判断:是
或
判断:否
**输出样例结束位置**
"""
template3 = """
用中文回答
你需要将用户输入的选择题改写,**不用回答该题**,将其问题和选项改写为判断题
**示例1**
输入:
下列四组字中，全是形声字的一组是
A.修约菜苗
B.寐融照哀
C.问娶分笺
D.保禄私空
输出:
1.修约菜苗全是形声字吗？
2.寐融照哀全是形声字吗？
3.问娶分笺全是形声字吗？
4.保禄私空全是形声字吗？
**示例2**
输入:   
下列句中，“是”充当前置宾语的一句是
A.如有不由此者，在執者去，衆以焉殃，是謂小康。
B.子曰：敏而好學，不下恥問，是以謂之文也。
C.是乃其所以千萬臣而無數者也。
D.鑄名器，藏寶財，固民之殄病是待。
输出:
1.如有不由此者，在執者去，衆以焉殃，是謂小康。是“是”充当前置宾语吗？
2.子曰：敏而好學，不下恥問，是以謂之文也。是“是”充当前置宾语吗？
3.是乃其所以千萬臣而無數者也。是“是”充当前置宾语吗？
4.鑄名器，藏寶財，固民之殄病是待。是“是”充当前置宾语吗？
"""
import random
from http import HTTPStatus
import dashscope

def requery(template,query)->str:
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
def judge_requery(question:str,query:str):
    requery_result=requery(query,template1)
    while(True):
        messages = [
        {'role': 'system', 'content': f"{template2}"},
        {'role': 'user', 'content': f"{query}"}]
        response = dashscope.Generation.call(
            'qwen-plus',
            messages=messages,
            # set the random seed, optional, default to 1234 if not set
            seed=random.randint(1, 10000),
            result_format='message',  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            judge_reslut=response["output"]["choices"][0]["message"]["content"]
            print(judge_reslut)
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
        import re
        match = re.search(r':(\w)', judge_reslut)

        if match:
            # 如果找到匹配项，提取并打印结果
            result = match.group(1)
            if  result=="否":
                print("该题不需要改写")
                return requery_result
            elif  result=="是":
                print("该题需要改写")
                return requery(question,template3)
        else:
            print("回答不符规范，请重新回答")
            continue

if __name__ == '__main__':
    query="""
   下列四组字中，全是会意字的一组是
    """
    question=""""
    下列四组字中，全是会意字的一组是
    A.集冰迢逐
    B.凭亦寒罟
    C.莫鱼向闽
    D.牧岩岳泪
    """
    # requery(query=query)
    judge_requery(question=question,query=query)