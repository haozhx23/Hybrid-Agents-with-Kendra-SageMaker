
from langchain.agents import Tool
from langchain.tools import BaseTool
from langchain import PromptTemplate, LLMChain
from langchain.agents import BaseSingleActionAgent, AgentOutputParser, LLMSingleActionAgent, AgentExecutor
from typing import List, Tuple, Any, Union, Optional, Type
from langchain.schema import AgentAction, AgentFinish
from langchain.prompts import StringPromptTemplate
from langchain.callbacks.manager import CallbackManagerForToolRun
import re
from langchain.memory import ConversationBufferWindowMemory

class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        
        llm_output = llm_output.strip()
        llm_output = llm_output.replace('\n', ' ')
        
        
        f_llm_output = llm_output
        for c in "\n.-:?;,<{[>}]!#@$%*，。？！":
            f_llm_output = f_llm_output.replace(c,' ')
        
        print('-DD-CustomOutputParser-f_llm_output: ', f_llm_output)
        match = re.match(r'^[\s\w]*(WebSearch)\(([^\)]+)\)', f_llm_output, re.DOTALL)
        print('-DD-CustomOutputParser-match: ', match)
        

        if not match:
            return AgentFinish(
                return_values={"output": llm_output.strip()},
                log=llm_output,
            )
        else:
            print('-DD-CustomOutputParser-match: ', 'True')
            action = match.group(1).strip()
            action_input = match.group(2).strip()
            
            print('-DD-CustomOutputParser-action: ', action)
            print('-DD-CustomOutputParser-action_input: ', action_input)
            
            return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]
    
    # input_variables=["related_content","tool_name", "input", "intermediate_steps"]

    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        
        print('-DD-intermediate_steps: ',intermediate_steps)
        
        if len(intermediate_steps) == 0:
            role = "固定任务的机器人"
            background_infomation = "\n"
            answer_format = "如果没有或者缺失必要的相关信息，请你只回答\"WebSearch('搜索词')\"，并将'搜索词'替换为你认为需要搜索的关键词"
            
        else:
            role = "AI助手"
            background_infomation = "\n\n你还有这些已知信息作为参考：\n\n"
            action, observation = intermediate_steps[0]
            background_infomation += f"{observation}\n"
            answer_format = '''如果没有或者缺失必要的相关信息，请你如实回答\"不知道\"，除此之外不要回答其他任何内容'''
        
        kwargs["role"] = role
        kwargs["background_infomation"] = background_infomation
        # kwargs["question_guide"] = question_guide
        kwargs["answer_format"] = answer_format

        formated_prompt_temp = self.template.format(**kwargs)
        print('-DD-formated_prompt_temp: ', formated_prompt_temp)
        return formated_prompt_temp


class CustomExecutor:


    def __init__(self, llm, retriever=None, websearcher=None, kendra_chain=None, verbose=True):
        self.llm = llm
        self.retriever = retriever
        self.websearcher = websearcher
        self.kendra_chain = kendra_chain
        
        agent_template = '''现在你是一个{role}。这里有一些已知信息：
        {related_content}
        {background_infomation}
        Instruction: 只能基于以上提供的已知信息，回答问题“{input}”。{answer_format}。下面请回答我上面提出的问题。
        解答:'''
        
        # 基于以上提供的信息和你自己的知识，请给问题“{input}”一个详细的解答。{answer_format}
        # 基于以上提供的信息和你自己的知识，请给问题“{input}”一个详细的解答。{answer_format}。下面请回答我上面提出的问题。

        # tools = [
        #     Tool(
        #         description="useful for when you need to answer questions about current events"
        #     ),
        #     Tool(
        #         description="Useful for general questions about how to do things and for details on interesting topics. Input should be a fully formed question."
        #     )
        # ]
        
        tools = []
        
        if self.websearcher:
            tools.append(
                Tool.from_function(
                        # func=WebSearch.search,
                        func=websearcher.search,
                        name=websearcher.NAME,
                        description=websearcher.DESC
                    )
            )

        prompt = CustomPromptTemplate(template=agent_template,
                                      tools=tools,
                                      input_variables=["related_content",
                                                       "tool_name", 
                                                       "input", 
                                                       "intermediate_steps"])

        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Define the memory for the agent
        # agent_memory = ConversationBufferWindowMemory(k=2)

        output_parser = CustomOutputParser()

        self.tool_names = [tool.name for tool in tools]

        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["\nObservation:"],
            allowed_tools=self.tool_names
        )

        self.agent_executor = AgentExecutor.from_agent_and_tools(
                                agent=agent,
                                tools=tools,
                                verbose=verbose
                                # memory=agent_memory
                                )


    def query(self, query: str = ""):
        related_content = []
        
        if self.retriever:
            related_content = self.retriever.get_relevant_documents(query)
        
        if self.kendra_chain:
            # related_content = self.kendra_chain.kendra_chain_qa(query)
            related_content = self.kendra_chain.get_chain_QA(query)
        
        result = self.agent_executor.run(related_content=related_content, 
                                         input=query,
                                         tool_name=self.tool_names
                                        )
        return result
