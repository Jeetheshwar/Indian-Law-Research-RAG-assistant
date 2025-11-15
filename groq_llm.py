"""Custom LangChain LLM wrapper for Groq API."""

from typing import Any, List, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from groq import Groq
from pydantic import Field


class GroqChatModel(BaseChatModel):
    """Custom chat model using Groq API."""
    
    client: Any = Field(default=None, exclude=True)
    model: str = Field(default="moonshotai/kimi-k2-instruct-0905")
    api_key: str = Field(default="")
    temperature: float = Field(default=0.6)
    max_tokens: int = Field(default=4096)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.client:
            self.client = Groq(api_key=self.api_key)
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "groq"
    
    def _convert_messages_to_groq_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages to Groq format."""
        groq_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                groq_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                groq_messages.append({"role": "assistant", "content": message.content})
            elif isinstance(message, SystemMessage):
                groq_messages.append({"role": "system", "content": message.content})
            else:
                # Default to user message
                groq_messages.append({"role": "user", "content": str(message.content)})
        return groq_messages
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response."""
        groq_messages = self._convert_messages_to_groq_format(messages)
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=self.temperature,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                top_p=1,
                stream=False,
                stop=stop
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Handle empty responses
            if not content or content.strip() == "":
                content = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error calling Groq API: {str(e)}"
            print(f"[ERROR] {error_message}")
            
            # Return a fallback message
            fallback_content = "I apologize, but I encountered an error processing your request. Please try again."
            message = AIMessage(content=fallback_content)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generate - falls back to sync for now."""
        return self._generate(messages, stop, run_manager, **kwargs)
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

