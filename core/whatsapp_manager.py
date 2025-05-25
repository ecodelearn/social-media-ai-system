#!/usr/bin/env python3
"""
WhatsApp Manager - Social Media AI System

Gerenciador especializado para operações do WhatsApp via MCP.
Fornece interface simplificada para envio, busca de grupos e logs.

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - FASE 4
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from config.settings import SystemSettings
from core.mcp_integrations import MCPIntegrations, WhatsAppGroup, MCPResponse

@dataclass
class WhatsAppGroupSelection:
    """Seleção de grupo com critérios específicos"""
    group_id: str
    group_name: str
    selection_reason: str
    confidence_score: float

@dataclass
class MessageSendLog:
    """Log de mensagem enviada"""
    timestamp: datetime
    group_id: str
    group_name: str
    message_preview: str
    success: bool
    error_message: Optional[str] = None
    response_time: Optional[float] = None

class WhatsAppManager:
    """Gerenciador especializado para WhatsApp"""
    
    def __init__(self):
        """Inicializa o gerenciador WhatsApp"""
        self.logger = logging.getLogger(__name__)
        self.mcp = MCPIntegrations()
        
        # Cache de grupos com metadados
        self._groups_cache = {}
        self._cache_metadata = {
            "last_update": None,
            "total_groups": 0,
            "update_count": 0
        }
        
        # Logs de envio
        self._send_logs = []
        self._logs_file = SystemSettings.SENT_MESSAGES_DIR / "whatsapp_logs.json"
        
        # Estatísticas
        self.stats = {
            "groups_fetched": 0,
            "messages_sent": 0,
            "successful_sends": 0,
            "failed_sends": 0,
            "group_searches": 0
        }
        
        # Carregar logs existentes
        self._load_existing_logs()
        
        self.logger.info("WhatsApp Manager inicializado")
    
    # === GERENCIAMENTO DE GRUPOS ===
    
    async def fetch_groups(self, force_refresh: bool = False) -> List[WhatsAppGroup]:
        """Busca e cacheia grupos do WhatsApp"""
        try:
            self.logger.info("Buscando grupos do WhatsApp...")
            
            # Usar cache se disponível e não forçar refresh
            if (not force_refresh and 
                self._groups_cache and 
                self._cache_metadata["last_update"] and
                (datetime.now() - self._cache_metadata["last_update"]).total_seconds() < 300):
                
                self.logger.info("Usando grupos do cache")
                return list(self._groups_cache.values())
            
            # Buscar grupos via MCP
            groups = await self.mcp.get_whatsapp_groups(force_refresh=True)
            
            if groups:
                # Atualizar cache
                self._groups_cache = {group.id: group for group in groups}
                self._cache_metadata.update({
                    "last_update": datetime.now(),
                    "total_groups": len(groups),
                    "update_count": self._cache_metadata["update_count"] + 1
                })
                
                self.stats["groups_fetched"] += len(groups)
                self.logger.info(f"✅ {len(groups)} grupos obtidos e cacheados")
                
                # Salvar cache em arquivo para persistência
                await self._save_groups_cache()
                
                return groups
            else:
                self.logger.warning("⚠️ Nenhum grupo encontrado")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar grupos: {e}")
            return []
    
    async def search_groups(self, search_term: str) -> List[WhatsAppGroupSelection]:
        """Busca grupos por nome ou palavra-chave com scoring"""
        try:
            self.stats["group_searches"] += 1
            self.logger.info(f"🔍 Buscando grupos com termo: '{search_term}'")
            
            # Garantir que temos grupos atualizados
            groups = await self.fetch_groups()
            
            if not groups:
                self.logger.warning("Nenhum grupo disponível para busca")
                return []
            
            # Busca com scoring
            results = []
            search_lower = search_term.lower().strip()
            
            for group in groups:
                group_name_lower = group.name.lower()
                
                # Exato match - score máximo
                if search_lower == group_name_lower:
                    results.append(WhatsAppGroupSelection(
                        group_id=group.id,
                        group_name=group.name,
                        selection_reason="Nome exato",
                        confidence_score=1.0
                    ))
                
                # Contém o termo - score médio/alto
                elif search_lower in group_name_lower:
                    # Score baseado em posição e tamanho
                    position = group_name_lower.find(search_lower)
                    name_length = len(group_name_lower)
                    term_length = len(search_lower)
                    
                    # Score maior se está no início e ocupa boa parte do nome
                    score = 0.8 - (position * 0.1) + (term_length / name_length * 0.2)
                    score = max(0.3, min(0.95, score))  # Limitar entre 0.3 e 0.95
                    
                    results.append(WhatsAppGroupSelection(
                        group_id=group.id,
                        group_name=group.name,
                        selection_reason=f"Contém '{search_term}' (posição: {position})",
                        confidence_score=score
                    ))
                
                # Palavras parciais - score baixo
                elif any(word in group_name_lower for word in search_lower.split()):
                    matching_words = [word for word in search_lower.split() if word in group_name_lower]
                    score = 0.2 + (len(matching_words) * 0.1)
                    
                    results.append(WhatsAppGroupSelection(
                        group_id=group.id,
                        group_name=group.name,
                        selection_reason=f"Palavras encontradas: {', '.join(matching_words)}",
                        confidence_score=score
                    ))
            
            # Ordenar por score descendente
            results.sort(key=lambda x: x.confidence_score, reverse=True)
            
            self.logger.info(f"✅ {len(results)} grupos encontrados para '{search_term}'")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Erro na busca de grupos: {e}")
            return []
    
    async def get_best_group_match(self, search_term: str) -> Optional[WhatsAppGroup]:
        """Retorna o melhor match para um termo de busca"""
        try:
            results = await self.search_groups(search_term)
            
            if not results:
                return None
            
            # Retornar o melhor resultado (primeiro da lista ordenada)
            best_match = results[0]
            
            if best_match.confidence_score >= 0.5:  # Confiança mínima
                group = self._groups_cache.get(best_match.group_id)
                self.logger.info(f"✅ Melhor match: '{best_match.group_name}' (score: {best_match.confidence_score:.2f})")
                return group
            else:
                self.logger.warning(f"⚠️ Melhor match tem baixa confiança: {best_match.confidence_score:.2f}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar melhor match: {e}")
            return None
    
    # === ENVIO DE MENSAGENS ===
    
    async def send_message_to_group(
        self, 
        group_identifier: str, 
        message: str,
        auto_find: bool = True
    ) -> MCPResponse:
        """Envia mensagem para grupo (por ID ou nome)"""
        try:
            start_time = datetime.now()
            self.stats["messages_sent"] += 1
            
            group = None
            group_id = None
            
            # Verificar se é um ID direto (formato xxx@g.us)
            if "@g.us" in group_identifier:
                group_id = group_identifier
                # Buscar dados do grupo no cache
                group = self._groups_cache.get(group_id)
                if not group:
                    await self.fetch_groups()  # Atualizar cache
                    group = self._groups_cache.get(group_id)
            
            # Se não encontrou por ID, buscar por nome
            elif auto_find:
                group = await self.get_best_group_match(group_identifier)
                if group:
                    group_id = group.id
            
            if not group_id:
                error_msg = f"Grupo '{group_identifier}' não encontrado"
                self.logger.error(f"❌ {error_msg}")
                
                # Log do erro
                self._add_send_log(MessageSendLog(
                    timestamp=datetime.now(),
                    group_id="",
                    group_name=group_identifier,
                    message_preview=message[:50] + "..." if len(message) > 50 else message,
                    success=False,
                    error_message=error_msg
                ))
                
                self.stats["failed_sends"] += 1
                
                return MCPResponse(
                    provider="whatsapp",
                    tool_name="send_message_to_group",
                    success=False,
                    content="",
                    error_message=error_msg
                )
            
            # Enviar via MCP
            self.logger.info(f"📤 Enviando mensagem para: {group.name if group else group_id}")
            response = await self.mcp.send_message_to_group(group_id, message)
            
            # Calcular tempo de resposta
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Log do envio
            log_entry = MessageSendLog(
                timestamp=datetime.now(),
                group_id=group_id,
                group_name=group.name if group else group_identifier,
                message_preview=message[:50] + "..." if len(message) > 50 else message,
                success=response.success,
                error_message=response.error_message,
                response_time=response_time
            )
            
            self._add_send_log(log_entry)
            
            # Atualizar estatísticas
            if response.success:
                self.stats["successful_sends"] += 1
                self.logger.info(f"✅ Mensagem enviada com sucesso para {group.name if group else group_id}")
            else:
                self.stats["failed_sends"] += 1
                self.logger.error(f"❌ Falha ao enviar para {group.name if group else group_id}: {response.error_message}")
            
            return response
            
        except Exception as e:
            self.stats["failed_sends"] += 1
            error_msg = f"Erro interno ao enviar mensagem: {e}"
            self.logger.error(f"❌ {error_msg}")
            
            return MCPResponse(
                provider="whatsapp",
                tool_name="send_message_to_group",
                success=False,
                content="",
                error_message=error_msg
            )
    
    async def send_message_to_phone(self, phone: str, message: str) -> MCPResponse:
        """Envia mensagem para número de telefone"""
        try:
            start_time = datetime.now()
            self.stats["messages_sent"] += 1
            
            self.logger.info(f"📱 Enviando mensagem para: {phone}")
            response = await self.mcp.send_message_to_phone(phone, message)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Log do envio
            log_entry = MessageSendLog(
                timestamp=datetime.now(),
                group_id=phone,
                group_name=f"Phone: {phone}",
                message_preview=message[:50] + "..." if len(message) > 50 else message,
                success=response.success,
                error_message=response.error_message,
                response_time=response_time
            )
            
            self._add_send_log(log_entry)
            
            # Atualizar estatísticas
            if response.success:
                self.stats["successful_sends"] += 1
                self.logger.info(f"✅ Mensagem enviada com sucesso para {phone}")
            else:
                self.stats["failed_sends"] += 1
                self.logger.error(f"❌ Falha ao enviar para {phone}: {response.error_message}")
            
            return response
            
        except Exception as e:
            self.stats["failed_sends"] += 1
            error_msg = f"Erro interno ao enviar mensagem: {e}"
            self.logger.error(f"❌ {error_msg}")
            
            return MCPResponse(
                provider="whatsapp",
                tool_name="send_message_to_phone",
                success=False,
                content="",
                error_message=error_msg
            )
    
    # === UTILITÁRIOS E LOGS ===
    
    def _add_send_log(self, log_entry: MessageSendLog):
        """Adiciona entrada ao log de envios"""
        self._send_logs.append(log_entry)
        
        # Manter apenas os últimos 1000 logs
        if len(self._send_logs) > 1000:
            self._send_logs = self._send_logs[-1000:]
        
        # Salvar em arquivo
        asyncio.create_task(self._save_send_logs())
    
    async def _save_send_logs(self):
        """Salva logs de envio em arquivo"""
        try:
            # Preparar dados para JSON
            logs_data = []
            for log in self._send_logs[-50:]:  # Últimos 50 logs
                log_dict = asdict(log)
                log_dict["timestamp"] = log.timestamp.isoformat()
                logs_data.append(log_dict)
            
            # Salvar arquivo
            with open(self._logs_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "total_logs": len(self._send_logs),
                        "last_update": datetime.now().isoformat(),
                        "stats": self.stats
                    },
                    "recent_logs": logs_data
                }, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar logs: {e}")
    
    async def _save_groups_cache(self):
        """Salva cache de grupos em arquivo"""
        try:
            cache_file = SystemSettings.DATA_DIR / "whatsapp_groups_cache.json"
            
            # Preparar dados
            groups_data = []
            for group in self._groups_cache.values():
                groups_data.append({
                    "id": group.id,
                    "name": group.name,
                    "participants_count": group.participants_count,
                    "description": group.description
                })
            
            cache_data = {
                "metadata": self._cache_metadata.copy(),
                "groups": groups_data
            }
            
            # Converter datetime para string
            if cache_data["metadata"]["last_update"]:
                cache_data["metadata"]["last_update"] = cache_data["metadata"]["last_update"].isoformat()
            
            # Salvar
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar cache de grupos: {e}")
    
    def _load_existing_logs(self):
        """Carrega logs existentes do arquivo"""
        try:
            if self._logs_file.exists():
                with open(self._logs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carregar estatísticas
                if "metadata" in data and "stats" in data["metadata"]:
                    self.stats.update(data["metadata"]["stats"])
                
                self.logger.info("Logs existentes carregados")
                
        except Exception as e:
            self.logger.warning(f"Não foi possível carregar logs existentes: {e}")
    
    # === INFORMAÇÕES E ESTATÍSTICAS ===
    
    def get_groups_summary(self) -> Dict:
        """Retorna resumo dos grupos disponíveis"""
        return {
            "total_groups": len(self._groups_cache),
            "last_update": self._cache_metadata["last_update"].isoformat() if self._cache_metadata["last_update"] else None,
            "update_count": self._cache_metadata["update_count"],
            "groups": [
                {
                    "id": group.id,
                    "name": group.name,
                    "participants": group.participants_count
                }
                for group in self._groups_cache.values()
            ]
        }
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas completas do gerenciador"""
        success_rate = (self.stats["successful_sends"] / max(1, self.stats["messages_sent"])) * 100
        
        return {
            **self.stats,
            "success_rate": round(success_rate, 2),
            "recent_logs_count": len(self._send_logs),
            "cache_info": self._cache_metadata
        }
    
    def get_recent_sends(self, limit: int = 10) -> List[Dict]:
        """Retorna envios recentes"""
        recent = self._send_logs[-limit:] if self._send_logs else []
        
        return [
            {
                "timestamp": log.timestamp.strftime("%H:%M:%S"),
                "group_name": log.group_name,
                "message_preview": log.message_preview,
                "success": "✅" if log.success else "❌",
                "error": log.error_message or ""
            }
            for log in reversed(recent)
        ]

# Instância global do gerenciador WhatsApp
whatsapp_manager = WhatsAppManager()
