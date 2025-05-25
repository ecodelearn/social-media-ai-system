#!/usr/bin/env python3
"""
Testes dos Agentes - Social Media AI System

Este módulo contém testes abrangentes para validar o funcionamento
dos 4 agentes especializados e suas interações.

Testes incluem:
- Inicialização dos agentes
- Execução individual de tarefas
- Integração entre agentes
- Validação de outputs
- Performance e qualidade

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - Fase 3
"""

import pytest
import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import time

# Configurar logging para testes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports do sistema
from config.settings import SystemSettings
from core.agents import (
    SocialMediaAgents,
    ContentRequest,
    CrewResult,
    AgentResult,
    social_agents,
    create_content
)
from core.llm_manager import llm_manager

class TestSocialMediaAgents:
    """Testes para o sistema de agentes"""
    
    @pytest.fixture
    def sample_request(self) -> ContentRequest:
        """Solicitação de exemplo para testes"""
        return ContentRequest(
            topic="Inteligência Artificial no Marketing Digital",
            platforms=["instagram", "linkedin"],
            target_audience="Profissionais de marketing e empreendedores",
            objective="Educar sobre IA e gerar leads",
            tone="Profissional e inspirador",
            special_instructions="Inclua estatísticas recentes e casos de sucesso"
        )
    
    @pytest.fixture
    def simple_request(self) -> ContentRequest:
        """Solicitação simples para testes rápidos"""
        return ContentRequest(
            topic="Dicas de produtividade",
            platforms=["whatsapp"],
            target_audience="Público geral",
            objective="Engajamento",
            tone="Casual"
        )
    
    def test_agents_initialization(self):
        """Testa inicialização do sistema de agentes"""
        logger.info("🧪 Testando inicialização dos agentes...")
        
        # Verificar se o sistema foi inicializado
        assert social_agents is not None
        
        # Verificar status dos agentes
        status = social_agents.get_agent_status()
        assert isinstance(status, dict)
        assert len(status) == 4
        
        # Verificar agentes específicos
        expected_agents = ["researcher", "writer", "visual", "editor"]
        for agent_name in expected_agents:
            assert agent_name in status
            assert status[agent_name] is True, f"Agente {agent_name} não está ativo"
        
        logger.info("✅ Agentes inicializados corretamente")
    
    def test_agents_info(self):
        """Testa obtenção de informações dos agentes"""
        logger.info("🧪 Testando informações dos agentes...")
        
        info = social_agents.get_agents_info()
        assert isinstance(info, dict)
        assert len(info) == 4
        
        # Verificar estrutura das informações
        for agent_name, agent_info in info.items():
            assert "name" in agent_info
            assert "role" in agent_info
            assert "goal" in agent_info
            assert "llm_provider" in agent_info
            assert "llm_model" in agent_info
            assert "status" in agent_info
            
            # Verificar valores não vazios
            assert agent_info["name"].strip() != ""
            assert agent_info["role"].strip() != ""
            assert agent_info["goal"].strip() != ""
            assert "✅" in agent_info["status"]
        
        logger.info("✅ Informações dos agentes válidas")
    
    def test_research_task_creation(self, sample_request):
        """Testa criação de tarefa de pesquisa"""
        logger.info("🧪 Testando criação de tarefa de pesquisa...")
        
        task = social_agents.create_research_task(sample_request)
        
        # Verificar propriedades da tarefa
        assert task is not None
        assert hasattr(task, 'description')
        assert hasattr(task, 'agent')
        assert hasattr(task, 'expected_output')
        
        # Verificar conteúdo da descrição
        description = task.description.lower()
        assert sample_request.topic.lower() in description
        assert sample_request.target_audience.lower() in description
        assert "pesquisa" in description or "research" in description
        
        # Verificar agente correto
        assert task.agent == social_agents._agents["researcher"]
        
        logger.info("✅ Tarefa de pesquisa criada corretamente")
    
    def test_writing_task_creation(self, sample_request):
        """Testa criação de tarefa de redação"""
        logger.info("🧪 Testando criação de tarefa de redação...")
        
        task = social_agents.create_writing_task(sample_request)
        
        # Verificar propriedades da tarefa
        assert task is not None
        assert hasattr(task, 'description')
        assert hasattr(task, 'agent')
        assert hasattr(task, 'context')
        
        # Verificar conteúdo da descrição
        description = task.description.lower()
        assert sample_request.topic.lower() in description
        assert any(platform in description for platform in sample_request.platforms)
        
        # Verificar agente correto
        assert task.agent == social_agents._agents["writer"]
        
        # Verificar contexto (depende da pesquisa)
        assert task.context is not None
        assert len(task.context) > 0
        
        logger.info("✅ Tarefa de redação criada corretamente")
    
    def test_visual_task_creation(self, sample_request):
        """Testa criação de tarefa visual"""
        logger.info("🧪 Testando criação de tarefa visual...")
        
        task = social_agents.create_visual_task(sample_request)
        
        # Verificar propriedades da tarefa
        assert task is not None
        assert hasattr(task, 'description')
        assert hasattr(task, 'agent')
        assert hasattr(task, 'context')
        
        # Verificar conteúdo da descrição
        description = task.description.lower()
        assert sample_request.topic.lower() in description
        assert "prompt" in description or "visual" in description
        assert "dall-e" in description or "dalle" in description
        
        # Verificar agente correto
        assert task.agent == social_agents._agents["visual"]
        
        logger.info("✅ Tarefa visual criada corretamente")
    
    def test_editing_task_creation(self, sample_request):
        """Testa criação de tarefa de edição"""
        logger.info("🧪 Testando criação de tarefa de edição...")
        
        task = social_agents.create_editing_task(sample_request)
        
        # Verificar propriedades da tarefa
        assert task is not None
        assert hasattr(task, 'description')
        assert hasattr(task, 'agent')
        assert hasattr(task, 'context')
        
        # Verificar conteúdo da descrição
        description = task.description.lower()
        assert sample_request.topic.lower() in description
        assert "aprova" in description or "rejeita" in description
        assert "qualidade" in description
        
        # Verificar agente correto
        assert task.agent == social_agents._agents["editor"]
        
        # Verificar contexto (depende de todos os outros agentes)
        assert task.context is not None
        assert len(task.context) == 3  # research, writing, visual
        
        logger.info("✅ Tarefa de edição criada corretamente")
    
    def test_crew_creation(self, sample_request):
        """Testa criação do crew com todos os agentes"""
        logger.info("🧪 Testando criação do crew...")
        
        crew = social_agents.create_crew(sample_request)
        
        # Verificar propriedades do crew
        assert crew is not None
        assert hasattr(crew, 'agents')
        assert hasattr(crew, 'tasks')
        
        # Verificar número de agentes e tarefas
        assert len(crew.agents) == 4
        assert len(crew.tasks) == 4
        
        # Verificar ordem das tarefas (sequencial)
        task_agents = [task.agent for task in crew.tasks]
        expected_order = [
            social_agents._agents["researcher"],
            social_agents._agents["writer"],
            social_agents._agents["visual"],
            social_agents._agents["editor"]
        ]
        assert task_agents == expected_order
        
        logger.info("✅ Crew criado corretamente")
    
    def test_llm_assignments(self):
        """Testa atribuição correta de LLMs aos agentes"""
        logger.info("🧪 Testando atribuição de LLMs...")
        
        # Verificar mapeamento esperado
        expected_mapping = {
            "researcher": "google",  # Gemini Flash
            "writer": "google",      # Gemini Flash
            "visual": "openai",      # GPT-4o-mini
            "editor": "openai"       # GPT-4o-mini
        }
        
        for agent_name, expected_provider in expected_mapping.items():
            llm = llm_manager.get_crew_llm(agent_name)
            assert llm is not None, f"LLM não configurado para {agent_name}"
            
            # Verificar tipo do LLM baseado no provedor esperado
            llm_class_name = llm.__class__.__name__.lower()
            if expected_provider == "google":
                assert "google" in llm_class_name or "gemini" in llm_class_name
            elif expected_provider == "openai":
                assert "openai" in llm_class_name or "chatopen" in llm_class_name
        
        logger.info("✅ LLMs atribuídos corretamente")
    
    @pytest.mark.asyncio
    async def test_agent_tools_integration(self):
        """Testa integração das ferramentas dos agentes"""
        logger.info("🧪 Testando integração de ferramentas...")
        
        # Por enquanto, as ferramentas são placeholders
        # Este teste verifica se a estrutura está preparada
        
        researcher_tools = social_agents._get_researcher_tools()
        writer_tools = social_agents._get_writer_tools()
        visual_tools = social_agents._get_visual_tools()
        editor_tools = social_agents._get_editor_tools()
        
        # Verificar que retornam listas (mesmo que vazias por enquanto)
        assert isinstance(researcher_tools, list)
        assert isinstance(writer_tools, list)
        assert isinstance(visual_tools, list)
        assert isinstance(editor_tools, list)
        
        logger.info("✅ Estrutura de ferramentas preparada")
    
    def test_agent_configurations(self):
        """Testa configurações dos agentes"""
        logger.info("🧪 Testando configurações dos agentes...")
        
        # Verificar configurações carregadas
        assert hasattr(social_agents, 'researcher_config')
        assert hasattr(social_agents, 'writer_config')
        assert hasattr(social_agents, 'visual_config')
        assert hasattr(social_agents, 'editor_config')
        
        configs = [
            social_agents.researcher_config,
            social_agents.writer_config,
            social_agents.visual_config,
            social_agents.editor_config
        ]
        
        for config in configs:
            # Verificar propriedades obrigatórias
            assert hasattr(config, 'name')
            assert hasattr(config, 'role')
            assert hasattr(config, 'goal')
            assert hasattr(config, 'backstory')
            assert hasattr(config, 'max_iter')
            assert hasattr(config, 'max_execution_time')
            
            # Verificar valores válidos
            assert config.name.strip() != ""
            assert config.role.strip() != ""
            assert config.goal.strip() != ""
            assert config.max_iter > 0
            assert config.max_execution_time > 0
        
        logger.info("✅ Configurações dos agentes válidas")
    
    def test_performance_limits(self, simple_request):
        """Testa limites de performance dos agentes"""
        logger.info("🧪 Testando limites de performance...")
        
        # Verificar configurações de timeout
        configs = [
            social_agents.researcher_config,
            social_agents.writer_config,
            social_agents.visual_config,
            social_agents.editor_config
        ]
        
        for config in configs:
            # Verificar timeouts razoáveis (não muito altos)
            assert config.max_execution_time <= 300  # Max 5 minutos por agente
            assert config.max_iter <= 10  # Max 10 iterações
            
        logger.info("✅ Limites de performance adequados")

class TestAgentQuality:
    """Testes de qualidade dos agentes"""
    
    def test_agent_specialization(self):
        """Testa especialização dos agentes"""
        logger.info("🧪 Testando especialização dos agentes...")
        
        # Verificar roles únicos e especializados
        roles = [
            social_agents.researcher_config.role,
            social_agents.writer_config.role,
            social_agents.visual_config.role,
            social_agents.editor_config.role
        ]
        
        # Todos os roles devem ser únicos
        assert len(set(roles)) == 4
        
        # Verificar palavras-chave específicas de cada especialização
        researcher_role = social_agents.researcher_config.role.lower()
        assert any(word in researcher_role for word in ["pesquisa", "research", "specialist"])
        
        writer_role = social_agents.writer_config.role.lower()
        assert any(word in writer_role for word in ["redator", "writer", "copywriter", "seo"])
        
        visual_role = social_agents.visual_config.role.lower()
        assert any(word in visual_role for word in ["visual", "designer", "prompt"])
        
        editor_role = social_agents.editor_config.role.lower()
        assert any(word in editor_role for word in ["editor", "quality", "manager"])
        
        logger.info("✅ Especialização dos agentes validada")
    
    def test_goal_alignment(self):
        """Testa alinhamento dos objetivos dos agentes"""
        logger.info("🧪 Testando alinhamento de objetivos...")
        
        # Verificar que cada agente tem objetivo claro e específico
        goals = [
            social_agents.researcher_config.goal,
            social_agents.writer_config.goal,
            social_agents.visual_config.goal,
            social_agents.editor_config.goal
        ]
        
        for goal in goals:
            # Objetivos devem ser detalhados (não muito curtos)
            assert len(goal) > 50
            
            # Devem conter palavras-chave de ação
            goal_lower = goal.lower()
            action_words = ["criar", "gerar", "produzir", "analisar", "revisar", "otimizar"]
            assert any(word in goal_lower for word in action_words)
        
        logger.info("✅ Objetivos dos agentes alinhados")
    
    def test_backstory_depth(self):
        """Testa profundidade das backstories dos agentes"""
        logger.info("🧪 Testando profundidade das backstories...")
        
        backstories = [
            social_agents.researcher_config.backstory,
            social_agents.writer_config.backstory,
            social_agents.visual_config.backstory,
            social_agents.editor_config.backstory
        ]
        
        for backstory in backstories:
            # Backstories devem ser detalhadas
            assert len(backstory) > 100
            
            # Devem conter contexto profissional
            backstory_lower = backstory.lower()
            professional_words = [
                "experiência", "especialista", "anos", "profissional",
                "expert", "conhecimento", "habilidade"
            ]
            assert any(word in backstory_lower for word in professional_words)
        
        logger.info("✅ Backstories dos agentes com profundidade adequada")

class TestIntegrationFlow:
    """Testes de fluxo de integração entre agentes"""
    
    def test_task_dependencies(self, sample_request):
        """Testa dependências entre tarefas"""
        logger.info("🧪 Testando dependências entre tarefas...")
        
        # Criar tarefas
        research_task = social_agents.create_research_task(sample_request)
        writing_task = social_agents.create_writing_task(sample_request)
        visual_task = social_agents.create_visual_task(sample_request)
        editing_task = social_agents.create_editing_task(sample_request)
        
        # Verificar dependências corretas
        # Writing depende de Research
        assert writing_task.context is not None
        assert research_task in writing_task.context
        
        # Visual depende de Writing
        assert visual_task.context is not None
        assert writing_task in visual_task.context
        
        # Editing depende de todos os anteriores
        assert editing_task.context is not None
        assert len(editing_task.context) == 3
        assert research_task in editing_task.context
        assert writing_task in editing_task.context
        assert visual_task in editing_task.context
        
        logger.info("✅ Dependências entre tarefas configuradas corretamente")
    
    def test_content_flow_logic(self, sample_request):
        """Testa lógica do fluxo de conteúdo"""
        logger.info("🧪 Testando lógica do fluxo de conteúdo...")
        
        # Verificar que as plataformas são passadas corretamente
        writing_task = social_agents.create_writing_task(sample_request)
        description = writing_task.description.lower()
        
        for platform in sample_request.platforms:
            assert platform in description
        
        # Verificar instruções específicas por plataforma
        if "instagram" in sample_request.platforms:
            assert "instagram" in description
            assert "hashtag" in description
        
        if "linkedin" in sample_request.platforms:
            assert "linkedin" in description
            assert "profissional" in description
        
        if "whatsapp" in sample_request.platforms:
            assert "whatsapp" in description
        
        logger.info("✅ Lógica do fluxo de conteúdo validada")

# Utilitários para testes
class TestHelpers:
    """Helpers para execução de testes"""
    
    @staticmethod
    def create_test_requests() -> List[ContentRequest]:
        """Cria lista de solicitações de teste variadas"""
        return [
            ContentRequest(
                topic="Marketing Digital 2024",
                platforms=["instagram", "linkedin"],
                target_audience="Empreendedores",
                objective="Gerar leads"
            ),
            ContentRequest(
                topic="Produtividade no Home Office",
                platforms=["whatsapp"],
                target_audience="Trabalhadores remotos",
                objective="Engajamento"
            ),
            ContentRequest(
                topic="Sustentabilidade Empresarial",
                platforms=["linkedin"],
                target_audience="Executivos",
                objective="Conscientização",
                tone="Formal e técnico"
            ),
            ContentRequest(
                topic="Dicas de Culinária Saudável",
                platforms=["instagram", "whatsapp"],
                target_audience="Pessoas interessadas em saúde",
                objective="Compartilhamento",
                tone="Casual e amigável"
            )
        ]
    
    @staticmethod
    def validate_crew_result(result: CrewResult, request: ContentRequest) -> bool:
        """Valida resultado do crew"""
        try:
            # Verificar estrutura básica
            assert isinstance(result, CrewResult)
            assert result.request == request
            assert isinstance(result.success, bool)
            assert isinstance(result.final_content, str)
            assert isinstance(result.agent_results, list)
            assert isinstance(result.total_execution_time, float)
            assert result.approval_status in ["approved", "rejected", "pending", "error"]
            
            # Verificar conteúdo se sucesso
            if result.success:
                assert len(result.final_content) > 0
                assert result.approval_status == "approved"
            
            return True
            
        except AssertionError as e:
            logger.error(f"Validação falhou: {e}")
            return False

if __name__ == "__main__":
    # Execução direta para testes rápidos
    logger.info("🧪 Executando testes básicos dos agentes...")
    
    test_agents = TestSocialMediaAgents()
    
    # Testes básicos
    test_agents.test_agents_initialization()
    test_agents.test_agents_info()
    test_agents.test_llm_assignments()
    
    # Teste de configurações
    test_quality = TestAgentQuality()
    test_quality.test_agent_specialization()
    
    logger.info("✅ Testes básicos concluídos com sucesso!")
    
    # Para executar todos os testes: pytest tests/test_agents.py -v
