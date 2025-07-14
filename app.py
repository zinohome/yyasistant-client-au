#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: ibmzhangjun@139.com
@file: app.py.py
@time: 2025/7/13 下午8:15
@desc: 
"""
import asyncio
import base64
import os
import io
import wave
from uuid import uuid4

import numpy as np
import audioop

from chainlit.input_widget import Switch
from config import config_from_dotenv

from realtime import RealtimeClient
from realtime.tools import tools
from utils.logger import logger
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg = config_from_dotenv(os.path.join(BASE_DIR, '.env'), read_from_file=True)

PROFILE_NAME = "健康助手"
PROFILE_ICON = "/public/profileimg/XiaoYan2.png"
PROFILE_DESC = "我是您的健康助手小研，我总是在这里，随时准备帮助您。我能够为您提供多方面、个性化的服务。"
PROFILE_STARTERS = [
    {
        "label": "健康与养生",
        "message": "给我介绍一些健康和养生方面的知识。",
        "icon": "/public/startterimg/chat.png"
    },
    {
        "label": "文艺与文化生活",
        "message": "退休后如何丰富文艺和文化生活？",
        "icon": "/public/startterimg/report.png"
    },
    {
        "label": "日常生活助手",
        "message": "做我的小助手，陪我聊天解闷。",
        "icon": "/public/startterimg/knowledge.png"
    },
    {
        "label": "新技能学习",
        "message": "退休后我可以学哪些新技能，给我推荐几个吧。",
        "icon": "/public/startterimg/doctor.png"
    },
]

# Define a threshold for detecting silence and a timeout for ending a turn
SILENCE_THRESHOLD = (
    3500  # Adjust based on your audio level (e.g., lower for quieter audio)
)
SILENCE_TIMEOUT = 1300.0  # Seconds of silence to consider the turn finished

import chainlit as cl
from utils.yyassistantapiclient import YYAssistantAPIClient


async def setup_openai_realtime():
    """Instantiate and configure the OpenAI Realtime Client"""
    openai_realtime = RealtimeClient(api_key=cfg.OPENAI_API_KEY)
    cl.user_session.set("track_id", str(uuid4()))

    async def handle_conversation_updated(event):
        item = event.get("item")
        delta = event.get("delta")
        """Currently used to stream audio back to the client."""
        if delta:
            # Only one of the following will be populated for any given event
            if "audio" in delta:
                audio = delta["audio"]  # Int16Array, audio added
                await cl.context.emitter.send_audio_chunk(
                    cl.OutputAudioChunk(
                        mimeType="pcm16",
                        data=audio,
                        track=cl.user_session.get("track_id"),
                    )
                )
            if "transcript" in delta:
                transcript = delta["transcript"]  # string, transcript added
                pass
            if "arguments" in delta:
                arguments = delta["arguments"]  # string, function arguments added
                pass

    async def handle_item_completed(item):
        """Used to populate the chat context with transcription once an item is completed."""
        # print(item) # TODO
        pass

    async def handle_conversation_interrupt(event):
        """Used to cancel the client previous audio playback."""
        cl.user_session.set("track_id", str(uuid4()))
        await cl.context.emitter.send_audio_interrupt()

    async def handle_error(event):
        logger.error(event)

    openai_realtime.on("conversation.updated", handle_conversation_updated)
    openai_realtime.on("conversation.item.completed", handle_item_completed)
    openai_realtime.on("conversation.interrupted", handle_conversation_interrupt)
    openai_realtime.on("error", handle_error)

    cl.user_session.set("openai_realtime", openai_realtime)
    coros = [
        openai_realtime.add_tool(tool_def, tool_handler)
        for tool_def, tool_handler in tools
    ]
    await asyncio.gather(*coros)



@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    starters = [
        cl.Starter(label=s["label"], message=s["message"], icon=s["icon"])
        for s in PROFILE_STARTERS
    ]
    return [
        cl.ChatProfile(
            name=PROFILE_NAME,
            icon=PROFILE_ICON,
            markdown_description=PROFILE_DESC,
            starters=starters,
        )
    ]

@cl.on_settings_update
async def settings_update(settings):
    cl.user_session.set("chat_settings", settings)

@cl.on_chat_start
async def start_chat():
    settings = await cl.ChatSettings(
        [
            Switch(id="auto_play_audio", label="自动播放语音", default=True, description="开启后会自动播报助手的语音回复"),
        ]
    ).send()
    await settings_update(settings)
    # 初始化客户端和会话
    base_url = cfg.SERVER_BASE_URL
    client = YYAssistantAPIClient(base_url)  # 请替换为实际的API基础URL
    # 获取默认引擎
    default_engine = cfg.DEFAULT_AGENT_ENGINE
    if not default_engine:
        default_engine = await client.get_default_agent_engine()

    # 创建新会话
    conversation = await client.create_agent_conversation(default_engine, {"input": "开始对话"})
    conversation_id = conversation.get("data", "") if isinstance(conversation, dict) else ""

    # 存储客户端和会话ID到用户会话中
    cl.user_session.set("client", client)
    cl.user_session.set("conversation_id", conversation_id)
    cl.user_session.set("engine_name", default_engine)

    # 初始化 OpenAI Realtime
    await setup_openai_realtime()
    '''
    # 发送欢迎消息
    welcome_msg = f"您好，我是您的健康助手**{PROFILE_NAME}** 😊\n\n"
    welcome_msg += f"{PROFILE_DESC}\n\n"
    welcome_msg += "您可以直接输入问题，也可以点击左侧的快捷问题与我交流～\n\n"
    welcome_msg += "**以下是一些您可以尝试的问题：**\n"
    for idx, s in enumerate(PROFILE_STARTERS, 1):
        welcome_msg += f"{idx}. **{s['label']}**：{s['message']}\n"

    await cl.Message(content=welcome_msg).send()
    '''

@cl.on_message
async def main(message: cl.Message):
    # 从用户会话中获取客户端和会话ID
    client: YYAssistantAPIClient = cl.user_session.get("client")
    conversation_id = cl.user_session.get("conversation_id")
    engine_name = cl.user_session.get("engine_name")

    if not client or not conversation_id:
        await cl.Message(content="会话未初始化，请刷新页面重试。", author="健康助手").send()
        return

    # 读取 ChatSettings 设置
    chat_settings = cl.user_session.get("chat_settings") or {}
    auto_play_audio = chat_settings.get("auto_play_audio", True)  # 默认为True

    # 启动 OpenAI Realtime
    # 输出空消息用于流式token输出
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    logger.info(f"openai_realtime: {openai_realtime}")
    logger.info(f"openai_realtime.is_connected: {openai_realtime.is_connected()}")
    if openai_realtime and openai_realtime.is_connected():
        # TODO: Try image processing with message.elements
        await openai_realtime.send_user_message_content(
            [{"type": "input_text", "text": message.content}]
        )
    else:
        msg = cl.Message(content="", author="健康助手")
        await msg.send()

    # 调用 Agent 推理 API获取流式响应
    try:
        full_response = ""
        # 接收流式响应
        # ------ 新增try锁定generator -------
        stream_gen = client.agent_inference_stream(
            data=message.content,
            conversation_id=conversation_id,
            user_id="chainlit-user"
        )
        async for chunk in stream_gen:
            full_response += chunk
            await msg.stream_token(chunk)
        msg.content = full_response
        await msg.update()

    except Exception as e:
        # 创建新消息显示错误，而不是更新原有消息
        await cl.Message(author="健康助手", content=f"错误: {str(e)}").send()
        raise

@cl.on_audio_start
async def on_audio_start():
    try:
        openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
        await openai_realtime.connect()
        logger.info("Connected to OpenAI realtime")
        # TODO: might want to recreate items to restore context
        # openai_realtime.create_conversation_item(item)
        return True
    except Exception as e:
        await cl.ErrorMessage(
            content=f"Failed to connect to OpenAI realtime: {e}"
        ).send()
        return False

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime.is_connected():
        await openai_realtime.append_input_audio(chunk.data)
    else:
        logger.info("RealtimeClient is not connected")

@cl.on_audio_end
@cl.on_chat_end
@cl.on_stop
async def on_end():
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime and openai_realtime.is_connected():
        await openai_realtime.disconnect()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)