#!/usr/bin/env python3
"""
OpenRouter Setup Script
Helps configure OpenRouter as a provider in RAG-SaaS
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def setup_openrouter_provider():
    """Setup OpenRouter as a provider in RAG-SaaS"""
    print("🚀 Setting up OpenRouter Provider for RAG-SaaS")
    print("=" * 60)
    
    # OpenRouter supported models
    openrouter_models = {
        "openai": [
            "openai/gpt-4o",
            "openai/gpt-4o-mini", 
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo"
        ],
        "anthropic": [
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku"
        ],
        "meta": [
            "meta-llama/llama-3.1-405b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct"
        ],
        "google": [
            "google/gemini-pro-1.5",
            "google/gemini-pro"
        ],
        "mistral": [
            "mistralai/mistral-7b-instruct",
            "mistralai/mixtral-8x7b-instruct"
        ],
        "cohere": [
            "cohere/command-r-plus",
            "cohere/command-r"
        ]
    }
    
    # Embedding models
    embedding_models = [
        "text-embedding-3-small",
        "text-embedding-3-large", 
        "text-embedding-ada-002"
    ]
    
    print("\n📋 OpenRouter Provider Information:")
    print("-" * 40)
    print("🌐 API Base URL: https://openrouter.ai/api/v1")
    print("🔑 Authentication: Bearer token (API key)")
    print("📡 Protocol: OpenAI-compatible API")
    print("💰 Pricing: Pay-per-use, varies by model")
    
    print("\n🤖 Supported Model Categories:")
    for category, models in openrouter_models.items():
        print(f"  {category.upper()}:")
        for model in models[:3]:  # Show first 3 models
            print(f"    - {model}")
        if len(models) > 3:
            print(f"    ... and {len(models) - 3} more")
    
    print(f"\n🔤 Supported Embedding Models:")
    for model in embedding_models:
        print(f"  - {model}")
    
    print("\n⚙️ Configuration Steps:")
    print("-" * 40)
    print("1. Get OpenRouter API Key:")
    print("   - Visit: https://openrouter.ai/")
    print("   - Sign up and generate API key")
    print("   - Add to environment: OPENROUTER_API_KEY=your_key")
    
    print("\n2. Create Provider Configuration:")
    print("   - Use the admin panel or API")
    print("   - Provider Type: 'openrouter'")
    print("   - Model: 'openai/gpt-4o-mini' (or your choice)")
    print("   - Embedding Model: 'text-embedding-3-small'")
    
    print("\n3. Test Configuration:")
    print("   - Use the provider test endpoint")
    print("   - Verify LLM and embedding connections")
    
    # Create sample configuration
    sample_config = {
        "name": "OpenRouter GPT-4o Mini",
        "provider_type": "openrouter",
        "enabled": True,
        "api_key": "your_openrouter_api_key_here",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4o-mini",
        "embedding_model": "text-embedding-3-small",
        "temperature": 0.7,
        "max_tokens": 4096,
        "dimensions": 1536,
        "custom_config": {
            "context_window": 4096,
            "supports_function_calling": False,
            "supports_streaming": True
        }
    }
    
    print("\n📄 Sample Configuration JSON:")
    print("-" * 40)
    print(json.dumps(sample_config, indent=2))
    
    print("\n🔗 API Endpoints for Configuration:")
    print("-" * 40)
    print("POST /api/chat/config/providers - Create provider")
    print("GET /api/chat/config/providers - List providers")
    print("PUT /api/chat/config/providers/{id} - Update provider")
    print("POST /api/chat/config/providers/{id}/test - Test provider")
    
    print("\n✅ OpenRouter Setup Information Complete!")
    print("\n📋 Next Steps:")
    print("1. Get your OpenRouter API key")
    print("2. Create provider configuration via admin panel")
    print("3. Test the provider connection")
    print("4. Switch to OpenRouter provider")
    print("5. Start using 200+ models through OpenRouter!")

def create_openrouter_config_file():
    """Create a sample OpenRouter configuration file"""
    config_file = Path(__file__).parent / "openrouter_config.json"
    
    configs = [
        {
            "name": "OpenRouter GPT-4o Mini",
            "provider_type": "openrouter",
            "enabled": True,
            "api_key": "your_openrouter_api_key_here",
            "base_url": "https://openrouter.ai/api/v1",
            "model": "openai/gpt-4o-mini",
            "embedding_model": "text-embedding-3-small",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dimensions": 1536,
            "custom_config": {
                "context_window": 4096,
                "supports_function_calling": False,
                "supports_streaming": True
            }
        },
        {
            "name": "OpenRouter Claude 3.5 Sonnet",
            "provider_type": "openrouter",
            "enabled": False,
            "api_key": "your_openrouter_api_key_here",
            "base_url": "https://openrouter.ai/api/v1",
            "model": "anthropic/claude-3.5-sonnet",
            "embedding_model": "text-embedding-3-small",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dimensions": 1536,
            "custom_config": {
                "context_window": 4096,
                "supports_function_calling": False,
                "supports_streaming": True
            }
        },
        {
            "name": "OpenRouter Llama 3.1 70B",
            "provider_type": "openrouter",
            "enabled": False,
            "api_key": "your_openrouter_api_key_here",
            "base_url": "https://openrouter.ai/api/v1",
            "model": "meta-llama/llama-3.1-70b-instruct",
            "embedding_model": "text-embedding-3-small",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dimensions": 1536,
            "custom_config": {
                "context_window": 4096,
                "supports_function_calling": False,
                "supports_streaming": True
            }
        }
    ]
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(configs, f, indent=2)
    
    print(f"📄 Created sample configuration file: {config_file}")
    return config_file

def main():
    """Main execution function"""
    setup_openrouter_provider()
    config_file = create_openrouter_config_file()
    
    print(f"\n🎉 OpenRouter Provider Setup Complete!")
    print(f"📁 Sample configurations saved to: {config_file}")
    print("\n🔗 Useful Links:")
    print("  - OpenRouter Website: https://openrouter.ai/")
    print("  - OpenRouter Models: https://openrouter.ai/models")
    print("  - OpenRouter Pricing: https://openrouter.ai/pricing")
    print("  - OpenRouter Docs: https://openrouter.ai/docs")

if __name__ == "__main__":
    main()
