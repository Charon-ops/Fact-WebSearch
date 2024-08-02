from helpfulness_detect import helpfulness_detect
from multi_agent_helpfulness import multiAgent_debate_helpfuless
from typing import List
import concurrent.futures


def mul_judge(recall_info,result_With_Recall,result_Without_Recall,question):
    if(multiAgent_debate_helpfuless(result_With_Recall,result_Without_Recall,question)==True):
        return result_With_Recall
    else:
        print(recall_info, "is not helpful")
def helpfulness_pipline(query,question)->str:
    helpfulness_infos=[]
    recall_infos,result_With_Recalls,result_Without_Recall=helpfulness_detect(query=query,question=question)
    futures=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(len(recall_infos)):    
            future = executor.submit(
                    mul_judge,
                    recall_infos[i],
                    result_With_Recalls[i],
                    result_Without_Recall,
                    question=query
                )
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            result=future.result()
            if result is not None:
                helpfulness_infos.append(result)
    Final_help_result=""
    for id,helpfulness_info in enumerate(helpfulness_infos):
        Final_help_result+=f"第{id+1}个证据\n"+helpfulness_info+"\n"
    print(Final_help_result)
    return Final_help_result
if __name__ == "__main__":
    query=input("请输入查询:")
    helpfulness_pipline(query=query)