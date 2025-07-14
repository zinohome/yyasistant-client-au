#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: ibmzhangjun@139.com
@file: yyassistantapiclient.py
@time: 2025/7/13 下午6:06
@desc: 
"""
import os
from config import config_from_dotenv
from utils.logger import logger
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = config_from_dotenv(os.path.join(BASE_DIR, '.env'), read_from_file=True)

import httpx
import asyncio

class YYAssistantAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(int(cfg.HTTPX_TIMEOUT)))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def close(self):
        """手动关闭客户端连接"""
        await self.client.aclose()

    async def get_asr_engine_list(self):
        url = f"{self.base_url}/yyh/asr/v0/engine"
        response = await self.client.get(url)
        return response.json()

    async def asr_inference_wav(self, data, user_id="tester", request_id="", cookie="", **kwargs):
        url = f"{self.base_url}/yyh/asr/v0/engine"
        headers = {
            "User-Id": user_id,
            "Request-Id": request_id,
            "Cookie": cookie
        }
        payload = {
            "data": data,
            **kwargs
        }
        response = await self.client.post(url, headers=headers, json=payload)
        return response.json()

    async def get_default_asr_engine(self):
        url = f"{self.base_url}/yyh/asr/v0/engine/default"
        response = await self.client.get(url)
        data = response.json()

        # 检查响应中是否包含 ['data']['name']
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict) and 'name' in data['data']:
            return data['data']['name']
        else:
            return "Tencent-API"

    async def get_asr_engine_param(self, engine):
        url = f"{self.base_url}/yyh/asr/v0/engine/{engine}"
        response = await self.client.get(url)
        return response.json()

    async def asr_inference_mp3(self, file_path, engine, audio_type, config, sample_rate, sample_width, user_id="tester",
                          request_id="", cookie=""):
        url = f"{self.base_url}/yyh/asr/v0/engine/file"
        headers = {
            "User-Id": user_id,
            "Request-Id": request_id,
            "Cookie": cookie
        }
        with open(file_path, 'rb') as file:
            files = {
                "file": file
            }
            data = {
                "engine": engine,
                "type": audio_type,
                "config": config,
                "sampleRate": sample_rate,
                "sampleWidth": sample_width
            }
            response = await self.client.post(url, headers=headers, files=files, data=data)
        return response.json()

    async def get_tts_engine_list(self):
        url = f"{self.base_url}/yyh/tts/v0/engine"
        response = await self.client.get(url)
        return response.json()

    async def tts_inference(self, data, user_id="tester", request_id="", cookie="", **kwargs):
        url = f"{self.base_url}/yyh/tts/v0/engine"
        headers = {
            "User-Id": user_id,
            "Request-Id": request_id,
            "Cookie": cookie
        }
        payload = {
            "data": data,
            **kwargs
        }
        response = await self.client.post(url, headers=headers, json=payload)
        return response.json()

    async def get_default_tts_engine(self):
        url = f"{self.base_url}/yyh/tts/v0/engine/default"
        response = await self.client.get(url)
        data = response.json()

        # 检查响应中是否包含 ['data']['name']
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict) and 'name' in data['data']:
            return data['data']['name']
        else:
            return "Tencent-API"

    async def get_tts_engine_voice_list(self, engine):
        url = f"{self.base_url}/yyh/tts/v0/engine/{engine}/voice"
        response = await self.client.get(url)
        return response.json()

    async def get_tts_engine_param(self, engine):
        url = f"{self.base_url}/yyh/tts/v0/engine/{engine}"
        response = await self.client.get(url)
        return response.json()

    async def get_llm_engine_list(self):
        url = f"{self.base_url}/yyh/llm/v0/engine"
        response = await self.client.get(url)
        return response.json()

    async def llm_inference(self, data, user_id="tester", request_id="", cookie="", **kwargs):
        url = f"{self.base_url}/yyh/llm/v0/engine"
        headers = {
            "User-Id": user_id,
            "Request-Id": request_id,
            "Cookie": cookie
        }
        payload = {
            "data": data,
            **kwargs
        }
        response = await self.client.post(url, headers=headers, json=payload)
        return response.json()

    async def get_default_llm_engine(self):
        url = f"{self.base_url}/yyh/llm/v0/engine/default"
        response = await self.client.get(url)
        return response.json()

    async def get_llm_engine_param(self, engine):
        url = f"{self.base_url}/yyh/llm/v0/engine/{engine}"
        response = await self.client.get(url)
        return response.json()

    async def get_agent_engine_list(self):
        url = f"{self.base_url}/yyh/agent/v0/engine"
        response = await self.client.get(url)
        return response.json()

    async def agent_inference(self, data, user_id="tester", request_id="", cookie="", conversation_id="", **kwargs):
        url = f"{self.base_url}/yyh/agent/v0/engine"
        headers = {
            "User-Id": user_id,
            "Request-Id": request_id,
            "Cookie": cookie
        }
        payload = {
            "data": data,
            "conversation_id": conversation_id,
            **kwargs
        }
        '''
        response = await self.client.post(url, headers=headers, json=payload)
        logger.info(f"Agent Inference Response: {response}")
        return response
        '''


        # 使用流式请求
        async with self.client.stream("POST", url, headers=headers, json=payload) as response:
            # 检查响应状态码
            response.raise_for_status()

            # 初始化结果列表和当前消息
            results = []
            current_message = ""
            current_event_type = None

            # 异步迭代响应流的每个部分
            async for chunk in response.aiter_text():
                # 处理每一行数据
                lines = chunk.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        # 空行忽略
                        continue
                    # 解析字段
                    if line.startswith("event: "):
                        # 新事件开始
                        # 如果之前有累积的TEXT消息，先添加到结果
                        if current_event_type == "TEXT" and current_message:
                            results.append(current_message)
                            current_message = ""
                        current_event_type = line[7:].strip()
                    elif line.startswith("data: ") and current_event_type is not None:
                        data_part = line[6:].strip()
                        # 只处理TEXT事件，忽略其他类型
                        if current_event_type == "TEXT" and data_part:
                            current_message += data_part

            # 添加最后可能剩余的消息
            if current_event_type == "TEXT" and current_message:
                results.append(current_message)

            return results


    async def agent_inference_stream(self, data, user_id="tester", request_id="", cookie="", conversation_id="", **kwargs):
        url = f"{self.base_url}/yyh/agent/v0/engine"
        headers = {
            "User-Id": user_id,
            "Request-Id": request_id,
            "Cookie": cookie
        }
        payload = {
            "data": data,
            "conversation_id": conversation_id,
            **kwargs
        }

        try:
            # 创建独立的客户端会话，确保可以单独关闭
            async with httpx.AsyncClient(timeout=httpx.Timeout(int(cfg.HTTPX_TIMEOUT))) as session:
                async with session.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()

                    try:
                        async for chunk in response.aiter_text():
                            lines = chunk.strip().split('\n')
                            current_event = None
                            current_content = ""

                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue

                                if line.startswith("event: "):
                                    if current_event == "TEXT" and current_content:
                                        yield current_content
                                        current_content = ""
                                    current_event = line[7:].strip()

                                    if current_event == "DONE":
                                        if current_content:
                                            yield current_content
                                        return

                                elif line.startswith("data: ") and current_event == "TEXT":
                                    current_content += line[6:].replace("\\n", "\n").replace('\n', '  \n')  # 恢复换行符，不要去掉空格

                            # 发送当前块的累积内容
                            if current_event == "TEXT" and current_content:
                                yield current_content

                    finally:
                        # 确保流被正确关闭
                        if not response.is_closed:
                            await response.aclose()

        except httpx.HTTPStatusError as http_err:
            logger.error(f"HTTP返回失败 {http_err.response.status_code}: {http_err}")
        except httpx.RequestError as req_err:
            logger.error(f"请求连接异常: {req_err}")
        except asyncio.CancelledError:
            # 调用方中断时，优雅释放，不需要raise
            logger.info("agent_inference_stream 被任务取消")
            return
        except GeneratorExit:
            # 调用方强制终止生成器
            logger.info("agent_inference_stream 被生成器终止，资源已清理")
            return
        except Exception as e:
            logger.error(f"未知异常: {e}")

    async def get_default_agent_engine(self):
        url = f"{self.base_url}/yyh/agent/v0/engine/default"
        response = await self.client.get(url)
        data = response.json()

        # 检查响应中是否包含 ['data']['name']
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict) and 'name' in data['data']:
            return data['data']['name']
        else:
            return "Dify"

    async def get_agent_engine_param(self, engine):
        url = f"{self.base_url}/yyh/agent/v0/engine/{engine}"
        response = await self.client.get(url)
        return response.json()

    async def create_agent_conversation(self, engine, data, user_id="tester", request_id="", cookie=""):
        url = f"{self.base_url}/yyh/agent/v0/engine/{engine}"
        headers = {
            "User-Id": user_id,
            "Request-Id": request_id,
            "Cookie": cookie
        }
        payload = {
            "data": data
        }
        response = await self.client.post(url, headers=headers, json=payload)
        return response.json()


# 使用示例
if __name__ == "__main__":
    base_url = cfg.SERVER_BASE_URL  # 替换为实际的API基础URL

    '''
    async def main():
        async with YYAssistantAPIClient(base_url) as client:
            # 获取ASR引擎列表
            asr_engine_list = await client.get_asr_engine_list()
            logger.info(f"ASR Engine List: {asr_engine_list}")
            # 执行ASR推理（wav二进制）
            # 示例数据，根据实际情况替换
            asr_data = "your-asr-data"
            asr_result = await client.asr_inference_wav(asr_data)
            logger.info(f"ASR Inference Result: {asr_result}")

            # 获取 Agent 引擎列表
            default_engine = await client.get_default_agent_engine()
            logger.info(f"Agent Default Engine: {default_engine}")
            # 创建会话
            conversation_id = await client.create_agent_conversation(
                engine=default_engine, data={"input": "你好"}
            )
            logger.info(f"Agent Conversation ID: {conversation_id}")
            # 执行推理
            async for chunk in client.agent_inference_stream(data="今天青岛的天气如何？",conversation_id=conversation_id['data']):
                print("Agent 回复:",chunk)

    asyncio.run(main())
    
            '''
