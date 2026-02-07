import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import threading
from queue import Queue
from typing import Optional

load_dotenv()

class AIService:
    def __init__(self):
        self.enable_summary = os.getenv('ENABLE_AI_SUMMARY', 'true').lower() == 'true'
        self.enable_translate = os.getenv('ENABLE_AI_TRANSLATE', 'true').lower() == 'true'
        self.enable_chat = os.getenv('ENABLE_AI_CHAT', 'true').lower() == 'true'
        self.max_concurrent = int(os.getenv('MAX_CONCURRENT_REQUESTS', '1'))
        
        self.request_queue = Queue()
        self.active_requests = 0
        self.lock = threading.Lock()
    
    def _get_client(self, api_key: Optional[str] = None):
        if api_key and api_key != 'your_api_key_here':
            return ZhipuAI(api_key=api_key)
        return None
    
    def is_enabled(self, api_key: Optional[str] = None):
        client = self._get_client(api_key)
        return client is not None
    
    def test_api_key(self, api_key: Optional[str] = None) -> dict:
        try:
            client = self._get_client(api_key)
            if not client:
                return {
                    'valid': False,
                    'error': 'API Key is empty or invalid'
                }
            
            response = client.chat.completions.create(
                model='glm-4-flash',
                messages=[
                    {
                        'role': 'user',
                        'content': 'test'
                    }
                ],
                max_tokens=10
            )
            
            if response and response.choices:
                return {
                    'valid': True,
                    'message': 'API Key is valid'
                }
            else:
                return {
                    'valid': False,
                    'error': 'API Key seems invalid'
                }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _acquire_slot(self):
        with self.lock:
            if self.active_requests < self.max_concurrent:
                self.active_requests += 1
                return True
            return False
    
    def _release_slot(self):
        with self.lock:
            self.active_requests -= 1
    
    async def generate_summary(self, text: str, api_key: Optional[str] = None) -> Optional[str]:
        if not self.enable_summary:
            return None
        
        client = self._get_client(api_key)
        if not client:
            return None
        
        try:
            response = client.chat.completions.create(
                model='glm-4-flash',
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的文档摘要助手。请为给定的文档内容生成简洁准确的摘要，突出重点信息。'
                    },
                    {
                        'role': 'user',
                        'content': f'请为以下文档内容生成摘要：\n\n{text[:4000]}'
                    }
                ],
                temperature=0.7,
                max_tokens=20000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f'生成摘要失败: {str(e)}')
            return None
    
    async def translate_text(self, text: str, target_lang: str = '中文', api_key: Optional[str] = None) -> Optional[str]:
        if not self.enable_translate:
            return None
        
        client = self._get_client(api_key)
        if not client:
            return None
        
        try:
            response = client.chat.completions.create(
                model='glm-4-flash',
                messages=[
                    {
                        'role': 'system',
                        'content': f'你是一个专业的翻译助手。请将文本翻译成{target_lang}，保持原文的格式和结构。'
                    },
                    {
                        'role': 'user',
                        'content': f'请将以下文本翻译成{target_lang}：\n\n{text[:3000]}'
                    }
                ],
                temperature=0.3,
                max_tokens=20000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f'翻译失败: {str(e)}')
            return None
    
    async def chat_with_document(self, question: str, context: str, api_key: Optional[str] = None) -> Optional[str]:
        if not self.enable_chat:
            return None
        
        client = self._get_client(api_key)
        if not client:
            return None
        
        try:
            response = client.chat.completions.create(
                model='glm-4-flash',
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个智能文档助手，可以根据文档内容回答用户的问题。请基于提供的文档内容准确回答，不要编造信息。'
                    },
                    {
                        'role': 'user',
                        'content': f'文档内容：\n{context[:3000]}\n\n用户问题：{question}\n\n请根据文档内容回答这个问题。'
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f'AI 问答失败: {str(e)}')
            return None
    
    def chat_with_document_stream(self, question: str, context: str, api_key: Optional[str] = None):
        if not self.enable_chat:
            return None
        
        client = self._get_client(api_key)
        if not client:
            return None
        
        try:
            response = client.chat.completions.create(
                model='glm-4-flash',
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个智能文档助手，可以根据文档内容回答用户的问题。请基于提供的文档内容准确回答，不要编造信息。'
                    },
                    {
                        'role': 'user',
                        'content': f'文档内容：\n{context[:3000]}\n\n用户问题：{question}\n\n请根据文档内容回答这个问题。'
                    }
                ],
                temperature=0.7,
                max_tokens=100000,
                stream=True
            )
            return response
        except Exception as e:
            print(f'AI 问答流式输出失败: {str(e)}')
            return None

ai_service = AIService()
