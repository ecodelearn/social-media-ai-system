#!/usr/bin/env python3
"""
Orquestrador Principal - Social Media AI System

Este módulo implementa o orquestrador principal que coordena os 4 agentes
especializados usando CrewAI, gerencia o fluxo de aprovação e implementa
o sistema de feedback entre agentes.

Funcionalidades:
- Coordenação sequencial dos 4 agentes
- Sistema de aprovação/rejeição do Editor
- Feedback loop entre agentes
- Métricas de qualidade e performance
- Retry automático com melhorias

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - Fase 3
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# CrewAI Imports
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logging.warning("CrewAI não disponível")

from config.settings import SystemSettings
from core.agents import (
    SocialMediaAgents, 
    ContentRequest, 
    CrewResult, 
    AgentResult,
    social_agents
)
from core.llm_manager import llm_manager

class OrchestrationStatus(Enum):
    """Status da orquestração"""
    IDLE = "idle"
    RESEARCH = "research"
    WRITING = "writing"  
    VISUAL = "visual"
    EDITING = "editing"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"
    RETRY = "retry"

class ApprovalDecision(Enum):
    """Decisões de aprovação do Editor"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    PENDING = "pending"

@dataclass
class OrchestrationMetrics:
    """Métricas da orquestração"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time: float = 0.0
    avg_retries: float = 0.0
    approval_rate: float = 0.0
    agent_performance: Dict[str, float] = field(default_factory=dict)
    cost_tracking: Dict[str, float] = field(default_factory=dict)

@dataclass
class QualityFeedback:
    """Feedback de qualidade entre agentes"""
    from_agent: str
    to_agent: str
    feedback_type: str  # "improvement", "error", "suggestion"
    message: str
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime
    resolved: bool = False

@dataclass
class ExecutionContext:
    """Contexto de execução da orquestração"""
    request: ContentRequest
    status: OrchestrationStatus
    current_agent: Optional[str] = None
    start_time: Optional[datetime] = None
    agent_results: List[AgentResult] = field(default_factory=list)
    feedback_history: List[QualityFeedback] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    approval_decision: ApprovalDecision = ApprovalDecision.PENDING
    editor_feedback: Optional[str] = None

class ContentOrchestrator:
    """Orquestrador principal do sistema de criação de conteúdo"""
    
    def __init__(self):
        """Inicializa o orquestrador"""
        self.logger = logging.getLogger(__name__)
        
        if not CREWAI_AVAILABLE:
            raise RuntimeError("CrewAI não está disponível. Execute: pip install crewai")
        
        # Configurações
        self.max_concurrent_executions = SystemSettings.ORCHESTRATOR_CONFIG.max_concurrent_executions
        self.default_timeout = SystemSettings.ORCHESTRATOR_CONFIG.execution_timeout
        self.quality_threshold = SystemSettings.ORCHESTRATOR_CONFIG.quality_threshold
        
        # Estado interno
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.execution_history: List[ExecutionContext] = []
        self.metrics = OrchestrationMetrics()
        
        # Sistema de agentes
        self.agents_system = social_agents
        
        # Feedback system
        self.feedback_processors = {
            "research_to_writing": self._process_research_feedback,
            "writing_to_visual": self._process_writing_feedback,
            "visual_to_editing": self._process_visual_feedback,
            "editing_to_all": self._process_editor_feedback
        }
        
        self.logger.info("🎬 Orquestrador de Conteúdo inicializado")
    
    async def create_content(
        self,
        request: ContentRequest,
        execution_id: Optional[str] = None
    ) -> CrewResult:
        """
        Ponto de entrada principal para criação de conteúdo
        
        Args:
            request: Solicitação de conteúdo
            execution_id: ID único da execução (opcional)
            
        Returns:
            CrewResult: Resultado completo da execução
        """
        if execution_id is None:
            execution_id = f"exec_{int(time.time())}_{hash(request.topic) % 10000}"
        
        # Verificar limite de execuções concorrentes
        if len(self.active_executions) >= self.max_concurrent_executions:
            raise RuntimeError(
                f"Limite de execuções concorrentes excedido: "
                f"{len(self.active_executions)}/{self.max_concurrent_executions}"
            )
        
        # Criar contexto de execução
        context = ExecutionContext(
            request=request,
            status=OrchestrationStatus.IDLE,
            start_time=datetime.now()
        )
        
        self.active_executions[execution_id] = context
        
        try:
            self.logger.info(
                f"🚀 Iniciando criação de conteúdo [ID: {execution_id}]: {request.topic}"
            )
            
            # Executar fluxo principal
            result = await self._execute_orchestration_flow(execution_id, context)
            
            # Atualizar métricas
            self._update_metrics(context, result)
            
            # Mover para histórico
            self.execution_history.append(context)
            del self.active_executions[execution_id]
            
            self.logger.info(
                f"✅ Conteúdo criado com sucesso [ID: {execution_id}]: "
                f"{result.approval_status} em {result.total_execution_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            context.status = OrchestrationStatus.ERROR
            self.logger.error(f"❌ Erro na criação de conteúdo [ID: {execution_id}]: {e}")
            
            # Criar resultado de erro
            error_result = CrewResult(
                request=request,
                success=False,
                final_content="",
                agent_results=context.agent_results,
                total_execution_time=(datetime.now() - context.start_time).total_seconds(),
                approval_status="error",
                revision_feedback=str(e)
            )
            
            # Atualizar métricas de erro
            self.metrics.failed_executions += 1
            
            # Mover para histórico
            self.execution_history.append(context)
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            return error_result
    
    async def _execute_orchestration_flow(
        self, 
        execution_id: str, 
        context: ExecutionContext
    ) -> CrewResult:
        """Executa o fluxo principal de orquestração"""
        
        retry_count = 0
        while retry_count <= context.max_retries:
            try:
                # Executar sequência de agentes
                context.status = OrchestrationStatus.RESEARCH
                research_result = await self._execute_research_phase(context)
                
                context.status = OrchestrationStatus.WRITING
                writing_result = await self._execute_writing_phase(context, research_result)
                
                context.status = OrchestrationStatus.VISUAL
                visual_result = await self._execute_visual_phase(context, writing_result)
                
                context.status = OrchestrationStatus.EDITING
                editing_result = await self._execute_editing_phase(
                    context, research_result, writing_result, visual_result
                )
                
                # Processar decisão do editor
                approval_decision = self._parse_editor_decision(editing_result)
                context.approval_decision = approval_decision
                
                if approval_decision == ApprovalDecision.APPROVED:
                    context.status = OrchestrationStatus.APPROVED
                    return self._create_final_result(context, editing_result)
                
                elif approval_decision == ApprovalDecision.REJECTED:
                    context.status = OrchestrationStatus.REJECTED
                    
                    if retry_count >= context.max_retries:
                        return self._create_rejection_result(context, editing_result)
                    
                    # Processar feedback e tentar novamente
                    await self._process_rejection_feedback(context, editing_result)
                    retry_count += 1
                    context.retry_count = retry_count
                    context.status = OrchestrationStatus.RETRY
                    
                    self.logger.info(
                        f"🔄 Tentativa {retry_count}/{context.max_retries} "
                        f"[ID: {execution_id}]: processando feedback do editor"
                    )
                    
                elif approval_decision == ApprovalDecision.NEEDS_REVISION:
                    # Implementar lógica específica de revisão
                    await self._process_revision_feedback(context, editing_result)
                    retry_count += 1
                    context.retry_count = retry_count
                    
                else:
                    raise RuntimeError("Decisão de aprovação não reconhecida")
                    
            except Exception as e:
                self.logger.error(f"Erro na execução do fluxo: {e}")
                if retry_count >= context.max_retries:
                    raise
                retry_count += 1
        
        # Se chegou aqui, excedeu tentativas
        context.status = OrchestrationStatus.REJECTED
        return self._create_max_retries_result(context)
    
    async def _execute_research_phase(self, context: ExecutionContext) -> AgentResult:
        """Executa a fase de pesquisa"""
        context.current_agent = "researcher"
        start_time = time.time()
        
        try:
            # Criar tarefa de pesquisa
            task = self.agents_system.create_research_task(context.request)
            agent = self.agents_system._agents["researcher"]
            
            # Executar tarefa
            result = agent.execute_task(task)
            
            # Criar resultado estruturado
            agent_result = AgentResult(
                agent_name="researcher",
                success=True,
                content=str(result),
                metadata={
                    "task_description": task.description,
                    "expected_output": task.expected_output
                },
                execution_time=time.time() - start_time
            )
            
            context.agent_results.append(agent_result)
            
            self.logger.info(
                f"🔍 Fase de pesquisa concluída em {agent_result.execution_time:.2f}s"
            )
            
            return agent_result
            
        except Exception as e:
            agent_result = AgentResult(
                agent_name="researcher",
                success=False,
                content="",
                metadata={},
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
            
            context.agent_results.append(agent_result)
            raise RuntimeError(f"Erro na fase de pesquisa: {e}")
    
    async def _execute_writing_phase(
        self, 
        context: ExecutionContext, 
        research_result: AgentResult
    ) -> AgentResult:
        """Executa a fase de redação"""
        context.current_agent = "writer"
        start_time = time.time()
        
        try:
            # Criar tarefa de escrita com contexto da pesquisa
            task = self.agents_system.create_writing_task(context.request)
            agent = self.agents_system._agents["writer"]
            
            # Adicionar contexto da pesquisa
            enhanced_description = f"""
            {task.description}
            
            **CONTEXTO DA PESQUISA:**
            {research_result.content}
            
            Use essas informações para criar conteúdo mais preciso e relevante.
            """
            task.description = enhanced_description
            
            # Executar tarefa
            result = agent.execute_task(task)
            
            # Criar resultado estruturado
            agent_result = AgentResult(
                agent_name="writer",
                success=True,
                content=str(result),
                metadata={
                    "task_description": task.description,
                    "research_context": research_result.content[:500] + "...",
                    "platforms": context.request.platforms
                },
                execution_time=time.time() - start_time
            )
            
            context.agent_results.append(agent_result)
            
            # Processar feedback research -> writing
            await self._generate_inter_agent_feedback(
                "research_to_writing", research_result, agent_result, context
            )
            
            self.logger.info(
                f"✍️ Fase de redação concluída em {agent_result.execution_time:.2f}s"
            )
            
            return agent_result
            
        except Exception as e:
            agent_result = AgentResult(
                agent_name="writer",
                success=False,
                content="",
                metadata={},
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
            
            context.agent_results.append(agent_result)
            raise RuntimeError(f"Erro na fase de redação: {e}")
    
    async def _execute_visual_phase(
        self, 
        context: ExecutionContext, 
        writing_result: AgentResult
    ) -> AgentResult:
        """Executa a fase de design visual"""
        context.current_agent = "visual"
        start_time = time.time()
        
        try:
            # Criar tarefa visual com contexto da redação
            task = self.agents_system.create_visual_task(context.request)
            agent = self.agents_system._agents["visual"]
            
            # Adicionar contexto da redação
            enhanced_description = f"""
            {task.description}
            
            **CONTEÚDO TEXTUAL CRIADO:**
            {writing_result.content}
            
            Crie prompts visuais que complementem perfeitamente esse conteúdo.
            """
            task.description = enhanced_description
            
            # Executar tarefa
            result = agent.execute_task(task)
            
            # Criar resultado estruturado
            agent_result = AgentResult(
                agent_name="visual",
                success=True,
                content=str(result),
                metadata={
                    "task_description": task.description,
                    "writing_context": writing_result.content[:500] + "...",
                    "platforms": context.request.platforms
                },
                execution_time=time.time() - start_time
            )
            
            context.agent_results.append(agent_result)
            
            # Processar feedback writing -> visual
            await self._generate_inter_agent_feedback(
                "writing_to_visual", writing_result, agent_result, context
            )
            
            self.logger.info(
                f"🎨 Fase visual concluída em {agent_result.execution_time:.2f}s"
            )
            
            return agent_result
            
        except Exception as e:
            agent_result = AgentResult(
                agent_name="visual",
                success=False,
                content="",
                metadata={},
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
            
            context.agent_results.append(agent_result)
            raise RuntimeError(f"Erro na fase visual: {e}")
    
    async def _execute_editing_phase(
        self,
        context: ExecutionContext,
        research_result: AgentResult,
        writing_result: AgentResult,
        visual_result: AgentResult
    ) -> AgentResult:
        """Executa a fase de edição final"""
        context.current_agent = "editor"
        start_time = time.time()
        
        try:
            # Criar tarefa de edição com todo o contexto
            task = self.agents_system.create_editing_task(context.request)
            agent = self.agents_system._agents["editor"]
            
            # Adicionar contexto completo
            enhanced_description = f"""
            {task.description}
            
            **PESQUISA REALIZADA:**
            {research_result.content}
            
            **CONTEÚDO TEXTUAL:**
            {writing_result.content}
            
            **PROMPTS VISUAIS:**
            {visual_result.content}
            
            **FEEDBACK DE QUALIDADE:**
            {self._get_quality_feedback_summary(context)}
            
            Avalie todo o conjunto e tome uma decisão final de aprovação.
            """
            task.description = enhanced_description
            
            # Executar tarefa
            result = agent.execute_task(task)
            
            # Criar resultado estruturado
            agent_result = AgentResult(
                agent_name="editor",
                success=True,
                content=str(result),
                metadata={
                    "task_description": task.description,
                    "evaluated_agents": ["researcher", "writer", "visual"],
                    "feedback_count": len(context.feedback_history)
                },
                execution_time=time.time() - start_time
            )
            
            context.agent_results.append(agent_result)
            
            self.logger.info(
                f"🎬 Fase de edição concluída em {agent_result.execution_time:.2f}s"
            )
            
            return agent_result
            
        except Exception as e:
            agent_result = AgentResult(
                agent_name="editor",
                success=False,
                content="",
                metadata={},
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
            
            context.agent_results.append(agent_result)
            raise RuntimeError(f"Erro na fase de edição: {e}")
    
    def _parse_editor_decision(self, editing_result: AgentResult) -> ApprovalDecision:
        """Extrai a decisão de aprovação do resultado do editor"""
        content = editing_result.content.lower()
        
        if "[aprovado]" in content or "aprovado" in content.split()[:10]:
            return ApprovalDecision.APPROVED
        elif "[rejeitado]" in content or "rejeitado" in content.split()[:10]:
            return ApprovalDecision.REJECTED
        elif "[revisão necessária]" in content or "revisão" in content.split()[:10]:
            return ApprovalDecision.NEEDS_REVISION
        else:
            # Analisar contexto para inferir decisão
            if "excelente" in content or "perfeito" in content or "ótimo" in content:
                return ApprovalDecision.APPROVED
            elif "precisa melhorar" in content or "não atende" in content:
                return ApprovalDecision.NEEDS_REVISION
            else:
                return ApprovalDecision.PENDING
    
    async def _generate_inter_agent_feedback(
        self,
        feedback_type: str,
        from_result: AgentResult,
        to_result: AgentResult,
        context: ExecutionContext
    ):
        """Gera feedback entre agentes"""
        processor = self.feedback_processors.get(feedback_type)
        if processor:
            feedback = await processor(from_result, to_result, context)
            if feedback:
                context.feedback_history.append(feedback)
                self.logger.info(f"💬 Feedback {feedback_type}: {feedback.severity}")
    
    async def _process_research_feedback(
        self, 
        research: AgentResult, 
        writing: AgentResult, 
        context: ExecutionContext
    ) -> Optional[QualityFeedback]:
        """Processa feedback da pesquisa para redação"""
        # Implementar análise de qualidade
        return None  # Placeholder
    
    async def _process_writing_feedback(
        self, 
        writing: AgentResult, 
        visual: AgentResult, 
        context: ExecutionContext
    ) -> Optional[QualityFeedback]:
        """Processa feedback da redação para visual"""
        # Implementar análise de qualidade
        return None  # Placeholder
    
    async def _process_visual_feedback(
        self, 
        visual: AgentResult, 
        editing: AgentResult, 
        context: ExecutionContext
    ) -> Optional[QualityFeedback]:
        """Processa feedback visual para edição"""
        # Implementar análise de qualidade
        return None  # Placeholder
    
    async def _process_editor_feedback(
        self, 
        editing: AgentResult, 
        all_results: AgentResult, 
        context: ExecutionContext
    ) -> Optional[QualityFeedback]:
        """Processa feedback do editor para todos"""
        # Implementar análise de qualidade
        return None  # Placeholder
    
    async def _process_rejection_feedback(
        self, 
        context: ExecutionContext, 
        editing_result: AgentResult
    ):
        """Processa feedback de rejeição e prepara nova tentativa"""
        # Extrair feedback específico do editor
        context.editor_feedback = self._extract_editor_feedback(editing_result.content)
        
        # Resetar resultados para nova tentativa
        context.agent_results = []
        context.feedback_history = []
        
        self.logger.info(f"🔄 Processando feedback de rejeição: {context.editor_feedback[:100]}...")
    
    async def _process_revision_feedback(
        self, 
        context: ExecutionContext, 
        editing_result: AgentResult
    ):
        """Processa feedback para revisão específica"""
        # Similar ao rejection mas com abordagem mais focada
        await self._process_rejection_feedback(context, editing_result)
    
    def _extract_editor_feedback(self, editor_content: str) -> str:
        """Extrai feedback específico do conteúdo do editor"""
        lines = editor_content.split('\n')
        feedback_section = []
        in_feedback = False
        
        for line in lines:
            if "feedback" in line.lower() or "melhorias" in line.lower():
                in_feedback = True
            elif in_feedback and line.strip():
                feedback_section.append(line.strip())
            elif in_feedback and not line.strip():
                break
        
        return '\n'.join(feedback_section) if feedback_section else editor_content[:500]
    
    def _get_quality_feedback_summary(self, context: ExecutionContext) -> str:
        """Gera resumo do feedback de qualidade"""
        if not context.feedback_history:
            return "Nenhum feedback de qualidade registrado."
        
        summary = []
        for feedback in context.feedback_history:
            summary.append(
                f"- {feedback.from_agent} → {feedback.to_agent}: "
                f"{feedback.feedback_type} ({feedback.severity})"
            )
        
        return '\n'.join(summary)
    
    def _create_final_result(
        self, 
        context: ExecutionContext, 
        editing_result: AgentResult
    ) -> CrewResult:
        """Cria resultado final aprovado"""
        total_time = (datetime.now() - context.start_time).total_seconds()
        
        return CrewResult(
            request=context.request,
            success=True,
            final_content=editing_result.content,
            agent_results=context.agent_results,
            total_execution_time=total_time,
            approval_status="approved",
            revision_feedback=None
        )
    
    def _create_rejection_result(
        self, 
        context: ExecutionContext, 
        editing_result: AgentResult
    ) -> CrewResult:
        """Cria resultado de rejeição"""
        total_time = (datetime.now() - context.start_time).total_seconds()
        
        return CrewResult(
            request=context.request,
            success=False,
            final_content="",
            agent_results=context.agent_results,
            total_execution_time=total_time,
            approval_status="rejected",
            revision_feedback=context.editor_feedback
        )
    
    def _create_max_retries_result(self, context: ExecutionContext) -> CrewResult:
        """Cria resultado quando excede tentativas máximas"""
        total_time = (datetime.now() - context.start_time).total_seconds()
        
        return CrewResult(
            request=context.request,
            success=False,
            final_content="",
            agent_results=context.agent_results,
            total_execution_time=total_time,
            approval_status="max_retries_exceeded",
            revision_feedback=f"Excedido limite de {context.max_retries} tentativas"
        )
    
    def _update_metrics(self, context: ExecutionContext, result: CrewResult):
        """Atualiza métricas do orquestrador"""
        self.metrics.total_executions += 1
        
        if result.success:
            self.metrics.successful_executions += 1
        else:
            self.metrics.failed_executions += 1
        
        # Atualizar média de tempo de execução
        current_avg = self.metrics.avg_execution_time
        total_execs = self.metrics.total_executions
        self.metrics.avg_execution_time = (
            (current_avg * (total_execs - 1) + result.total_execution_time) / total_execs
        )
        
        # Atualizar média de retries
        current_avg_retries = self.metrics.avg_retries
        self.metrics.avg_retries = (
            (current_avg_retries * (total_execs - 1) + context.retry_count) / total_execs
        )
        
        # Atualizar taxa de aprovação
        if self.metrics.total_executions > 0:
            self.metrics.approval_rate = (
                self.metrics.successful_executions / self.metrics.total_executions
            )
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de uma execução específica"""
        if execution_id in self.active_executions:
            context = self.active_executions[execution_id]
            return {
                "id": execution_id,
                "status": context.status.value,
                "current_agent": context.current_agent,
                "retry_count": context.retry_count,
                "agents_completed": len(context.agent_results),
                "elapsed_time": (datetime.now() - context.start_time).total_seconds()
            }
        return None
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Retorna lista de execuções ativas"""
        return [
            self.get_execution_status(exec_id) 
            for exec_id in self.active_executions.keys()
        ]
    
    def get_metrics(self) -> OrchestrationMetrics:
        """Retorna métricas atuais"""
        return self.metrics
    
    def get_recent_history(self, limit: int = 10) -> List[ExecutionContext]:
        """Retorna histórico recente de execuções"""
        return sorted(
            self.execution_history,
            key=lambda x: x.start_time,
            reverse=True
        )[:limit]

# Instância global do orquestrador
content_orchestrator = ContentOrchestrator()

# Funções de conveniência
async def create_content_orchestrated(
    topic: str,
    platforms: List[str] = ["instagram", "whatsapp", "linkedin"],
    target_audience: str = "Público geral",
    objective: str = "Engajamento e compartilhamento",
    tone: Optional[str] = None,
    special_instructions: Optional[str] = None
) -> CrewResult:
    """Função de conveniência para criação orquestrada de conteúdo"""
    request = ContentRequest(
        topic=topic,
        platforms=platforms,
        target_audience=target_audience,
        objective=objective,
        tone=tone,
        special_instructions=special_instructions
    )
    
    return await content_orchestrator.create_content(request)

def get_orchestration_metrics() -> OrchestrationMetrics:
    """Função de conveniência para obter métricas"""
    return content_orchestrator.get_metrics()

def get_active_orchestrations() -> List[Dict[str, Any]]:
    """Função de conveniência para obter execuções ativas"""
    return content_orchestrator.get_active_executions()
