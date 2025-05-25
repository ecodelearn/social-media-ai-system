#!/usr/bin/env python3
"""
Testes de Workflows - Social Media AI System

Este módulo contém testes abrangentes para validar o funcionamento
dos workflows de orquestração e integração entre agentes.

Testes incluem:
- Criação e configuração de workflows
- Execução de workflows completos
- Sistema de recomendação de workflows
- Métricas e estatísticas
- Integração com orquestrador

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
from core.agents import ContentRequest, CrewResult, AgentResult
from core.orchestrator import (
    ContentOrchestrator,
    OrchestrationStatus,
    ApprovalDecision,
    ExecutionContext,
    content_orchestrator,
    create_content_orchestrated
)
from core.workflows import (
    WorkflowManager,
    WorkflowType,
    WorkflowStep,
    WorkflowConfig,
    WorkflowExecution,
    workflow_manager,
    get_recommended_workflow,
    get_available_workflows,
    create_custom_workflow
)

class TestWorkflowManager:
    """Testes para o gerenciador de workflows"""
    
    @pytest.fixture
    def sample_request(self) -> ContentRequest:
        """Solicitação de exemplo para testes"""
        return ContentRequest(
            topic="Estratégias de Marketing Digital 2024",
            platforms=["instagram", "linkedin"],
            target_audience="Profissionais de marketing e empreendedores",
            objective="Educar e gerar leads qualificados",
            tone="Profissional e inspirador",
            special_instructions="Inclua estatísticas recentes, tendências e casos práticos"
        )
    
    @pytest.fixture
    def urgent_request(self) -> ContentRequest:
        """Solicitação urgente para testes"""
        return ContentRequest(
            topic="Comunicado sobre nova funcionalidade",
            platforms=["whatsapp"],
            target_audience="Usuários existentes",
            objective="Informar rapidamente",
            tone="Direto e claro",
            deadline=datetime.now() + timedelta(hours=1)
        )
    
    @pytest.fixture
    def premium_request(self) -> ContentRequest:
        """Solicitação premium para testes"""
        return ContentRequest(
            topic="Lançamento oficial da campanha premium da marca",
            platforms=["instagram", "linkedin", "facebook"],
            target_audience="Clientes premium e prospects qualificados",
            objective="Maximizar conversões e impacto da marca",
            tone="Premium e exclusivo",
            special_instructions="Campanha estratégica com múltiplas validações e alta qualidade visual"
        )
    
    def test_workflow_manager_initialization(self):
        """Testa inicialização do gerenciador de workflows"""
        logger.info("🧪 Testando inicialização do WorkflowManager...")
        
        # Verificar se foi inicializado
        assert workflow_manager is not None
        
        # Verificar workflows predefinidos
        assert len(workflow_manager.predefined_workflows) == 3
        assert WorkflowType.STANDARD in workflow_manager.predefined_workflows
        assert WorkflowType.EXPRESS in workflow_manager.predefined_workflows
        assert WorkflowType.PREMIUM in workflow_manager.predefined_workflows
        
        # Verificar estruturas internas
        assert isinstance(workflow_manager.custom_workflows, dict)
        assert isinstance(workflow_manager.active_executions, dict)
        assert isinstance(workflow_manager.workflow_stats, dict)
        
        logger.info("✅ WorkflowManager inicializado corretamente")
    
    def test_predefined_workflows_creation(self):
        """Testa criação dos workflows predefinidos"""
        logger.info("🧪 Testando workflows predefinidos...")
        
        workflows = workflow_manager.predefined_workflows
        
        # Testar Standard Workflow
        standard = workflows[WorkflowType.STANDARD]
        assert standard.name == "Standard Content Creation"
        assert len(standard.steps) == 4
        assert standard.estimated_time == 180
        assert standard.quality_level == "standard"
        assert "instagram" in standard.platforms_supported
        
        # Testar Express Workflow
        express = workflows[WorkflowType.EXPRESS]
        assert express.name == "Express Content Creation"
        assert len(express.steps) == 2
        assert standard.estimated_time > express.estimated_time
        assert express.quality_level == "basic"
        
        # Testar Premium Workflow
        premium = workflows[WorkflowType.PREMIUM]
        assert premium.name == "Premium Content Creation"
        assert len(premium.steps) >= 4
        assert premium.estimated_time >= standard.estimated_time
        assert premium.quality_level == "premium"
        
        logger.info("✅ Workflows predefinidos criados corretamente")
    
    def test_workflow_steps_configuration(self):
        """Testa configuração dos passos dos workflows"""
        logger.info("🧪 Testando configuração dos passos...")
        
        workflows = workflow_manager.predefined_workflows
        
        # Standard deve ter sequência completa
        standard_steps = workflows[WorkflowType.STANDARD].steps
        expected_standard = [
            WorkflowStep.RESEARCH,
            WorkflowStep.WRITING,
            WorkflowStep.VISUAL,
            WorkflowStep.EDITING
        ]
        assert standard_steps == expected_standard
        
        # Express deve ser minimalista
        express_steps = workflows[WorkflowType.EXPRESS].steps
        assert WorkflowStep.WRITING in express_steps
        assert WorkflowStep.EDITING in express_steps
        assert WorkflowStep.RESEARCH not in express_steps
        
        # Premium deve ter passos extras
        premium_steps = workflows[WorkflowType.PREMIUM].steps
        assert len(premium_steps) > len(standard_steps)
        assert WorkflowStep.VALIDATION in premium_steps or WorkflowStep.REVIEW in premium_steps
        
        logger.info("✅ Passos dos workflows configurados corretamente")
    
    def test_workflow_recommendation_logic(self, sample_request, urgent_request, premium_request):
        """Testa lógica de recomendação de workflows"""
        logger.info("🧪 Testando lógica de recomendação...")
        
        # Teste com prioridade balanceada
        balanced_workflow = workflow_manager.get_recommended_workflow(sample_request, "balanced")
        assert balanced_workflow.name == "Standard Content Creation"
        
        # Teste com prioridade de velocidade
        speed_workflow = workflow_manager.get_recommended_workflow(urgent_request, "speed")
        assert speed_workflow.quality_level in ["basic", "standard"]
        assert speed_workflow.estimated_time <= 120
        
        # Teste com prioridade de qualidade
        quality_workflow = workflow_manager.get_recommended_workflow(premium_request, "quality")
        assert quality_workflow.quality_level in ["standard", "premium"]
        
        logger.info("✅ Lógica de recomendação funcionando")
    
    def test_content_complexity_calculation(self):
        """Testa cálculo de complexidade do conteúdo"""
        logger.info("🧪 Testando cálculo de complexidade...")
        
        # Conteúdo simples
        simple_request = ContentRequest(
            topic="Dica rápida",
            platforms=["whatsapp"],
            target_audience="Geral",
            objective="Compartilhar"
        )
        simple_complexity = workflow_manager._calculate_content_complexity(simple_request)
        assert 0.0 <= simple_complexity <= 0.4
        
        # Conteúdo complexo
        complex_request = ContentRequest(
            topic="Análise estratégica detalhada de research científico e comparativo técnico",
            platforms=["instagram", "linkedin", "facebook", "twitter"],
            target_audience="Especialistas em múltiplas áreas",
            objective="Educação técnica avançada",
            special_instructions="Inclua análises estatísticas detalhadas com múltiplas referências e estudos comparativos entre diferentes metodologias de pesquisa aplicada"
        )
        complex_complexity = workflow_manager._calculate_content_complexity(complex_request)
        assert 0.6 <= complex_complexity <= 1.0
        
        logger.info("✅ Cálculo de complexidade funcionando")
    
    def test_urgency_calculation(self):
        """Testa cálculo de urgência"""
        logger.info("🧪 Testando cálculo de urgência...")
        
        # Sem deadline (urgência padrão)
        no_deadline = ContentRequest(
            topic="Teste",
            platforms=["instagram"],
            target_audience="Teste",
            objective="Teste"
        )
        default_urgency = workflow_manager._calculate_urgency(no_deadline)
        assert default_urgency == 0.3
        
        # Muito urgente (1 hora)
        very_urgent = ContentRequest(
            topic="Teste",
            platforms=["instagram"],
            target_audience="Teste",
            objective="Teste",
            deadline=datetime.now() + timedelta(minutes=30)
        )
        high_urgency = workflow_manager._calculate_urgency(very_urgent)
        assert high_urgency >= 0.8
        
        # Não urgente (1 semana)
        not_urgent = ContentRequest(
            topic="Teste",
            platforms=["instagram"],
            target_audience="Teste",
            objective="Teste",
            deadline=datetime.now() + timedelta(days=7)
        )
        low_urgency = workflow_manager._calculate_urgency(not_urgent)
        assert low_urgency <= 0.3
        
        logger.info("✅ Cálculo de urgência funcionando")
    
    def test_quality_requirement_assessment(self):
        """Testa avaliação de requisito de qualidade"""
        logger.info("🧪 Testando avaliação de qualidade...")
        
        # Baixa qualidade
        basic_request = ContentRequest(
            topic="Post casual",
            platforms=["whatsapp"],
            target_audience="Amigos",
            objective="Diversão"
        )
        basic_quality = workflow_manager._assess_quality_requirement(basic_request)
        assert basic_quality <= 0.6
        
        # Alta qualidade
        premium_request = ContentRequest(
            topic="Lançamento oficial da campanha premium corporativa da marca",
            platforms=["linkedin", "instagram"],
            target_audience="Executivos C-level",
            objective="Maximizar conversões estratégicas",
            special_instructions="Campanha profissional premium para lançamento oficial"
        )
        premium_quality = workflow_manager._assess_quality_requirement(premium_request)
        assert premium_quality >= 0.7
        
        logger.info("✅ Avaliação de qualidade funcionando")
    
    def test_custom_workflow_creation(self):
        """Testa criação de workflow customizado"""
        logger.info("🧪 Testando criação de workflow customizado...")
        
        # Criar workflow customizado
        custom_id = workflow_manager.create_custom_workflow(
            name="Workflow de Teste",
            description="Workflow criado para testes",
            steps=[WorkflowStep.RESEARCH, WorkflowStep.WRITING],
            agents_required=["researcher", "writer"],
            estimated_time=90,
            quality_level="standard",
            platforms_supported=["instagram", "whatsapp"],
            use_cases=["Teste automatizado"]
        )
        
        # Verificar se foi criado
        assert custom_id.startswith("custom_")
        assert custom_id in workflow_manager.custom_workflows
        
        # Verificar configuração
        custom_workflow = workflow_manager.custom_workflows[custom_id]
        assert custom_workflow.name == "Workflow de Teste"
        assert len(custom_workflow.steps) == 2
        assert custom_workflow.estimated_time == 90
        
        logger.info("✅ Workflow customizado criado")
    
    def test_workflow_recommendations_list(self, sample_request):
        """Testa lista de recomendações de workflows"""
        logger.info("🧪 Testando lista de recomendações...")
        
        recommendations = workflow_manager.get_workflow_recommendations(sample_request)
        
        # Verificar estrutura
        assert isinstance(recommendations, list)
        assert len(recommendations) == 3  # Standard, Express, Premium
        
        # Verificar ordenação por score
        scores = [rec["suitability_score"] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
        
        # Verificar estrutura de cada recomendação
        for rec in recommendations:
            assert "workflow_type" in rec
            assert "config" in rec
            assert "suitability_score" in rec
            assert "estimated_time" in rec
            assert "quality_level" in rec
            assert "platforms_supported" in rec
            
            # Verificar valores válidos
            assert 0.0 <= rec["suitability_score"] <= 1.0
            assert rec["estimated_time"] > 0
        
        logger.info("✅ Lista de recomendações funcionando")
    
    def test_workflow_suitability_calculation(self, sample_request):
        """Testa cálculo de adequação de workflow"""
        logger.info("🧪 Testando cálculo de adequação...")
        
        # Testar adequação do Standard
        standard_config = workflow_manager.predefined_workflows[WorkflowType.STANDARD]
        standard_score = workflow_manager._calculate_workflow_suitability(standard_config, sample_request)
        
        # Testar adequação do Express
        express_config = workflow_manager.predefined_workflows[WorkflowType.EXPRESS]
        express_score = workflow_manager._calculate_workflow_suitability(express_config, sample_request)
        
        # Verificar que scores são válidos
        assert 0.0 <= standard_score <= 1.0
        assert 0.0 <= express_score <= 1.0
        
        # Para uma solicitação balanceada, Standard deve ter score alto
        assert standard_score >= 0.5
        
        logger.info("✅ Cálculo de adequação funcionando")

class TestWorkflowExecution:
    """Testes de execução de workflows"""
    
    @pytest.fixture
    def simple_request(self) -> ContentRequest:
        """Solicitação simples para testes de execução"""
        return ContentRequest(
            topic="Dicas de produtividade para trabalho remoto",
            platforms=["whatsapp"],
            target_audience="Profissionais remotos",
            objective="Compartilhar conhecimento útil"
        )
    
    def test_workflow_execution_creation(self, simple_request):
        """Testa criação de execução de workflow"""
        logger.info("🧪 Testando criação de execução...")
        
        # Obter workflow recomendado
        workflow_config = workflow_manager.get_recommended_workflow(simple_request)
        
        # Criar contexto de execução
        context = ExecutionContext(
            request=simple_request,
            status=OrchestrationStatus.IDLE
        )
        
        # Iniciar execução
        execution_id = workflow_manager.start_workflow_execution(workflow_config, context)
        
        # Verificar se foi criado
        assert execution_id.startswith("wf_")
        assert execution_id in workflow_manager.active_executions
        
        # Verificar estrutura da execução
        execution = workflow_manager.active_executions[execution_id]
        assert execution.workflow_id == execution_id
        assert execution.config == workflow_config
        assert execution.context == context
        assert execution.start_time is not None
        assert execution.estimated_completion is not None
        
        logger.info("✅ Execução de workflow criada")
    
    def test_workflow_progress_tracking(self, simple_request):
        """Testa acompanhamento de progresso"""
        logger.info("🧪 Testando acompanhamento de progresso...")
        
        # Criar execução
        workflow_config = workflow_manager.get_recommended_workflow(simple_request)
        context = ExecutionContext(request=simple_request, status=OrchestrationStatus.IDLE)
        execution_id = workflow_manager.start_workflow_execution(workflow_config, context)
        
        # Verificar progresso inicial
        progress = workflow_manager.get_workflow_progress(execution_id)
        assert progress is not None
        assert progress["execution_id"] == execution_id
        assert progress["progress_percentage"] == 0.0
        assert progress["total_steps"] == len(workflow_config.steps)
        
        # Simular conclusão de um passo
        if workflow_config.steps:
            first_step = workflow_config.steps[0]
            mock_result = AgentResult(
                agent_name="test",
                success=True,
                content="Resultado de teste",
                metadata={},
                execution_time=1.0
            )
            
            workflow_manager.complete_workflow_step(execution_id, first_step, mock_result)
            
            # Verificar progresso atualizado
            updated_progress = workflow_manager.get_workflow_progress(execution_id)
            assert updated_progress["progress_percentage"] > 0.0
            assert len(updated_progress["completed_steps"]) == 1
        
        logger.info("✅ Acompanhamento de progresso funcionando")
    
    def test_workflow_step_completion(self, simple_request):
        """Testa conclusão de passos do workflow"""
        logger.info("🧪 Testando conclusão de passos...")
        
        # Criar execução
        workflow_config = workflow_manager.get_recommended_workflow(simple_request)
        context = ExecutionContext(request=simple_request, status=OrchestrationStatus.IDLE)
        execution_id = workflow_manager.start_workflow_execution(workflow_config, context)
        
        execution = workflow_manager.active_executions[execution_id]
        initial_completed = len(execution.completed_steps)
        
        # Simular conclusão de passo
        if workflow_config.steps:
            step = workflow_config.steps[0]
            result = AgentResult(
                agent_name="test_agent",
                success=True,
                content="Conteúdo de teste",
                metadata={"test": True},
                execution_time=2.5
            )
            
            workflow_manager.complete_workflow_step(execution_id, step, result)
            
            # Verificar que o passo foi marcado como concluído
            assert len(execution.completed_steps) == initial_completed + 1
            assert step in execution.completed_steps
            assert step.value in execution.step_results
            assert execution.step_results[step.value] == result
        
        logger.info("✅ Conclusão de passos funcionando")

class TestWorkflowIntegration:
    """Testes de integração entre workflows e orquestrador"""
    
    @pytest.fixture
    def integration_request(self) -> ContentRequest:
        """Solicitação para testes de integração"""
        return ContentRequest(
            topic="Benefícios da automação no marketing",
            platforms=["instagram", "linkedin"],
            target_audience="Profissionais de marketing",
            objective="Educar sobre automação"
        )
    
    def test_orchestrator_initialization(self):
        """Testa inicialização do orquestrador"""
        logger.info("🧪 Testando inicialização do orquestrador...")
        
        # Verificar se foi inicializado
        assert content_orchestrator is not None
        
        # Verificar configurações
        assert hasattr(content_orchestrator, 'max_concurrent_executions')
        assert hasattr(content_orchestrator, 'default_timeout')
        assert hasattr(content_orchestrator, 'quality_threshold')
        
        # Verificar estruturas internas
        assert isinstance(content_orchestrator.active_executions, dict)
        assert isinstance(content_orchestrator.execution_history, list)
        assert hasattr(content_orchestrator, 'metrics')
        
        logger.info("✅ Orquestrador inicializado corretamente")
    
    def test_workflow_orchestrator_integration(self, integration_request):
        """Testa integração entre workflow e orquestrador"""
        logger.info("🧪 Testando integração workflow-orquestrador...")
        
        # Obter workflow recomendado
        recommended = get_recommended_workflow(integration_request)
        assert recommended is not None
        
        # Verificar que o workflow é adequado para a solicitação
        assert any(platform in recommended.platforms_supported for platform in integration_request.platforms)
        
        # Verificar disponibilidade de workflows
        available = get_available_workflows()
        assert isinstance(available, dict)
        assert len(available) >= 3  # Pelo menos os 3 predefinidos
        
        logger.info("✅ Integração workflow-orquestrador funcionando")
    
    def test_workflow_selection_logic(self):
        """Testa lógica de seleção de workflows"""
        logger.info("🧪 Testando lógica de seleção...")
        
        # Casos de teste para diferentes cenários
        test_cases = [
            {
                "request": ContentRequest(
                    topic="Post rápido",
                    platforms=["whatsapp"],
                    target_audience="Geral",
                    objective="Comunicação rápida",
                    deadline=datetime.now() + timedelta(minutes=30)
                ),
                "expected_quality": "basic",
                "max_time": 90
            },
            {
                "request": ContentRequest(
                    topic="Estratégia de marca premium para campanha oficial",
                    platforms=["instagram", "linkedin"],
                    target_audience="Executivos e investidores",
                    objective="Maximizar impacto da marca e conversões estratégicas",
                    special_instructions="Campanha premium com alta qualidade visual e múltiplas validações"
                ),
                "expected_quality": "premium",
                "min_steps": 4
            }
        ]
        
        for case in test_cases:
            workflow = get_recommended_workflow(case["request"])
            
            if "expected_quality" in case:
                assert workflow.quality_level == case["expected_quality"]
            
            if "max_time" in case:
                assert workflow.estimated_time <= case["max_time"]
            
            if "min_steps" in case:
                assert len(workflow.steps) >= case["min_steps"]
        
        logger.info("✅ Lógica de seleção validada")

class TestWorkflowStatistics:
    """Testes de estatísticas e métricas de workflows"""
    
    def test_workflow_stats_initialization(self):
        """Testa inicialização das estatísticas"""
        logger.info("🧪 Testando inicialização de estatísticas...")
        
        # Verificar estrutura inicial
        stats = workflow_manager.get_workflow_stats()
        assert isinstance(stats, dict)
        
        # Por ser sistema novo, pode estar vazio
        # Mas estrutura deve estar preparada
        
        logger.info("✅ Estatísticas inicializadas")
    
    def test_workflow_stats_structure(self):
        """Testa estrutura das estatísticas"""
        logger.info("🧪 Testando estrutura de estatísticas...")
        
        # Simular atualização de estatísticas
        test_execution = WorkflowExecution(
            workflow_id="test_123",
            config=workflow_manager.predefined_workflows[WorkflowType.STANDARD],
            context=ExecutionContext(
                request=ContentRequest(
                    topic="Teste",
                    platforms=["instagram"],
                    target_audience="Teste",
                    objective="Teste"
                ),
                status=OrchestrationStatus.IDLE
            ),
            start_time=datetime.now()
        )
        
        test_result = CrewResult(
            request=test_execution.context.request,
            success=True,
            final_content="Conteúdo de teste",
            agent_results=[],
            total_execution_time=120.0,
            approval_status="approved"
        )
        
        # Atualizar estatísticas
        workflow_manager._update_workflow_stats(test_execution, test_result)
        
        # Verificar estrutura criada
        stats = workflow_manager.get_workflow_stats()
        
        if "Standard Content Creation" in stats:
            workflow_stats = stats["Standard Content Creation"]
            expected_keys = [
                "total_executions",
                "successful_executions",
                "avg_execution_time",
                "avg_quality_score",
                "platform_usage",
                "use_case_performance"
            ]
            
            for key in expected_keys:
                assert key in workflow_stats
        
        logger.info("✅ Estrutura de estatísticas validada")

# Funções de utilidade para testes
class TestWorkflowUtils:
    """Utilitários para testes de workflows"""
    
    @staticmethod
    def create_test_workflow_config() -> WorkflowConfig:
        """Cria configuração de workflow para testes"""
        return WorkflowConfig(
            name="Test Workflow",
            description="Workflow criado para testes unitários",
            steps=[WorkflowStep.WRITING, WorkflowStep.EDITING],
            agents_required=["writer", "editor"],
            estimated_time=60,
            quality_level="basic",
            platforms_supported=["whatsapp", "instagram"],
            use_cases=["Testes automatizados"],
            validation_rules={
                "min_content_length": 10,
                "max_content_length": 1000
            }
        )
    
    @staticmethod
    def create_test_requests() -> List[ContentRequest]:
        """Cria lista de solicitações variadas para testes"""
        return [
            ContentRequest(
                topic="Dica rápida de produtividade",
                platforms=["whatsapp"],
                target_audience="Trabalhadores",
                objective="Ajuda rápida"
            ),
            ContentRequest(
                topic="Análise completa de mercado e estratégias avançadas",
                platforms=["instagram", "linkedin", "facebook"],
                target_audience="Executivos e especialistas em marketing",
                objective="Educação estratégica e geração de leads qualificados",
                tone="Profissional e autoritativo",
                special_instructions="Incluir dados estatísticos, análises comparativas e recomendações estratégicas detalhadas"
            ),
            ContentRequest(
                topic="Comunicado urgente sobre atualização",
                platforms=["whatsapp", "instagram"],
                target_audience="Usuários da plataforma",
                objective="Informar rapidamente",
                deadline=datetime.now() + timedelta(hours=2)
            )
        ]
    
    @staticmethod
    def validate_workflow_recommendation(workflow: WorkflowConfig, request: ContentRequest) -> bool:
        """Valida se um workflow é adequado para uma solicitação"""
        try:
            # Verificar suporte às plataformas
            platform_support = any(
                platform in workflow.platforms_supported 
                for platform in request.platforms
            )
            assert platform_support
            
            # Verificar que tem passos válidos
            assert len(workflow.steps) > 0
            assert len(workflow.agents_required) > 0
            
            # Verificar tempo estimado razoável
            assert 30 <= workflow.estimated_time <= 600  # Entre 30s e 10min
            
            return True
            
        except AssertionError:
            return False

if __name__ == "__main__":
    # Execução direta para testes rápidos
    logger.info("🧪 Executando testes básicos de workflows...")
    
    test_manager = TestWorkflowManager()
    
    # Testes básicos
    test_manager.test_workflow_manager_initialization()
    test_manager.test_predefined_workflows_creation()
    test_manager.test_workflow_steps_configuration()
    
    # Teste de integração
    test_integration = TestWorkflowIntegration()
    test_integration.test_orchestrator_initialization()
    
    logger.info("✅ Testes básicos de workflows concluídos!")
    
    # Para executar todos os testes: pytest tests/test_workflows.py -v
