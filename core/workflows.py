#!/usr/bin/env python3
"""
Workflows Completos - Social Media AI System

Este módulo implementa os workflows end-to-end que conectam:
1. 🔍 Pesquisa via Perplexity MCP
2. 🤖 Criação de conteúdo via 4 agentes CrewAI
3. 📱 Envio automático via WhatsApp MCP

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - FASE 3 IMPLEMENTADA
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# CrewAI Imports
try:
    from crewai import Agent, Task, Crew, Process
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
from core.real_mcp_integrations import real_mcp_integrations
from core.mcp_integrations import MCPResponse, WhatsAppGroup
from core.whatsapp_manager import whatsapp_manager

class WorkflowStatus(Enum):
    """Status do workflow"""
    IDLE = "idle"
    RESEARCHING = "researching" 
    CREATING_CONTENT = "creating_content"
    READY_TO_SEND = "ready_to_send"
    SENDING = "sending"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class WorkflowResult:
    """Resultado completo do workflow"""
    success: bool
    content_request: ContentRequest
    perplexity_research: Optional[MCPResponse] = None
    crew_result: Optional[CrewResult] = None
    whatsapp_results: List[MCPResponse] = field(default_factory=list)
    selected_groups: List[WhatsAppGroup] = field(default_factory=list)
    execution_time: float = 0.0
    status: WorkflowStatus = WorkflowStatus.IDLE
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AutoSendConfig:
    """Configuração para envio automático"""
    enabled: bool = False
    target_groups: List[str] = field(default_factory=list)  # IDs ou nomes de grupos
    auto_select_groups: bool = True  # Selecionar grupos automaticamente
    max_groups: int = 3  # Máximo de grupos para envio automático
    require_approval: bool = True  # Requer aprovação antes do envio

class ContentWorkflow:
    """Workflow completo de criação e distribuição de conteúdo"""
    
    def __init__(self):
        """Inicializa o workflow"""
        self.logger = logging.getLogger(__name__)
        
        if not CREWAI_AVAILABLE:
            raise RuntimeError("CrewAI não está disponível")
        
        # Componentes do sistema
        self.agents_system = social_agents
        self.mcp_integrations = real_mcp_integrations
        self.whatsapp_manager = whatsapp_manager
        
        # Estado do workflow
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.workflow_history: List[WorkflowResult] = []
        
        # Configurações padrão
        self.default_auto_send = AutoSendConfig()
        
        # Estatísticas
        self.stats = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "content_created": 0,
            "messages_sent": 0,
            "avg_execution_time": 0.0
        }
        
        self.logger.info("🔄 Content Workflow System inicializado")
    
    async def execute_complete_workflow(
        self,
        topic: str,
        platforms: List[str] = ["instagram", "whatsapp", "linkedin"],
        target_audience: str = "Público geral",
        objective: str = "Engajamento e compartilhamento",
        tone: Optional[str] = None,
        special_instructions: Optional[str] = None,
        auto_send_config: Optional[AutoSendConfig] = None,
        workflow_id: Optional[str] = None
    ) -> WorkflowResult:
        """
        Executa o workflow completo end-to-end
        
        Fluxo:
        1. Pesquisa com Perplexity MCP
        2. Criação de conteúdo com 4 agentes CrewAI
        3. Envio automático via WhatsApp MCP (opcional)
        """
        if workflow_id is None:
            workflow_id = f"workflow_{int(time.time())}_{hash(topic) % 10000}"
        
        start_time = time.time()
        
        # Criar estrutura da solicitação
        content_request = ContentRequest(
            topic=topic,
            platforms=platforms,
            target_audience=target_audience,
            objective=objective,
            tone=tone,
            special_instructions=special_instructions
        )
        
        # Criar resultado do workflow
        workflow_result = WorkflowResult(
            success=False,
            content_request=content_request,
            status=WorkflowStatus.IDLE
        )
        
        self.active_workflows[workflow_id] = workflow_result
        
        try:
            self.logger.info(f"🚀 Iniciando workflow completo [ID: {workflow_id}]: {topic}")
            
            # === FASE 1: PESQUISA VIA PERPLEXITY MCP ===
            workflow_result.status = WorkflowStatus.RESEARCHING
            perplexity_result = await self._execute_research_phase(content_request)
            workflow_result.perplexity_research = perplexity_result
            
            if not perplexity_result.success:
                raise RuntimeError(f"Falha na pesquisa: {perplexity_result.error_message}")
            
            # === FASE 2: CRIAÇÃO DE CONTEÚDO VIA CREWAI ===
            workflow_result.status = WorkflowStatus.CREATING_CONTENT
            crew_result = await self._execute_content_creation_phase(
                content_request, perplexity_result
            )
            workflow_result.crew_result = crew_result
            
            if not crew_result.success:
                raise RuntimeError(f"Falha na criação de conteúdo: {crew_result.revision_feedback}")
            
            workflow_result.status = WorkflowStatus.READY_TO_SEND
            
            # === FASE 3: ENVIO VIA WHATSAPP MCP (OPCIONAL) ===
            if auto_send_config and auto_send_config.enabled:
                workflow_result.status = WorkflowStatus.SENDING
                
                # Selecionar grupos automaticamente ou usar grupos específicos
                selected_groups = await self._select_target_groups(auto_send_config)
                workflow_result.selected_groups = selected_groups
                
                if selected_groups:
                    whatsapp_results = await self._execute_distribution_phase(
                        crew_result.final_content, selected_groups
                    )
                    workflow_result.whatsapp_results = whatsapp_results
                    
                    # Verificar se pelo menos um envio foi bem-sucedido
                    successful_sends = sum(1 for result in whatsapp_results if result.success)
                    self.stats["messages_sent"] += successful_sends
                    
                    self.logger.info(f"📱 Enviado para {successful_sends}/{len(selected_groups)} grupos")
            
            # === FINALIZAÇÃO ===
            workflow_result.status = WorkflowStatus.COMPLETED
            workflow_result.success = True
            workflow_result.execution_time = time.time() - start_time
            
            # Atualizar estatísticas
            self._update_workflow_stats(workflow_result)
            
            # Mover para histórico
            self.workflow_history.append(workflow_result)
            del self.active_workflows[workflow_id]
            
            self.logger.info(
                f"✅ Workflow completo finalizado [ID: {workflow_id}] em {workflow_result.execution_time:.2f}s"
            )
            
            return workflow_result
            
        except Exception as e:
            workflow_result.status = WorkflowStatus.ERROR
            workflow_result.error_message = str(e)
            workflow_result.execution_time = time.time() - start_time
            
            self.stats["failed_workflows"] += 1
            
            self.logger.error(f"❌ Erro no workflow [ID: {workflow_id}]: {e}")
            
            # Mover para histórico mesmo com erro
            self.workflow_history.append(workflow_result)
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            return workflow_result
    
    async def _execute_research_phase(self, request: ContentRequest) -> MCPResponse:
        """Executa a fase de pesquisa usando Perplexity MCP"""
        self.logger.info("🔍 Iniciando fase de pesquisa com Perplexity...")
        
        # Construir query de pesquisa otimizada
        research_query = self._build_research_query(request)
        
        # Executar pesquisa via MCP
        result = await self.mcp_integrations.search_perplexity_real(
            query=research_query,
            detail_level="detailed"
        )
        
        if result.success:
            self.logger.info("✅ Pesquisa Perplexity concluída com sucesso")
        else:
            self.logger.error(f"❌ Falha na pesquisa Perplexity: {result.error_message}")
        
        return result
    
    async def _execute_content_creation_phase(
        self, 
        request: ContentRequest, 
        research_data: MCPResponse
    ) -> CrewResult:
        """Executa a criação de conteúdo usando os 4 agentes CrewAI"""
        self.logger.info("🤖 Iniciando criação de conteúdo com agentes CrewAI...")
        
        # Enriquecer a solicitação com dados da pesquisa
        enhanced_request = self._enhance_request_with_research(request, research_data)
        
        # Executar criação via agentes
        result = await self.agents_system.execute_content_creation(enhanced_request)
        
        if result.success:
            self.logger.info("✅ Conteúdo criado com sucesso pelos agentes")
            self.stats["content_created"] += 1
        else:
            self.logger.error(f"❌ Falha na criação de conteúdo: {result.revision_feedback}")
        
        return result
    
    async def _execute_distribution_phase(
        self, 
        content: str, 
        target_groups: List[WhatsAppGroup]
    ) -> List[MCPResponse]:
        """Executa a distribuição via WhatsApp MCP"""
        self.logger.info(f"📱 Iniciando envio para {len(target_groups)} grupos...")
        
        results = []
        
        for group in target_groups:
            try:
                self.logger.info(f"📤 Enviando para grupo: {group.name}")
                
                # Adaptar conteúdo para WhatsApp (remover hashtags, etc.)
                whatsapp_content = self._adapt_content_for_whatsapp(content)
                
                # Enviar via MCP
                send_result = await self.mcp_integrations.send_message_to_group_real(
                    group_id=group.id,
                    message=whatsapp_content
                )
                
                results.append(send_result)
                
                if send_result.success:
                    self.logger.info(f"✅ Enviado com sucesso para: {group.name}")
                else:
                    self.logger.error(f"❌ Falha no envio para: {group.name}")
                
                # Pequeno delay entre envios
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no envio para {group.name}: {e}")
                results.append(MCPResponse(
                    provider="whatsapp",
                    tool_name="send_message_to_group",
                    success=False,
                    content="",
                    error_message=str(e)
                ))
        
        successful_sends = sum(1 for r in results if r.success)
        self.logger.info(f"📊 Distribuição concluída: {successful_sends}/{len(results)} sucessos")
        
        return results
    
    async def _select_target_groups(self, config: AutoSendConfig) -> List[WhatsAppGroup]:
        """Seleciona grupos para envio baseado na configuração"""
        
        # Obter todos os grupos disponíveis
        all_groups = await self.mcp_integrations.get_whatsapp_groups_real()
        
        if not all_groups:
            self.logger.warning("⚠️ Nenhum grupo WhatsApp disponível")
            return []
        
        selected_groups = []
        
        if config.target_groups:
            # Usar grupos específicos configurados
            for target in config.target_groups:
                # Buscar por ID ou nome
                group = next(
                    (g for g in all_groups if g.id == target or g.name == target),
                    None
                )
                if group:
                    selected_groups.append(group)
                else:
                    self.logger.warning(f"⚠️ Grupo não encontrado: {target}")
        
        elif config.auto_select_groups:
            # Seleção automática inteligente
            selected_groups = self._auto_select_best_groups(all_groups, config.max_groups)
        
        self.logger.info(f"🎯 {len(selected_groups)} grupos selecionados para envio")
        return selected_groups
    
    def _auto_select_best_groups(
        self, 
        all_groups: List[WhatsAppGroup], 
        max_groups: int
    ) -> List[WhatsAppGroup]:
        """Seleção automática dos melhores grupos"""
        
        # Critérios de seleção:
        # 1. Grupos com mais participantes (maior alcance)
        # 2. Nomes que indicam boa segmentação
        # 3. Diversificar tipos de grupos
        
        # Ordenar por número de participantes
        sorted_groups = sorted(all_groups, key=lambda g: g.participants_count, reverse=True)
        
        # Selecionar os top grupos, respeitando o limite
        selected = sorted_groups[:max_groups]
        
        self.logger.info(f"🤖 Seleção automática: {[g.name for g in selected]}")
        return selected
    
    def _build_research_query(self, request: ContentRequest) -> str:
        """Constrói query otimizada para pesquisa"""
        base_query = request.topic
        
        # Adicionar contexto de redes sociais
        if "instagram" in request.platforms:
            base_query += " Instagram tendências"
        if "linkedin" in request.platforms:
            base_query += " LinkedIn profissional"
        
        # Adicionar objetivo
        if "engajamento" in request.objective.lower():
            base_query += " engajamento viral"
        
        # Adicionar ano atual para dados recentes
        current_year = datetime.now().year
        base_query += f" {current_year} atualizado"
        
        return base_query
    
    def _enhance_request_with_research(
        self, 
        request: ContentRequest, 
        research: MCPResponse
    ) -> ContentRequest:
        """Enriquece a solicitação com dados da pesquisa"""
        
        # Adicionar insights da pesquisa às instruções especiais
        enhanced_instructions = f"""
        **DADOS DE PESQUISA ATUALIZADOS:**
        {research.content}
        
        **INSTRUÇÕES ORIGINAIS:**
        {request.special_instructions or 'Criar conteúdo envolvente e profissional'}
        
        Use os dados de pesquisa para criar conteúdo mais preciso e relevante.
        """
        
        return ContentRequest(
            topic=request.topic,
            platforms=request.platforms,
            target_audience=request.target_audience,
            objective=request.objective,
            tone=request.tone,
            special_instructions=enhanced_instructions,
            deadline=request.deadline
        )
    
    def _adapt_content_for_whatsapp(self, content: str) -> str:
        """Adapta conteúdo para WhatsApp"""
        
        # Extrair apenas a parte relevante para WhatsApp
        lines = content.split('\n')
        whatsapp_content = []
        
        in_whatsapp_section = False
        
        for line in lines:
            # Identificar seção do WhatsApp
            if "whatsapp" in line.lower() and "💬" in line:
                in_whatsapp_section = True
                continue
            
            # Parar quando encontrar outra plataforma
            if in_whatsapp_section and ("instagram" in line.lower() or "linkedin" in line.lower()):
                break
            
            # Adicionar conteúdo da seção WhatsApp
            if in_whatsapp_section and line.strip():
                # Remover marcadores de hashtags (não usados no WhatsApp)
                if not line.strip().startswith('#'):
                    whatsapp_content.append(line.strip())
        
        # Se não encontrou seção específica, usar o conteúdo geral adaptado
        if not whatsapp_content:
            # Remover hashtags e adaptar para WhatsApp
            adapted = content.replace('#', '').replace('**', '*')
            return adapted[:4000]  # Limite do WhatsApp
        
        return '\n'.join(whatsapp_content)[:4000]
    
    def _update_workflow_stats(self, result: WorkflowResult):
        """Atualiza estatísticas do workflow"""
        self.stats["total_workflows"] += 1
        
        if result.success:
            self.stats["successful_workflows"] += 1
        else:
            self.stats["failed_workflows"] += 1
        
        # Atualizar tempo médio de execução
        total = self.stats["total_workflows"]
        current_avg = self.stats["avg_execution_time"]
        self.stats["avg_execution_time"] = (
            (current_avg * (total - 1) + result.execution_time) / total
        )
    
    # === MÉTODOS DE CONVENIÊNCIA ===
    
    async def create_and_distribute(
        self,
        topic: str,
        auto_send: bool = False,
        max_groups: int = 3,
        **kwargs
    ) -> WorkflowResult:
        """Método simplificado para criação e distribuição"""
        
        auto_send_config = AutoSendConfig(
            enabled=auto_send,
            auto_select_groups=True,
            max_groups=max_groups,
            require_approval=False
        ) if auto_send else None
        
        return await self.execute_complete_workflow(
            topic=topic,
            auto_send_config=auto_send_config,
            **kwargs
        )
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de um workflow específico"""
        if workflow_id in self.active_workflows:
            result = self.active_workflows[workflow_id]
            return {
                "id": workflow_id,
                "status": result.status.value,
                "topic": result.content_request.topic,
                "execution_time": result.execution_time,
                "success": result.success
            }
        return None
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos workflows"""
        return {
            **self.stats,
            "active_workflows": len(self.active_workflows),
            "total_history": len(self.workflow_history),
            "success_rate": (
                self.stats["successful_workflows"] / max(self.stats["total_workflows"], 1)
            ) * 100
        }
    
    def get_recent_workflows(self, limit: int = 10) -> List[WorkflowResult]:
        """Retorna workflows recentes"""
        return sorted(
            self.workflow_history,
            key=lambda x: x.execution_time,
            reverse=True
        )[:limit]

# Instância global do sistema de workflows
content_workflow = ContentWorkflow()

# Funções de conveniência
async def create_content_complete(
    topic: str,
    platforms: List[str] = ["instagram", "whatsapp", "linkedin"],
    auto_send: bool = False,
    max_groups: int = 3,
    **kwargs
) -> WorkflowResult:
    """Função principal para criação completa de conteúdo"""
    return await content_workflow.create_and_distribute(
        topic=topic,
        platforms=platforms,
        auto_send=auto_send,
        max_groups=max_groups,
        **kwargs
    )

def get_workflow_statistics() -> Dict[str, Any]:
    """Função de conveniência para estatísticas"""
    return content_workflow.get_workflow_stats()
