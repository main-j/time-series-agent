import time
import logging
import backoff
import openai
from typing import Dict, List, Optional, Union
from tenacity import (
    retry,
    stop_after_attempt, 
    wait_exponential,
    retry_if_exception_type
)

class OpenAIClient:
    def __init__(
        self,
        api_config: Dict,
        max_retries: int = 3,
        timeout: int = 30,
        rate_limit_rpm: int = 200
    ):
        """
        Initialize OpenAI API client
        
        Args:
            api_config: API configuration dictionary containing api_key, base_url, etc.
            max_retries: Maximum number of retries
            timeout: Timeout in seconds
            rate_limit_rpm: Maximum number of requests per minute
        """
        self.client = openai.OpenAI(
            api_key=api_config["api_key"],
            base_url=api_config["base_url"]
        )
        self.model = api_config["model"]
        self.temperature = api_config["temperature"]
        self.max_tokens = api_config["max_tokens"]
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Rate limit related
        self.rate_limit_rpm = rate_limit_rpm
        self.request_timestamps: List[float] = []
        
    def _wait_for_rate_limit(self):
        """Implement simple rate limiting"""
        current_time = time.time()
        # Clean up timestamps older than 1 minute
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts <= 60
        ]
        
        if len(self.request_timestamps) >= self.rate_limit_rpm:
            # Wait until the earliest request is older than 1 minute
            sleep_time = 60 - (current_time - self.request_timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.request_timestamps.append(current_time)

    @retry(
        retry=retry_if_exception_type((
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.RateLimitError
        )),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3)
    )
    def _make_request(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict:
        """
        Send request to OpenAI API
        
        Args:
            messages: List of messages
            tools: List of available tools
            tool_choice: Tool selection strategy
            
        Returns:
            API response
        """
        self._wait_for_rate_limit()
        
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "timeout": self.timeout
            }
            
            if tools:
                kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
                
            response = self.client.chat.completions.create(**kwargs)
            return response
            
        except openai.APIError as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict:
        """
        Public interface for generating responses
        
        Args:
            messages: List of messages
            tools: List of available tools
            tool_choice: Tool selection strategy
            
        Returns:
            Processed response
        """
        try:
            response = self._make_request(
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )
            return response
        except Exception as e:
            logging.error(f"Failed to generate response: {str(e)}")
            raise