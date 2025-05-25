#!/usr/bin/env python3
"""
Definição dos 4 Agentes Especializados - Social Media AI System

Este módulo define os 4 agentes principais do sistema:
1. 🔍 Pesquisador Digital (Gemini Flash)
2. ✍️ Redator SEO & Redes Sociais (Gemini Flash)  
3. 🎨 Visual Designer & Prompt Engineer (GPT-4o-mini)
4. 🎬 Editor Final & Gerente de Qualidade (GPT-4o-mini)

Autor: Sistema de IA Colaborativo
Versão: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# CrewAI Imports
try:
    from crewai import Agent, Task, Crew
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logging.warning("CrewAI não disponível")

from config.settings import SystemSettings
from core.llm_manager import llm_manager

@dataclass
class ContentRequest:
    """Estrutura de uma solicitação de conteúdo"""
    topic: str
    platforms: List[str]
    target_audience: str
    objective: str
    tone: Optional[str] = None
    special_instructions: Optional[str] = None
    deadline: Optional[datetime] = None

@dataclass
class AgentResult:
    """Resultado de um agente específico"""
    agent_name: str
    success: bool
    content: str
    metadata: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

@dataclass
class CrewResult:
    """Resultado completo da execução do crew"""
    request: ContentRequest
    success: bool
    final_content: str
    agent_results: List[AgentResult]
    total_execution_time: float
    approval_status: str  # "approved", "rejected", "needs_revision"
    revision_feedback: Optional[str] = None

class SocialMediaAgents:
    """Gerenciador dos 4 agentes especializados"""
    
    def __init__(self):
        """Inicializa o sistema de agentes"""
        self.logger = logging.getLogger(__name__)
        
        if not CREWAI_AVAILABLE:
            raise RuntimeError("CrewAI não está disponível. Execute: pip install crewai")
        
        # Configurações dos agentes
        self.researcher_config = SystemSettings.RESEARCHER_CONFIG
        self.writer_config = SystemSettings.WRITER_CONFIG
        self.visual_config = SystemSettings.VISUAL_CONFIG
        self.editor_config = SystemSettings.EDITOR_CONFIG
        
        # Cache de agentes criados
        self._agents = {}
        self._crew = None
        
        # Inicializar agentes
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Inicializa todos os agentes do sistema"""
        try:
            self.logger.info("Inicializando agentes especializados...")
            
            # Criar os 4 agentes
            self._agents["researcher"] = self._create_researcher_agent()
            self._agents["writer"] = self._create_writer_agent()
            self._agents["visual"] = self._create_visual_agent()
            self._agents["editor"] = self._create_editor_agent()
            
            self.logger.info("Todos os agentes inicializados com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar agentes: {e}")
            raise
    
    def _create_researcher_agent(self) -> Agent:
        """Cria o agente Pesquisador Digital"""
        config = self.researcher_config
        llm = llm_manager.get_crew_llm("researcher")
        
        if not llm:
            raise RuntimeError("LLM não configurado para o agente Pesquisador")
        
        agent = Agent(
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=config.max_iter,
            max_execution_time=config.max_execution_time,
            tools=self._get_researcher_tools()
        )
        
        self.logger.info("🔍 Agente Pesquisador Digital criado")
        return agent
    
    def _create_writer_agent(self) -> Agent:
        """Cria o agente Redator SEO & Redes Sociais"""
        config = self.writer_config
        llm = llm_manager.get_crew_llm("writer")
        
        if not llm:
            raise RuntimeError("LLM não configurado para o agente Redator")
        
        agent = Agent(
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=config.max_iter,
            max_execution_time=config.max_execution_time,
            tools=self._get_writer_tools()
        )
        
        self.logger.info("✍️ Agente Redator SEO criado")
        return agent
    
    def _create_visual_agent(self) -> Agent:
        """Cria o agente Visual Designer & Prompt Engineer"""
        config = self.visual_config
        llm = llm_manager.get_crew_llm("visual")
        
        if not llm:
            raise RuntimeError("LLM não configurado para o agente Visual")
        
        agent = Agent(
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=config.max_iter,
            max_execution_time=config.max_execution_time,
            tools=self._get_visual_tools()
        )
        
        self.logger.info("🎨 Agente Visual Designer criado")
        return agent
    
    def _create_editor_agent(self) -> Agent:
        """Cria o agente Editor Final & Gerente de Qualidade"""
        config = self.editor_config
        llm = llm_manager.get_crew_llm("editor")
        
        if not llm:
            raise RuntimeError("LLM não configurado para o agente Editor")
        
        agent = Agent(
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=config.max_iter,
            max_execution_time=config.max_execution_time,
            tools=self._get_editor_tools()
        )
        
        self.logger.info("🎬 Agente Editor Final criado")
        return agent
    
    def _get_researcher_tools(self) -> List:
        """Retorna ferramentas para o agente Pesquisador"""
        # TODO: Implementar ferramentas MCP Perplexity na Fase 4
        tools = []
        
        # Placeholder para ferramentas futuras
        # tools.append(PerplexitySearchTool())
        # tools.append(WebSearchTool())
        
        return tools
    
    def _get_writer_tools(self) -> List:
        """Retorna ferramentas para o agente Redator"""
        # TODO: Implementar ferramentas de SEO e hashtags
        tools = []
        
        # Placeholder para ferramentas futuras
        # tools.append(SEOAnalyzerTool())
        # tools.append(HashtagGeneratorTool())
        
        return tools
    
    def _get_visual_tools(self) -> List:
        """Retorna ferramentas para o agente Visual"""
        # TODO: Implementar RAG Visual na Fase 2
        tools = []
        
        # Placeholder para ferramentas futuras
        # tools.append(VisualRAGTool())
        # tools.append(DALLEOptimizerTool())
        
        return tools
    
    def _get_editor_tools(self) -> List:
        """Retorna ferramentas para o agente Editor"""
        # TODO: Implementar ferramentas de qualidade
        tools = []
        
        # Placeholder para ferramentas futuras
        # tools.append(QualityCheckerTool())
        # tools.append(BrandValidatorTool())
        
        return tools
    
    def create_research_task(self, request: ContentRequest) -> Task:
        """Cria tarefa de pesquisa para o Pesquisador"""
        description = f"""
        Pesquise informações abrangentes e atualizadas sobre o tema: "{request.topic}"
        
        **CONTEXTO:**
        - Público-alvo: {request.target_audience}
        - Objetivo: {request.objective}
        - Plataformas: {', '.join(request.platforms)}
        
        **SUA MISSÃO:**
        1. Encontre dados atuais, estatísticas e tendências sobre o tema
        2. Identifique oportunidades de conteúdo e ângulos únicos
        3. Analise o que está funcionando nas redes sociais sobre este tema
        4. Colete informações relevantes sobre o público-alvo
        5. Identifique hashtags trending e palavras-chave relevantes
        
        **FORMATO DE SAÍDA:**
        Estruture sua pesquisa em seções claras:
        - 📊 Dados e Estatísticas Atuais
        - 🔥 Tendências e Oportunidades  
        - 👥 Insights sobre Público-alvo
        - 🏷️ Hashtags e Palavras-chave
        - 💡 Ângulos de Conteúdo Recomendados
        
        Seja preciso, atual e focado em insights acionáveis para criação de conteúdo.
        """
        
        return Task(
            description=description,
            agent=self._agents["researcher"],
            expected_output="Relatório estruturado de pesquisa com dados atuais, tendências e insights acionáveis"
        )
    
    def create_writing_task(self, request: ContentRequest) -> Task:
        """Cria tarefa de redação para o Redator SEO"""
        platforms_text = ', '.join(request.platforms)
        tone_instruction = f"Tom: {request.tone}" if request.tone else "Tom adequado à plataforma"
        
        description = f"""
        Com base na pesquisa fornecida, crie conteúdo otimizado para: {platforms_text}
        
        **CONTEXTO:**
        - Tema: {request.topic}
        - Público-alvo: {request.target_audience}
        - Objetivo: {request.objective}
        - {tone_instruction}
        
        **SUA MISSÃO:**
        1. Criar textos adaptados para cada plataforma solicitada
        2. Otimizar para algoritmos e engajamento
        3. Incluir calls-to-action eficazes
        4. Usar hashtags estratégicas
        5. Respeitar limites de caracteres de cada plataforma
        
        **FORMATO PARA CADA PLATAFORMA:**
        
        📷 **INSTAGRAM:**
        - Texto principal (máx. 2200 chars)
        - Hashtags estratégicas (máx. 30)
        - Call-to-action claro
        
        💬 **WHATSAPP:**
        - Mensagem conversacional (máx. 4096 chars)
        - Tom amigável e compartilhável
        - Sem hashtags (não são usadas no WhatsApp)
        
        💼 **LINKEDIN:**
        - Post profissional (máx. 3000 chars)
        - Tom de autoridade
        - Hashtags relevantes (máx. 5)
        
        Foque em maximizar engajamento, alcance e conversões.
        """
        
        return Task(
            description=description,
            agent=self._agents["writer"],
            expected_output="Conteúdo otimizado para cada plataforma com textos, hashtags e calls-to-action",
            context=[self.create_research_task(request)]  # Depende da pesquisa
        )
    
    def create_visual_task(self, request: ContentRequest) -> Task:
        """Cria tarefa visual para o Visual Designer"""
        platforms_text = ', '.join(request.platforms)
        
        description = f"""
        Com base no conteúdo criado, desenvolva prompts visuais profissionais para: {platforms_text}
        
        **CONTEXTO:**
        - Tema: {request.topic}
        - Público-alvo: {request.target_audience}
        - Objetivo: {request.objective}
        
        **SUA MISSÃO:**
        1. Criar prompts DALL-E detalhados e profissionais
        2. Adaptar dimensões e estilos para cada plataforma
        3. Usar técnicas avançadas de prompt engineering
        4. Garantir alinhamento visual com o conteúdo textual
        5. Considerar tendências visuais atuais
        
        **FORMATO PARA CADA PLATAFORMA:**
        
        📷 **INSTAGRAM:**
        - Prompt para Feed (1080x1080)
        - Prompt para Stories (1080x1920)
        - Estilo: moderno, atrativo, viral
        
        💬 **WHATSAPP:**
        - Prompt para mensagem (1024x1024)
        - Estilo: claro, informativo, compartilhável
        
        💼 **LINKEDIN:**
        - Prompt para post (1200x628)
        - Estilo: profissional, corporativo, confiável
        
        **ESTRUTURA DE CADA PROMPT:**
        1. Descrição principal da imagem
        2. Estilo visual e técnicas
        3. Cores e composição
        4. Elementos textuais (se necessário)
        5. Qualidade e resolução
        
        Use seu conhecimento especializado em prompts visuais para gerar imagens impactantes.
        """
        
        return Task(
            description=description,
            agent=self._agents["visual"],
            expected_output="Prompts DALL-E profissionais otimizados para cada plataforma",
            context=[self.create_writing_task(request)]  # Depende do conteúdo textual
        )
    
    def create_editing_task(self, request: ContentRequest) -> Task:
        """Cria tarefa de edição para o Editor Final"""
        platforms_text = ', '.join(request.platforms)
        
        description = f"""
        Revise e aprove/rejeite todo o conteúdo criado para: {platforms_text}
        
        **CONTEXTO:**
        - Tema: {request.topic}
        - Público-alvo: {request.target_audience}
        - Objetivo: {request.objective}
        
        **SUA MISSÃO DE QUALIDADE:**
        1. Revisar coerência entre pesquisa, texto e prompts visuais
        2. Verificar adequação a cada plataforma
        3. Avaliar potencial de engajamento
        4. Validar alinhamento com objetivos
        5. Aprovar ou rejeitar com feedback específico
        
        **CRITÉRIOS DE AVALIAÇÃO:**
        - ✅ Qualidade profissional
        - ✅ Coerência entre elementos
        - ✅ Adequação à plataforma
        - ✅ Potencial de engajamento
        - ✅ Alinhamento com objetivos
        - ✅ Precisão das informações
        
        **FORMATO DE SAÍDA:**
        📝 **DECISÃO:** [APROVADO] ou [REJEITADO] ou [REVISÃO NECESSÁRIA]
        
        **CONTEÚDO FINAL APROVADO:**
        [Se aprovado, organize todo o conteúdo de forma clara]
        
        **FEEDBACK PARA MELHORIAS:**
        [Se rejeitado/revisão, forneça feedback específico e construtivo]
        
        **JUSTIFICATIVA:**
        [Explique sua decisão baseada nos critérios de qualidade]
        
        Seja rigoroso - só aprove conteúdo que atende aos mais altos padrões profissionais.
        """
        
        return Task(
            description=description,
            agent=self._agents["editor"],
            expected_output="Decisão de aprovação com conteúdo final organizado ou feedback para melhorias",
            context=[
                self.create_research_task(request),
                self.create_writing_task(request),
                self.create_visual_task(request)
            ]  # Depende de todos os outros agentes
        )
    
    def create_crew(self, request: ContentRequest) -> Crew:
        """Cria o crew com todos os agentes e tarefas"""
        tasks = [
            self.create_research_task(request),
            self.create_writing_task(request),
            self.create_visual_task(request),
            self.create_editing_task(request)
        ]
        
        crew = Crew(
            agents=list(self._agents.values()),
            tasks=tasks,
            verbose=True,
            process=None,  # Sequencial por padrão
            max_rpm=10,  # Limitar requisições por minuto
            memory=False,  # Desabilitado por enquanto
            planning=False  # Desabilitado por enquanto
        )
        
        self.logger.info("🚀 Crew criado com 4 agentes e tarefas sequenciais")
        return crew
    
    async def execute_content_creation(self, request: ContentRequest) -> CrewResult:
        """Executa o processo completo de criação de conteúdo"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🎬 Iniciando criação de conteúdo: {request.topic}")
            
            # Criar crew
            crew = self.create_crew(request)
            
            # Executar crew
            result = crew.kickoff()
            
            # Calcular tempo total
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # Parsear resultado
            crew_result = CrewResult(
                request=request,
                success=True,
                final_content=str(result),
                agent_results=[],  # TODO: Extrair resultados individuais
                total_execution_time=total_time,
                approval_status="pending",  # TODO: Extrair do resultado do editor
                revision_feedback=None
            )
            
            self.logger.info(f"✅ Conteúdo criado com sucesso em {total_time:.2f}s")
            return crew_result
            
        except Exception as e:
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            error_result = CrewResult(
                request=request,
                success=False,
                final_content="",
                agent_results=[],
                total_execution_time=total_time,
                approval_status="error",
                revision_feedback=str(e)
            )
            
            self.logger.error(f"❌ Erro na criação de conteúdo: {e}")
            return error_result
    
    def get_agent_status(self) -> Dict[str, bool]:
        """Retorna status de todos os agentes"""
        return {
            name: agent is not None 
            for name, agent in self._agents.items()
        }
    
    def get_agents_info(self) -> Dict[str, Dict[str, str]]:
        """Retorna informações detalhadas dos agentes"""
        info = {}
        
        configs = {
            "researcher": self.researcher_config,
            "writer": self.writer_config,
            "visual": self.visual_config,
            "editor": self.editor_config
        }
        
        for name, config in configs.items():
            info[name] = {
                "name": config.name,
                "role": config.role,
                "goal": config.goal,
                "llm_provider": config.llm_config.provider,
                "llm_model": config.llm_config.model,
                "max_iter": config.max_iter,
                "status": "✅ Ativo" if name in self._agents else "❌ Inativo"
            }
        
        return info

# Instância global do sistema de agentes
social_agents = SocialMediaAgents()

# Funções de conveniência
async def create_content(
    topic: str,
    platforms: List[str] = ["instagram", "whatsapp", "linkedin"],
    target_audience: str = "Público geral",
    objective: str = "Engajamento e compartilhamento",
    tone: Optional[str] = None,
    special_instructions: Optional[str] = None
) -> CrewResult:
    """Função de conveniência para criar conteúdo"""
    request = ContentRequest(
        topic=topic,
        platforms=platforms,
        target_audience=target_audience,
        objective=objective,
        tone=tone,
        special_instructions=special_instructions
    )
    
    return await social_agents.execute_content_creation(request)

def get_agents_status() -> Dict[str, bool]:
    """Função de conveniência para verificar status dos agentes"""
    return social_agents.get_agent_status()

def get_agents_info() -> Dict[str, Dict[str, str]]:
    """Função de conveniência para obter informações dos agentes"""
    return social_agents.get_agents_info()
