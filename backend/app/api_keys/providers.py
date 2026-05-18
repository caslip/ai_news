"""
Provider Configuration - Defines supported AI providers and their properties
"""

PROVIDERS = {
    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-chat", "deepseek-v4-flash", "deepseek-v3-flash"],
        "supports_function_calling": True,
        "supports_vision": False,
        "website": "https://platform.deepseek.com",
        "description": "DeepSeek - 中国领先的 AI 大模型服务商",
    },
    "kimi": {
        "id": "kimi",
        "name": "Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "supports_function_calling": True,
        "supports_vision": True,
        "website": "https://platform.moonshot.cn",
        "description": "Kimi - Moonshot AI 开发的智能助手",
    },
    "minimax": {
        "id": "minimax",
        "name": "MiniMax",
        "base_url": "https://api.minimax.chat/v1",
        "models": ["abab6-chat", "abab6.5s-chat", "abab6.5g-chat"],
        "supports_function_calling": True,
        "supports_vision": True,
        "website": "https://www.minimax.io",
        "description": "MiniMax - 中国 AI 初创公司开发的语言模型",
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4"],
        "supports_function_calling": True,
        "supports_vision": True,
        "website": "https://platform.openai.com",
        "description": "OpenAI - ChatGPT 背后的 AI 研究公司",
    },
    "gemini": {
        "id": "gemini",
        "name": "Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"],
        "supports_function_calling": True,
        "supports_vision": True,
        "website": "https://ai.google.dev",
        "description": "Gemini - Google AI 开发的多模态大模型",
    },
    "anthropic": {
        "id": "anthropic",
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
        ],
        "supports_function_calling": True,
        "supports_vision": True,
        "website": "https://www.anthropic.com",
        "description": "Anthropic - Claude 大模型背后的 AI 安全公司",
    },
    "openrouter": {
        "id": "openrouter",
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models": [
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
            "google/gemini-1.5-pro",
            "deepseek/deepseek-chat-v3-0324",
            "meta-llama/llama-3-70b-instruct",
        ],
        "supports_function_calling": True,
        "supports_vision": True,
        "website": "https://openrouter.ai",
        "description": "OpenRouter - 统一访问多个 AI 模型的平台",
    },
}


def get_provider(provider_id: str) -> dict | None:
    """Get provider configuration by ID"""
    return PROVIDERS.get(provider_id)


def get_all_providers() -> list[dict]:
    """Get all available providers"""
    return list(PROVIDERS.values())


def get_provider_models(provider_id: str) -> list[str]:
    """Get available models for a provider"""
    provider = PROVIDERS.get(provider_id)
    return provider["models"] if provider else []


def is_valid_provider(provider_id: str) -> bool:
    """Check if a provider ID is valid"""
    return provider_id in PROVIDERS
