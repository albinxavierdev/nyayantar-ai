"""
Custom OpenRouter LLM implementation for LlamaIndex
"""
import os
import json
import requests
from typing import Any, Dict, List, Optional, Sequence, cast
from llama_index.core.llms import CustomLLM, CompletionResponse, CompletionResponseGen, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from pydantic import Field


class OpenRouterLLM(CustomLLM):
    """Custom LLM implementation for OpenRouter API"""
    
    model: str = Field(default="x-ai/grok-4-fast:free", description="OpenRouter model name")
    api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    api_base: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    max_tokens: int = Field(default=4096, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    context_window: int = Field(default=4096, description="Context window size")
    provider_order: List[str] = Field(default_factory=lambda: ["x-ai", "openai", "anthropic", "google"], description="Provider order")
    
    def __init__(
        self,
        model: str = "x-ai/grok-4-fast:free",
        api_key: Optional[str] = None,
        api_base: str = "https://openrouter.ai/api/v1",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        context_window: int = 4096,
        provider_order: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize OpenRouter LLM"""
        # Set default values
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
        if provider_order is None:
            provider_order = ["x-ai", "openai", "anthropic", "google"]
            
        if not api_key:
            raise ValueError("OpenRouter API key is required")
            
        super().__init__(
            model=model,
            api_key=api_key,
            api_base=api_base,
            max_tokens=max_tokens,
            temperature=temperature,
            context_window=context_window,
            provider_order=provider_order,
            **kwargs
        )
    
    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata"""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.max_tokens,
            is_chat_model=True,
            is_function_calling_model=False,
            model_name=self.model,
        )
    
    def _make_request(self, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
        """Make request to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "RAG-SaaS"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": stream,
            "extra_body": {
                "provider": {
                    "order": self.provider_order
                }
            }
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise ValueError(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def _convert_messages_to_openai_format(self, messages: Sequence[ChatMessage]) -> List[Dict[str, str]]:
        """Convert LlamaIndex messages to OpenAI format"""
        openai_messages = []
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                openai_messages.append({"role": "system", "content": message.content})
            elif message.role == MessageRole.USER:
                openai_messages.append({"role": "user", "content": message.content})
            elif message.role == MessageRole.ASSISTANT:
                openai_messages.append({"role": "assistant", "content": message.content})
        return openai_messages
    
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete a prompt"""
        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages)
        
        content = response["choices"][0]["message"]["content"]
        return CompletionResponse(text=content)
    
    @llm_completion_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatMessage:
        """Chat with the model"""
        openai_messages = self._convert_messages_to_openai_format(messages)
        response = self._make_request(openai_messages)
        
        content = response["choices"][0]["message"]["content"]
        return ChatMessage(role=MessageRole.ASSISTANT, content=content)
    
    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        """Stream complete a prompt"""
        messages = [{"role": "user", "content": prompt}]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "RAG-SaaS"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
            "extra_body": {
                "provider": {
                    "order": self.provider_order
                }
            }
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            raise ValueError(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        def generate() -> CompletionResponseGen:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield CompletionResponse(text=delta['content'])
                        except json.JSONDecodeError:
                            continue
        
        return generate()
    
    @llm_completion_callback()
    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> CompletionResponseGen:
        """Stream chat with the model"""
        openai_messages = self._convert_messages_to_openai_format(messages)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "RAG-SaaS"
        }
        
        data = {
            "model": self.model,
            "messages": openai_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
            "extra_body": {
                "provider": {
                    "order": self.provider_order
                }
            }
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            raise ValueError(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        def generate() -> CompletionResponseGen:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield CompletionResponse(text=delta['content'])
                        except json.JSONDecodeError:
                            continue
        
        return generate()
