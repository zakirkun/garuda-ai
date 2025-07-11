import os
import time
import logging
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import litellm
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RateLimitTracker:
    requests: List[datetime]
    tokens: int
    last_reset: datetime

class MultiModelManager:
    """Multi-provider LLM manager with fallback mechanism"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.rate_trackers: Dict[str, RateLimitTracker] = {}
        self._setup_providers()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration if config file not found"""
        return {
            "models": {
                "openai": {"gpt-4-turbo": "gpt-4-turbo", "gpt-3.5-turbo": "gpt-3.5-turbo"},
                "anthropic": {"claude-3-sonnet": "claude-3-sonnet-20240229"},
                "ollama": {"llama3": "llama3:8b"}
            },
            "fallback_order": ["openai", "anthropic", "ollama"],
            "rate_limiting": {"requests_per_minute": 60, "tokens_per_minute": 40000}
        }
    
    def _setup_providers(self):
        """Setup provider configurations"""
        # Set API keys from environment
        if os.getenv("OPENAI_API_KEY"):
            litellm.openai_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("ANTHROPIC_API_KEY"):
            litellm.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("OLLAMA_BASE_URL"):
            litellm.ollama_base_url = os.getenv("OLLAMA_BASE_URL")
    
    def _check_rate_limit(self, provider: str) -> bool:
        """Check if provider is within rate limits"""
        now = datetime.now()
        rate_config = self.config.get("rate_limiting", {})
        
        if provider not in self.rate_trackers:
            self.rate_trackers[provider] = RateLimitTracker([], 0, now)
        
        tracker = self.rate_trackers[provider]
        
        # Remove old requests (older than 1 minute)
        tracker.requests = [req for req in tracker.requests if now - req < timedelta(minutes=1)]
        
        # Check request rate limit
        if len(tracker.requests) >= rate_config.get("requests_per_minute", 60):
            return False
        
        return True
    
    def _update_rate_limit(self, provider: str, tokens_used: int = 0):
        """Update rate limit tracking"""
        now = datetime.now()
        if provider in self.rate_trackers:
            self.rate_trackers[provider].requests.append(now)
            self.rate_trackers[provider].tokens += tokens_used
    
    def get_available_models(self, provider: str) -> Dict[str, str]:
        """Get available models for a provider"""
        return self.config.get("models", {}).get(provider, {})
    
    def get_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.config.get("models", {}).keys())
    
    def generate(
        self, 
        messages: List[Dict[str, str]], 
        provider: str = "openai", 
        model_name: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using specified provider with fallback mechanism
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: Provider name (openai, anthropic, ollama)
            model_name: Specific model name
            temperature: Response randomness (0-1)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
            
        Returns:
            Dict containing response, provider used, model, tokens, etc.
        """
        
        # Get model name if not specified
        if not model_name:
            available_models = self.get_available_models(provider)
            if not available_models:
                raise ValueError(f"No models available for provider: {provider}")
            model_name = list(available_models.values())[0]
        
        # Try primary provider
        result = self._try_generate(
            messages, provider, model_name, temperature, max_tokens, **kwargs
        )
        
        if result["success"]:
            return result
        
        # Try fallback providers
        fallback_order = self.config.get("fallback_order", [])
        for fallback_provider in fallback_order:
            if fallback_provider != provider:
                try:
                    fallback_models = self.get_available_models(fallback_provider)
                    if fallback_models:
                        fallback_model = list(fallback_models.values())[0]
                        result = self._try_generate(
                            messages, fallback_provider, fallback_model, 
                            temperature, max_tokens, **kwargs
                        )
                        if result["success"]:
                            result["fallback_used"] = True
                            result["original_provider"] = provider
                            return result
                except Exception as e:
                    self.logger.warning(f"Fallback provider {fallback_provider} failed: {e}")
                    continue
        
        # All providers failed
        return {
            "success": False,
            "error": "All providers failed",
            "response": "I'm sorry, I'm experiencing technical difficulties. Please try again later.",
            "provider": provider,
            "model": model_name,
            "tokens_used": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def _try_generate(
        self, 
        messages: List[Dict[str, str]], 
        provider: str, 
        model_name: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Try to generate response with specific provider"""
        
        try:
            # Check rate limits
            if not self._check_rate_limit(provider):
                return {
                    "success": False,
                    "error": "Rate limit exceeded",
                    "provider": provider,
                    "model": model_name,
                    "tokens_used": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            start_time = time.time()
            
            # Make API call
            response = litellm.completion(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            end_time = time.time()
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            
            # Update rate limiting
            self._update_rate_limit(provider, tokens_used)
            
            self.logger.info(f"Successfully generated response using {provider}/{model_name}")
            
            return {
                "success": True,
                "response": content,
                "provider": provider,
                "model": model_name,
                "tokens_used": tokens_used,
                "response_time": end_time - start_time,
                "timestamp": datetime.now().isoformat(),
                "fallback_used": False
            }
            
        except Exception as e:
            self.logger.error(f"Error with {provider}/{model_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": provider,
                "model": model_name,
                "tokens_used": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_model_info(self, provider: str, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        models = self.get_available_models(provider)
        if model_name not in models:
            return {"error": f"Model {model_name} not found for provider {provider}"}
        
        return {
            "provider": provider,
            "model": model_name,
            "full_name": models[model_name],
            "available": True
        }
    
    def test_providers(self) -> Dict[str, bool]:
        """Test all providers to check availability"""
        results = {}
        test_messages = [{"role": "user", "content": "Hello, this is a test message."}]
        
        for provider in self.get_providers():
            try:
                models = self.get_available_models(provider)
                if models:
                    model_name = list(models.values())[0]
                    result = self._try_generate(
                        test_messages, provider, model_name, 0.1, 10
                    )
                    results[provider] = result["success"]
                else:
                    results[provider] = False
            except Exception:
                results[provider] = False
        
        return results 