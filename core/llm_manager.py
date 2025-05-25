#!/usr/bin/env python3
"""
Gerenciador de Large Language Models - Social Media AI System

Este módulo gerencia as conexões e operações com os diferentes LLMs:
- Google Gemini Flash (gratuito) - Pesquisador e Redator
- OpenAI GPT-4o-mini (pago) - Visual Designer e Editor

Autor: Sistema de IA Colaborativo
Versão: 1.0.0
"""

import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

# LLM Imports
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logging.warning("Google Generative AI não disponível")

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI não disponível")

# CrewAI Imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain não disponível")

from config.settings import SystemSettings, LLMConfig

class LLMProvider(Enum):
    """Provedores de LLM suportados"""
    GOOGLE = "google"
    OPENAI = "openai"

@dataclass
class LLMResponse:
    """Resposta padronizada de um LLM"""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict] = None

@dataclass
class LLMStats:
    """Estatísticas de uso dos LLMs"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    error_count: int = 0

class LLMManager:
    """Gerenciador centralizado de Large Language Models"""
    
    def __init__(self):
        """Inicializa o gerenciador de LLMs"""
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.gemini_config = SystemSettings.GEMINI_CONFIG
        self.openai_config = SystemSettings.OPENAI_CONFIG
        
        # Clientes dos LLMs
        self._google_client = None
        self._openai_client = None
        self._langchain_google = None
        self._langchain_openai = None
        
        # Estatísticas de uso
        self.stats = {
            LLMProvider.GOOGLE: LLMStats(),
            LLMProvider.OPENAI: LLMStats()
        }
        
        # Cache de configurações para CrewAI
        self._crew_llms = {}
        
        # Inicializar conexões
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Inicializa as conexões com os LLMs"""
        try:
            self._initialize_google()
            self._initialize_openai()
            self._initialize_langchain()
            self.logger.info("LLM Manager inicializado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar LLM Manager: {e}")
            raise
    
    def _initialize_google(self):
        """Inicializa conexão com Google Gemini"""
        if not GOOGLE_AVAILABLE:
            self.logger.warning("Google Generative AI não disponível")
            return
            
        if not self.gemini_config.api_key:
            self.logger.warning("API Key do Google não configurada")
            return
        
        try:
            genai.configure(api_key=self.gemini_config.api_key)
            
            # Configurações de segurança permissivas para conteúdo de marketing
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Configuração do modelo
            generation_config = {
                "temperature": self.gemini_config.temperature,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": self.gemini_config.max_tokens,
            }
            
            self._google_client = genai.GenerativeModel(
                model_name=self.gemini_config.model,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            self.logger.info("Conexão Google Gemini inicializada")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Google Gemini: {e}")
            self._google_client = None
    
    def _initialize_openai(self):
        """Inicializa conexão com OpenAI"""
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI não disponível")
            return
            
        if not self.openai_config.api_key:
            self.logger.warning("API Key da OpenAI não configurada")
            return
        
        try:
            self._openai_client = OpenAI(
                api_key=self.openai_config.api_key,
                timeout=self.openai_config.timeout
            )
            
            # Testar conexão
            self._openai_client.models.list()
            self.logger.info("Conexão OpenAI inicializada")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar OpenAI: {e}")
            self._openai_client = None
    
    def _initialize_langchain(self):
        """Inicializa instâncias LangChain para CrewAI"""
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain não disponível")
            return
        
        # Google LangChain
        if self.gemini_config.api_key:
            try:
                self._langchain_google = ChatGoogleGenerativeAI(
                    model=self.gemini_config.model,
                    google_api_key=self.gemini_config.api_key,
                    temperature=self.gemini_config.temperature,
                    max_tokens=self.gemini_config.max_tokens,
                    timeout=self.gemini_config.timeout
                )
                self.logger.info("LangChain Google inicializado")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar LangChain Google: {e}")
        
        # OpenAI LangChain
        if self.openai_config.api_key:
            try:
                self._langchain_openai = ChatOpenAI(
                    model=self.openai_config.model,
                    openai_api_key=self.openai_config.api_key,
                    temperature=self.openai_config.temperature,
                    max_tokens=self.openai_config.max_tokens,
                    timeout=self.openai_config.timeout
                )
                self.logger.info("LangChain OpenAI inicializado")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar LangChain OpenAI: {e}")
    
    def get_crew_llm(self, agent_name: str):
        """Retorna instância LLM configurada para um agente específico do CrewAI"""
        if agent_name in self._crew_llms:
            return self._crew_llms[agent_name]
        
        # Mapear agentes para LLMs
        llm_mapping = {
            "researcher": self._langchain_google,  # Pesquisador usa Gemini
            "writer": self._langchain_google,      # Redator usa Gemini
            "visual": self._langchain_openai,      # Visual usa OpenAI
            "editor": self._langchain_openai       # Editor usa OpenAI
        }
        
        llm = llm_mapping.get(agent_name.lower())
        if llm:
            self._crew_llms[agent_name] = llm
            self.logger.info(f"LLM configurado para agente {agent_name}")
        else:
            self.logger.warning(f"LLM não encontrado para agente {agent_name}")
        
        return llm
    
    async def generate_text(
        self, 
        prompt: str, 
        provider: LLMProvider,
        **kwargs
    ) -> LLMResponse:
        """Gera texto usando o LLM especificado"""
        start_time = time.time()
        
        try:
            if provider == LLMProvider.GOOGLE:
                response = await self._generate_google(prompt, **kwargs)
            elif provider == LLMProvider.OPENAI:
                response = await self._generate_openai(prompt, **kwargs)
            else:
                raise ValueError(f"Provedor não suportado: {provider}")
            
            # Calcular tempo de resposta
            response.response_time = time.time() - start_time
            
            # Atualizar estatísticas
            self._update_stats(provider, response)
            
            self.logger.info(
                f"Texto gerado com {provider.value}: "
                f"{len(response.content)} chars em {response.response_time:.2f}s"
            )
            
            return response
            
        except Exception as e:
            self.stats[provider].error_count += 1
            self.logger.error(f"Erro ao gerar texto com {provider.value}: {e}")
            raise
    
    async def _generate_google(self, prompt: str, **kwargs) -> LLMResponse:
        """Gera texto usando Google Gemini"""
        if not self._google_client:
            raise RuntimeError("Cliente Google não inicializado")
        
        try:
            response = self._google_client.generate_content(prompt)
            
            return LLMResponse(
                content=response.text,
                provider="google",
                model=self.gemini_config.model,
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None,
                cost_estimate=0.0,  # Gemini Flash é gratuito
                metadata={
                    "candidates": len(response.candidates) if hasattr(response, 'candidates') else 1,
                    "safety_ratings": getattr(response, 'safety_ratings', None)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro específico do Google Gemini: {e}")
            raise
    
    async def _generate_openai(self, prompt: str, **kwargs) -> LLMResponse:
        """Gera texto usando OpenAI"""
        if not self._openai_client:
            raise RuntimeError("Cliente OpenAI não inicializado")
        
        try:
            response = self._openai_client.chat.completions.create(
                model=self.openai_config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.openai_config.temperature,
                max_tokens=self.openai_config.max_tokens,
                **kwargs
            )
            
            # Calcular custo estimado (GPT-4o-mini pricing)
            tokens_used = response.usage.total_tokens
            cost_per_1k_tokens = 0.00015  # $0.15 per 1K tokens (exemplo)
            cost_estimate = (tokens_used / 1000) * cost_per_1k_tokens
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider="openai",
                model=self.openai_config.model,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "usage": response.usage._asdict() if response.usage else None
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro específico da OpenAI: {e}")
            raise
    
    def _update_stats(self, provider: LLMProvider, response: LLMResponse):
        """Atualiza estatísticas de uso"""
        stats = self.stats[provider]
        
        stats.total_requests += 1
        if response.tokens_used:
            stats.total_tokens += response.tokens_used
        if response.cost_estimate:
            stats.total_cost += response.cost_estimate
        if response.response_time:
            # Calcular média móvel do tempo de resposta
            stats.avg_response_time = (
                (stats.avg_response_time * (stats.total_requests - 1) + response.response_time) 
                / stats.total_requests
            )
    
    def get_stats(self) -> Dict[str, LLMStats]:
        """Retorna estatísticas de uso dos LLMs"""
        return {provider.value: stats for provider, stats in self.stats.items()}
    
    def get_status(self) -> Dict[str, bool]:
        """Retorna status de conexão dos LLMs"""
        return {
            "google": self._google_client is not None,
            "openai": self._openai_client is not None,
            "langchain_google": self._langchain_google is not None,
            "langchain_openai": self._langchain_openai is not None
        }
    
    async def test_connections(self) -> Dict[str, bool]:
        """Testa todas as conexões LLM"""
        results = {}
        
        # Testar Google
        try:
            if self._google_client:
                response = await self.generate_text(
                    "Teste de conexão", 
                    LLMProvider.GOOGLE
                )
                results["google"] = len(response.content) > 0
            else:
                results["google"] = False
        except:
            results["google"] = False
        
        # Testar OpenAI
        try:
            if self._openai_client:
                response = await self.generate_text(
                    "Teste de conexão", 
                    LLMProvider.OPENAI
                )
                results["openai"] = len(response.content) > 0
            else:
                results["openai"] = False
        except:
            results["openai"] = False
        
        return results
    
    def estimate_monthly_cost(self, daily_requests: int = 50) -> Dict[str, float]:
        """Estima custo mensal baseado no uso atual"""
        monthly_requests = daily_requests * 30
        
        # Gemini Flash é gratuito
        google_cost = 0.0
        
        # OpenAI GPT-4o-mini (estimativa)
        avg_tokens_per_request = 1000  # Estimativa conservadora
        total_tokens = monthly_requests * avg_tokens_per_request
        openai_cost = (total_tokens / 1000) * 0.00015  # $0.15 per 1K tokens
        
        return {
            "google": google_cost,
            "openai": openai_cost,
            "total": google_cost + openai_cost,
            "requests_estimated": monthly_requests
        }

# Instância global do gerenciador
llm_manager = LLMManager()

# Funções de conveniência para uso direto
async def generate_with_gemini(prompt: str, **kwargs) -> LLMResponse:
    """Gera texto usando Gemini"""
    return await llm_manager.generate_text(prompt, LLMProvider.GOOGLE, **kwargs)

async def generate_with_openai(prompt: str, **kwargs) -> LLMResponse:
    """Gera texto usando OpenAI"""
    return await llm_manager.generate_text(prompt, LLMProvider.OPENAI, **kwargs)

def get_agent_llm(agent_name: str):
    """Retorna LLM configurado para um agente específico"""
    return llm_manager.get_crew_llm(agent_name)
