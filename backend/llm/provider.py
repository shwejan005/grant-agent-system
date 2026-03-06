"""
Swappable LLM Provider Interface
Supports Gemini (default), OpenAI, Anthropic, Mistral.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, LLM_PROVIDER


def get_llm(provider: str = None, temperature: float = 0.7, model: str = None):
    """
    Get a LangChain-compatible LLM instance.

    Args:
        provider: One of 'gemini', 'openai', 'anthropic', 'mistral'
        temperature: Sampling temperature
        model: Specific model name override

    Returns:
        LangChain BaseLLM instance
    """
    provider = provider or LLM_PROVIDER

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=temperature,
            convert_system_message_to_human=True,
        )

    elif provider == "openai":
        from langchain.chat_models import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-4",
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    elif provider == "anthropic":
        from langchain.chat_models import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-3-sonnet-20240229",
            temperature=temperature,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        )

    elif provider == "mistral":
        from langchain.chat_models import ChatMistralAI
        return ChatMistralAI(
            model=model or "mistral-large-latest",
            temperature=temperature,
            mistral_api_key=os.getenv("MISTRAL_API_KEY", ""),
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
