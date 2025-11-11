"""
vLLM 客户端封装 - 支持 SSH 隧道环境
提供 requests 和 OpenAI SDK 两种实现方式

使用方法:
    # 方式1: requests 后端（推荐，最稳定）
    from vllm_client import VLLMClient
    client = VLLMClient(backend='requests')
    response = client.chat("你好")
    
    # 方式2: OpenAI 后端（支持流式输出）
    client = VLLMClient(backend='openai')
    for chunk in client.chat_stream("讲个故事"):
        print(chunk, end="", flush=True)

作者: AI Assistant & 用户实践总结
日期: 2025-10-05
"""

import requests
from openai import OpenAI
import httpx
from typing import List, Dict, Iterator, Optional, Literal
import json


class VLLMClient:
    """
    vLLM 统一客户端
    支持两种后端：'requests'（推荐用于稳定性）或 'openai'（推荐用于功能完整性）
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:9000",
        api_key: str = "muyu",
        # model: str = "Qwen3-4B",
        model: str = "Medical_Qwen3_8B_Large_Language_Model",
        backend: Literal['requests', 'openai'] = 'requests',
        timeout: float = 120.0
    ):
        """
        初始化客户端
        
        Args:
            base_url: vLLM API 服务地址
            api_key: API 密钥
            model: 模型名称
            backend: 后端实现 ('requests' 或 'openai')
            timeout: 请求超时时间（秒）
        
        Example:
            >>> client = VLLMClient(backend='requests')
            >>> client = VLLMClient(backend='openai')
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.backend = backend
        self.timeout = timeout
        
        if backend == 'openai':
            # OpenAI SDK 后端（需要特殊配置以支持 SSH 隧道）
            # 关键：四项配置缺一不可！
            http_client = httpx.Client(
                timeout=timeout,
                limits=httpx.Limits(
                    max_keepalive_connections=0,  # 不保持长连接
                    max_connections=100,           # 最大连接数
                    keepalive_expiry=0             # 连接立即过期
                ),
                transport=httpx.HTTPTransport(retries=0)  # 禁用重试
            )
            self._openai_client = OpenAI(
                base_url=f"{base_url}/v1",
                api_key=api_key,
                http_client=http_client
            )
        else:
            # requests 后端（默认，最稳定）
            self._headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
    
    def chat(
        self,
        message: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        **kwargs
    ) -> str:
        """
        简单对话接口
        
        Args:
            message: 用户输入
            max_tokens: 最大生成token数
            temperature: 温度参数（0-2）
            top_p: top_p采样参数（0-1）
            **kwargs: 其他API参数
        
        Returns:
            模型回复内容
        
        Example:
            >>> client = VLLMClient()
            >>> response = client.chat("你好，请介绍一下你自己")
            >>> print(response)
        """
        messages = [{"role": "user", "content": message}]
        return self.chat_with_history(messages, max_tokens, temperature, top_p, **kwargs)
    
    def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        **kwargs
    ) -> str:
        """
        多轮对话接口
        
        Args:
            messages: 对话历史列表，格式:
                [{"role": "user", "content": "..."},
                 {"role": "assistant", "content": "..."}]
            max_tokens: 最大生成token数
            temperature: 温度参数
            top_p: top_p采样参数
            **kwargs: 其他API参数
        
        Returns:
            模型回复内容
        
        Example:
            >>> messages = [
            ...     {"role": "user", "content": "你好"},
            ...     {"role": "assistant", "content": "你好！"},
            ...     {"role": "user", "content": "你是谁？"}
            ... ]
            >>> response = client.chat_with_history(messages)
        """
        if self.backend == 'openai':
            completion = self._openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            return completion.choices[0].message.content
        else:
            url = f"{self.base_url}/v1/chat/completions"
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                **kwargs
            }
            response = requests.post(
                url,
                headers=self._headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
    
    def chat_stream(
        self,
        message: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        **kwargs
    ) -> Iterator[str]:
        """
        流式对话接口（实时输出）
        注意：仅 OpenAI 后端支持
        
        Args:
            message: 用户输入
            max_tokens: 最大生成token数
            temperature: 温度参数
            top_p: top_p采样参数
            **kwargs: 其他API参数
        
        Yields:
            每次生成的文本片段
        
        Raises:
            NotImplementedError: 如果使用 requests 后端
        
        Example:
            >>> client = VLLMClient(backend='openai')
            >>> for chunk in client.chat_stream("讲个故事"):
            ...     print(chunk, end="", flush=True)
        """
        if self.backend != 'openai':
            raise NotImplementedError(
                "流式输出仅支持 'openai' 后端。"
                "请使用: VLLMClient(backend='openai')"
            )
        
        stream = self._openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": message}],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True,
            **kwargs
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def chat_stream_with_history(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        **kwargs
    ) -> Iterator[str]:
        """
        流式多轮对话接口
        注意：仅 OpenAI 后端支持
        
        Args:
            messages: 对话历史列表
            max_tokens: 最大生成token数
            temperature: 温度参数
            top_p: top_p采样参数
            **kwargs: 其他API参数
        
        Yields:
            每次生成的文本片段
        
        Raises:
            NotImplementedError: 如果使用 requests 后端
        """
        if self.backend != 'openai':
            raise NotImplementedError(
                "流式输出仅支持 'openai' 后端。"
                "请使用: VLLMClient(backend='openai')"
            )
        
        stream = self._openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True,
            **kwargs
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            模型ID列表
        
        Example:
            >>> client = VLLMClient()
            >>> models = client.get_models()
            >>> print(models)
        """
        if self.backend == 'openai':
            models = self._openai_client.models.list()
            return [model.id for model in models.data]
        else:
            url = f"{self.base_url}/v1/models"
            response = requests.get(url, headers=self._headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return [model['id'] for model in result['data']]
    
    def close(self):
        """关闭客户端连接"""
        if self.backend == 'openai':
            self._openai_client.close()
    
    def __enter__(self):
        """支持上下文管理器"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动关闭连接"""
        self.close()


# ============ 使用示例 ============

def example_basic():
    """示例1：基础使用"""
    print("=" * 60)
    print("示例1：基础对话（requests 后端）")
    print("=" * 60)
    
    client = VLLMClient(backend='requests')
    response = client.chat("你好，请介绍一下你自己", max_tokens=200)
    print(f"回复: {response}\n")


def example_multi_turn():
    """示例2：多轮对话"""
    print("=" * 60)
    print("示例2：多轮对话")
    print("=" * 60)
    
    client = VLLMClient(backend='requests')
    messages = [
        {"role": "user", "content": "你好，我叫小明"},
        {"role": "assistant", "content": "你好小明！很高兴认识你。"},
        {"role": "user", "content": "我刚才告诉你我叫什么？"}
    ]
    response = client.chat_with_history(messages, max_tokens=100)
    print(f"回复: {response}\n")


def example_stream():
    """示例3：流式输出"""
    print("=" * 60)
    print("示例3：流式输出（OpenAI 后端）")
    print("=" * 60)
    
    client = VLLMClient(backend='openai')
    print("回复: ", end="", flush=True)
    for chunk in client.chat_stream("用一句话介绍Python编程语言", max_tokens=200):
        print(chunk, end="", flush=True)
    print("\n")
    client.close()


def example_temperature():
    """示例4：调整温度参数"""
    print("=" * 60)
    print("示例4：温度参数对比")
    print("=" * 60)
    
    client = VLLMClient(backend='requests')
    
    # 低温度（更确定）
    response1 = client.chat(
        "1+1等于几？",
        max_tokens=50,
        temperature=0.1
    )
    print(f"低温度(0.1): {response1}")
    
    # 高温度（更随机）
    response2 = client.chat(
        "1+1等于几？",
        max_tokens=50,
        temperature=1.5
    )
    print(f"高温度(1.5): {response2}\n")


def example_context_manager():
    """示例5：上下文管理器"""
    print("=" * 60)
    print("示例5：上下文管理器（自动关闭）")
    print("=" * 60)
    
    with VLLMClient(backend='requests') as client:
        response = client.chat("Python的主要特点是什么？", max_tokens=200)
        print(f"回复: {response}\n")


def example_models():
    """示例6：获取模型列表"""
    print("=" * 60)
    print("示例6：获取可用模型")
    print("=" * 60)
    
    client = VLLMClient(backend='requests')
    models = client.get_models()
    print(f"可用模型: {models}\n")


def main():
    """运行所有示例"""
    try:
        example_basic()
        example_multi_turn()
        example_stream()
        example_temperature()
        example_context_manager()
        example_models()
        
        print("=" * 60)
        print("✅ 所有示例运行完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n提示：请确保：")
        print("1. vLLM 服务已启动")
        print("2. SSH 隧道已建立")
        print("3. 端口 9000 可访问")


if __name__ == "__main__":
    main()
