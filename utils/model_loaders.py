import os
from dotenv import load_dotenv
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model # Universal factory
from utils.config_loader import load_config

load_dotenv()

class ConfigLoader:
    def __init__(self):
        self.config = load_config()
        
    def __getitem__(self, key):
        return self.config[key]

class ModelLoader(BaseModel):
    # Support any string, but default to 'google' for your current needs
    model_provider: str = "google" 
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)
    
    def model_post_init(self, __context: Any) -> None:
        self.config = ConfigLoader()
        
    model_config = {"arbitrary_types_allowed": True}
        
    # In model_loader.py
    def load_llm(self, api_key: Optional[str] = None):
        print(f"--- Loading LLM Provider: {self.model_provider} ---")
        try:
            if not self.config:
                 self.config = ConfigLoader()
                 
            model_cfg = self.config['llm'].get(self.model_provider)
            if not model_cfg:
                print(f"⚠️ Provider '{self.model_provider}' not found in config.yaml. Falling back to 'google'.")
                self.model_provider = "google"
                model_cfg = self.config['llm']['google']

            model_name = model_cfg.get("model_name")
            provider = model_cfg.get("provider")

            # Extract OpenRouter base_url if defined in config, else use None
            base_url = model_cfg.get("base_url")

            kwargs = {
                "model": model_name,
                "model_provider": provider,
                "temperature": 0.1,
                "max_tokens": 4096,
            }
            if base_url:
                kwargs["base_url"] = base_url

            # Map specific providers to their env vars if using generic clients
            if self.model_provider == "deepseek":
                 kwargs["api_key"] = os.getenv("DEEPSEEK_API_KEY")
            elif self.model_provider == "mistral":
                 kwargs["api_key"] = os.getenv("MISTRAL_API_KEY")

            if self.model_provider == "groq":
                 api_key = api_key or os.getenv("GROQ_API_KEY")
                 if not api_key:
                     print("⚠️ GROQ_API_KEY not found. Server starting in BYOK mode only.")
                     # Return a dummy or None; the agent_function must handle this.
                     return None
                     
                 from langchain_groq import ChatGroq
                 return ChatGroq(
                     model=model_name, 
                     api_key=api_key,
                     temperature=0.1,
                     max_retries=5,
                     max_tokens=4096,
                 )
            
            # For other providers via init_chat_model
            if api_key:
                kwargs["api_key"] = api_key
                
            llm = init_chat_model(**kwargs)

            return llm

        except KeyError:
            raise ValueError(f"Provider '{self.model_provider}' not found in config.yaml")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise