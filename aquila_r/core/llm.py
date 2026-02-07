"""
LLM Client for Aquila-R.

Handles interactions with Large Language Models, supporting:
- OpenAI
- Ollama (Open Source / Local)
- Local (OpenAI-compatible)
- Anthropic
- Google

Prioritizes research integrity by using low temperature and
system prompts that discourage hallucination.
"""

import os
import json
import httpx
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from enum import Enum
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from aquila_r.core.config import LLMProvider, LLMConfig


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class LLMClient:
    """
    Unified client for LLM interactions.
    
    Abstracts away provider differences and enforces
    configuration settings (temperature, timeouts).
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize LLM client.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self.provider = config.provider
        self.api_key = config.get_api_key()
        self.base_url = config.api_base
        
        # Set defaults for local providers if not specified
        if self.provider == LLMProvider.OLLAMA and not self.base_url:
            self.base_url = "http://localhost:11434/api"
        elif self.provider == LLMProvider.LOCAL and not self.base_url:
            self.base_url = "http://localhost:1234/v1"  # Common for LM Studio
            
        self.timeout = httpx.Timeout(config.timeout)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_output: bool = False,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            json_output: Whether to force JSON output
            temperature: Override configured temperature
            
        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.config.temperature
        
        if self.provider == LLMProvider.OLLAMA:
            return await self._generate_ollama(prompt, system_prompt, json_output, temp)
        elif self.provider == LLMProvider.OPENAI or self.provider == LLMProvider.LOCAL:
            return await self._generate_openai(prompt, system_prompt, json_output, temp)
        elif self.provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(prompt, system_prompt, json_output, temp)
        elif self.provider == LLMProvider.GOOGLE:
            # Placeholder for Google implementation
            raise NotImplementedError("Google provider not yet implemented")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        json_output: bool,
        temperature: float,
    ) -> str:
        """Generate using Ollama API."""
        url = f"{self.base_url}/generate"
        
        # Construct full prompt if system prompt provided
        # Ollama supports 'system' parameter in /api/generate
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": self.config.max_tokens,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if json_output:
            payload["format"] = "json"
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except httpx.HTTPError as e:
                raise LLMError(f"Ollama API error: {str(e)}")

    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        json_output: bool,
        temperature: float,
    ) -> str:
        """Generate using OpenAI-compatible API."""
        url = f"{self.base_url or 'https://api.openai.com/v1'}/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        if json_output:
            payload["response_format"] = {"type": "json_object"}
            
        headers = {
            "Authorization": f"Bearer {self.api_key or 'lm-studio'}",  # Dummy key for local
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                raise LLMError(f"OpenAI API error: {str(e)}")

    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        json_output: bool,
        temperature: float,
    ) -> str:
        """Generate using Anthropic API."""
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.config.max_tokens,
            "temperature": temperature,
        }
        
        if system_prompt:
            payload["system"] = system_prompt

        # Anthropic doesn't have a strict JSON mode flag like OpenAI, 
        # but we can prompt for it.
        if json_output:
            payload["messages"][0]["content"] += "\nRespond with valid JSON only."

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
            except httpx.HTTPError as e:
                raise LLMError(f"Anthropic API error: {str(e)}")

    async def check_connection(self) -> bool:
        """Check if LLM provider is reachable."""
        try:
            # Simple ping/check depending on provider
            if self.provider == LLMProvider.OLLAMA:
                url = f"{self.base_url.replace('/api', '')}/" # Root often returns status
                async with httpx.AsyncClient(timeout=5) as client:
                    resp = await client.get(url)
                    return resp.status_code == 200
            elif self.provider == LLMProvider.LOCAL:
                # Try models endpoint
                 url = f"{self.base_url}/models"
                 async with httpx.AsyncClient(timeout=5) as client:
                    resp = await client.get(url)
                    return resp.status_code == 200
            # For cloud providers, assume true if key exists (basic check)
            return bool(self.api_key)
        except Exception:
            return False
