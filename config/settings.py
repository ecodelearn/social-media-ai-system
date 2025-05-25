#!/usr/bin/env python3
"""
Configurações Gerais do Sistema - Social Media AI System

Este módulo centraliza todas as configurações do sistema, incluindo:
- Configurações de LLMs (Gemini e OpenAI)  
- Configurações dos agentes
- Configurações de saída e exportação
- Configurações MCP (Perplexity e WhatsApp)

Autor: Sistema de IA Colaborativo
Versão: 1.0.0
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

@dataclass
class LLMConfig:
    """Configuração para um modelo de linguagem"""
    provider: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30

@dataclass
class AgentConfig:
    """Configuração para um agente especializado"""
    name: str
    role: str
    goal: str
    backstory: str
    llm_config: LLMConfig
    tools: List[str] = None
    max_iter: int = 5
    max_execution_time: Optional[int] = None

@dataclass
class PlatformConfig:
    """Configuração para uma plataforma de rede social"""
    name: str
    max_chars: int
    supports_images: bool
    supports_videos: bool
    image_dimensions: Dict[str, tuple]
    hashtag_limit: int
    tone: str

class SystemSettings:
    """Configurações principais do sistema"""
    
    # === INFORMAÇÕES DO PROJETO ===
    PROJECT_NAME = "Social Media AI System"
    VERSION = "1.0.0"
    PHASE = "FASE 1 - FUNDAÇÃO"
    
    # === CAMINHOS DO SISTEMA ===
    BASE_DIR = Path(__file__).parent.parent
    PROJECT_ROOT = BASE_DIR  # Alias para compatibilidade
    CONFIG_DIR = BASE_DIR / "config"
    CORE_DIR = BASE_DIR / "core"
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    TESTS_DIR = BASE_DIR / "tests"
    
    # Subpastas de dados
    EMBEDDINGS_DIR = DATA_DIR / "embeddings"
    VISUAL_GPT_DIR = DATA_DIR / "visual_gpt"
    
    # Subpastas de saída
    CONTENT_DIR = OUTPUT_DIR / "content"
    PROMPTS_DIR = OUTPUT_DIR / "prompts"
    ANALYTICS_DIR = OUTPUT_DIR / "analytics"
    SENT_MESSAGES_DIR = OUTPUT_DIR / "sent_messages"
    
    # === CONFIGURAÇÕES DE LLMs ===
    
    # Google Gemini (Gratuito) - Agentes Pesquisador e Redator
    GEMINI_CONFIG = LLMConfig(
        provider="google",
        model="gemini-1.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY", ""),
        temperature=0.7,
        max_tokens=8192,
        timeout=30
    )
    
    # OpenAI GPT-4o-mini (Pago) - Agentes Visual e Editor
    OPENAI_CONFIG = LLMConfig(
        provider="openai", 
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        temperature=0.3,  # Mais conservador para editor
        max_tokens=4096,
        timeout=30
    )
    
    # === CONFIGURAÇÕES DOS AGENTES ===
    
    # 🔍 Agente Pesquisador (Gemini Flash)
    RESEARCHER_CONFIG = AgentConfig(
        name="Pesquisador Digital",
        role="Especialista em Research Digital e Tendências",
        goal="Encontrar informações atualizadas, dados precisos e oportunidades de conteúdo sobre qualquer tema",
        backstory="""Você é um pesquisador digital experiente com vasta experiência em análise de tendências, 
        coleta de dados atualizados e identificação de oportunidades de conteúdo. Você trabalha com ferramentas 
        de pesquisa avançadas como Perplexity AI para garantir informações sempre atuais e relevantes. 
        Seu foco é fornecer dados sólidos que servirão como base para criação de conteúdo de alta qualidade.""",
        llm_config=GEMINI_CONFIG,
        tools=["perplexity_search", "web_search"],
        max_iter=3,
        max_execution_time=120
    )
    
    # ✍️ Agente Redator SEO (Gemini Flash)
    WRITER_CONFIG = AgentConfig(
        name="Redator SEO & Redes Sociais",
        role="Copywriter Especialista em SEO e Algoritmos de Redes Sociais",
        goal="Criar conteúdo otimizado que engaja, converte e se adequa perfeitamente a cada plataforma",
        backstory="""Você é um copywriter profissional especializado em SEO e algoritmos de redes sociais. 
        Conhece profundamente como funcionam os algoritmos do Instagram, LinkedIn e WhatsApp. Sabe criar 
        conteúdo persuasivo, usar hashtags estratégicas e call-to-actions eficazes. Seu conteúdo sempre 
        busca maximizar engajamento, alcance e conversões, adaptando tom e formato para cada plataforma específica.""",
        llm_config=GEMINI_CONFIG,
        tools=["seo_analyzer", "hashtag_generator"],
        max_iter=5,
        max_execution_time=180
    )
    
    # 🎨 Agente Visual Designer (GPT-4o-mini)
    VISUAL_CONFIG = AgentConfig(
        name="Visual Designer & Prompt Engineer",
        role="Designer Visual e Especialista em Prompt Engineering para DALL-E",
        goal="Criar prompts visuais profissionais que geram imagens impactantes e adequadas para cada plataforma",
        backstory="""Você é um designer visual e prompt engineer especializado em DALL-E e outras ferramentas 
        de geração de imagens por IA. Tem acesso ao conhecimento completo do manual VisualGPT através do sistema 
        RAG. Conhece formatos, dimensões, estilos e tendências visuais para cada rede social. Seus prompts 
        sempre geram imagens profissionais, alinhadas com a marca e otimizadas para engajamento visual.""",
        llm_config=OPENAI_CONFIG,
        tools=["visual_rag", "dalle_optimizer"],
        max_iter=3,
        max_execution_time=90
    )
    
    # 🎬 Agente Editor Final (GPT-4o-mini)
    EDITOR_CONFIG = AgentConfig(
        name="Editor Final & Gerente de Qualidade",
        role="Quality Assurance Manager e Editor Chefe",
        goal="Garantir excelência, consistência e qualidade profissional de todo conteúdo antes da publicação",
        backstory="""Você é um editor chefe experiente e gerente de qualidade rigoroso. Sua responsabilidade 
        é revisar, aprovar ou rejeitar todo conteúdo criado pelos outros agentes. Você verifica coerência, 
        qualidade, adequação à plataforma, alinhamento com objetivos e potencial de engajamento. Só aprova 
        conteúdo que atende aos mais altos padrões profissionais. Quando rejeita, fornece feedback específico 
        e construtivo para melhorias.""",
        llm_config=OPENAI_CONFIG,
        tools=["quality_checker", "brand_validator"],
        max_iter=2,
        max_execution_time=60
    )
    
    # === CONFIGURAÇÕES DAS PLATAFORMAS ===
    
    PLATFORMS = {
        "instagram": PlatformConfig(
            name="Instagram",
            max_chars=2200,
            supports_images=True,
            supports_videos=True,
            image_dimensions={
                "feed": (1080, 1080),
                "story": (1080, 1920),
                "reel": (1080, 1920)
            },
            hashtag_limit=30,
            tone="criativo_inspiracional"
        ),
        
        "whatsapp": PlatformConfig(
            name="WhatsApp",
            max_chars=4096,
            supports_images=True,
            supports_videos=True,
            image_dimensions={
                "message": (1024, 1024),
                "status": (1080, 1920)
            },
            hashtag_limit=0,  # WhatsApp não usa hashtags
            tone="conversacional_amigavel"
        ),
        
        "linkedin": PlatformConfig(
            name="LinkedIn",
            max_chars=3000,
            supports_images=True,
            supports_videos=True,
            image_dimensions={
                "post": (1200, 628),
                "article": (1200, 627),
                "carousel": (1080, 1080)
            },
            hashtag_limit=5,
            tone="profissional_autoridade"
        )
    }
    
    # === CONFIGURAÇÕES MCP ===
    
    # Perplexity MCP
    PERPLEXITY_MCP = {
        "server_name": "github.com.pashpashpash/perplexity-mcp",
        "enabled": True,
        "tools": ["search", "chat_perplexity", "get_documentation"]
    }
    
    # WhatsApp Evolution API MCP
    WHATSAPP_MCP = {
        "server_name": "evoapi_mcp",
        "enabled": True,
        "tools": ["send_message_to_phone", "send_message_to_group", "get_groups", "get_group_messages"]
    }
    
    # === CONFIGURAÇÕES RAG VISUAL ===
    
    RAG_CONFIG = {
        "pdf_path": DATA_DIR / "VISUAL GPT.pdf",
        "embeddings_model": "text-embedding-3-small",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "similarity_threshold": 0.7,
        "max_results": 5
    }
    
    # === CONFIGURAÇÕES DO ORQUESTRADOR ===
    
    @dataclass
    class OrchestratorConfig:
        """Configuração para o orquestrador"""
        max_concurrent_executions: int = 3
        default_timeout: int = 300
        execution_timeout: int = 300
        quality_threshold: float = 0.8
        retry_attempts: int = 2
        enable_feedback_loop: bool = True
        save_intermediate_results: bool = True
    
    ORCHESTRATOR_CONFIG = OrchestratorConfig()
    
    # === CONFIGURAÇÕES DE SAÍDA ===
    
    OUTPUT_CONFIG = {
        "save_content": True,
        "save_prompts": True,
        "save_analytics": True,
        "export_formats": ["markdown", "json", "txt"],
        "include_metadata": True,
        "timestamp_format": "%Y%m%d_%H%M%S"
    }
    
    # === CONFIGURAÇÕES DE LOGGING ===
    
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": OUTPUT_DIR / "logs" / "system.log",
        "max_size": "10MB",
        "backup_count": 5
    }
    
    # === MÉTODOS UTILITÁRIOS ===
    
    @classmethod
    def create_directories(cls):
        """Cria todas as pastas necessárias do sistema"""
        directories = [
            cls.DATA_DIR,
            cls.OUTPUT_DIR,
            cls.EMBEDDINGS_DIR,
            cls.VISUAL_GPT_DIR,
            cls.CONTENT_DIR,
            cls.PROMPTS_DIR,
            cls.ANALYTICS_DIR,
            cls.SENT_MESSAGES_DIR,
            cls.OUTPUT_DIR / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Valida se as chaves de API estão configuradas"""
        return {
            "google": bool(cls.GEMINI_CONFIG.api_key),
            "openai": bool(cls.OPENAI_CONFIG.api_key)
        }
    
    @classmethod
    def get_platform_config(cls, platform: str) -> Optional[PlatformConfig]:
        """Retorna configuração de uma plataforma específica"""
        return cls.PLATFORMS.get(platform.lower())
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Optional[AgentConfig]:
        """Retorna configuração de um agente específico"""
        agents = {
            "researcher": cls.RESEARCHER_CONFIG,
            "writer": cls.WRITER_CONFIG,
            "visual": cls.VISUAL_CONFIG,
            "editor": cls.EDITOR_CONFIG
        }
        return agents.get(agent_name.lower())

# Criar diretórios na importação
SystemSettings.create_directories()

# Validar chaves API na importação
_api_status = SystemSettings.validate_api_keys()
if not all(_api_status.values()):
    import warnings
    missing = [provider for provider, valid in _api_status.items() if not valid]
    warnings.warn(f"Chaves de API não configuradas: {', '.join(missing)}")
