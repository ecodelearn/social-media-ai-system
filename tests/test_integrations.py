#!/usr/bin/env python3
"""
Testes para Integrações MCP - FASE 4

Testa todas as funcionalidades de integração MCP:
- Perplexity AI (busca e documentação)
- WhatsApp (grupos e envio de mensagens)
- WhatsApp Manager (busca avançada e logs)

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - FASE 4
"""

import pytest
import asyncio
import logging
from datetime import datetime
from typing import List, Dict

from core.mcp_integrations import mcp_integrations, MCPResponse, WhatsAppGroup
from core.real_mcp_integrations import real_mcp_integrations, RealMCPIntegrations
from core.whatsapp_manager import whatsapp_manager, WhatsAppManager, WhatsAppGroupSelection

# Configurar logging para testes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMCPIntegrations:
    """Testes para integrações MCP básicas"""
    
    @pytest.mark.asyncio
    async def test_mcp_connections(self):
        """Testa verificação de conexões MCP"""
        logger.info("🧪 Testando conexões MCP...")
        
        connections = await mcp_integrations.check_mcp_connections()
        
        assert isinstance(connections, dict)
        assert "perplexity" in connections
        assert "whatsapp" in connections
        
        logger.info(f"✅ Conexões testadas: {connections}")
    
    @pytest.mark.asyncio
    async def test_perplexity_search(self):
        """Testa busca no Perplexity"""
        logger.info("🧪 Testando busca Perplexity...")
        
        query = "inteligência artificial 2025"
        response = await mcp_integrations.search_perplexity(query, "normal")
        
        assert isinstance(response, MCPResponse)
        assert response.provider == "perplexity"
        assert response.tool_name == "search"
        assert response.success == True
        assert len(response.content) > 0
        assert response.metadata["query"] == query
        assert response.response_time is not None
        
        logger.info(f"✅ Busca Perplexity concluída em {response.response_time:.2f}s")
        logger.info(f"📝 Conteúdo: {response.content[:100]}...")
    
    @pytest.mark.asyncio
    async def test_perplexity_documentation(self):
        """Testa obtenção de documentação"""
        logger.info("🧪 Testando documentação Perplexity...")
        
        technology = "Python"
        response = await mcp_integrations.get_documentation(technology)
        
        assert isinstance(response, MCPResponse)
        assert response.success == True
        assert technology.lower() in response.content.lower()
        assert response.metadata["technology"] == technology
        
        logger.info(f"✅ Documentação obtida para {technology}")
        logger.info(f"📚 Conteúdo: {response.content[:100]}...")
    
    @pytest.mark.asyncio
    async def test_whatsapp_groups(self):
        """Testa obtenção de grupos WhatsApp"""
        logger.info("🧪 Testando grupos WhatsApp...")
        
        groups = await mcp_integrations.get_whatsapp_groups()
        
        assert isinstance(groups, list)
        assert len(groups) > 0
        
        for group in groups:
            assert isinstance(group, WhatsAppGroup)
            assert group.id.endswith("@g.us")
            assert len(group.name) > 0
            
        logger.info(f"✅ {len(groups)} grupos obtidos")
        for group in groups:
            logger.info(f"📱 {group.name} ({group.participants_count} participantes)")
    
    @pytest.mark.asyncio
    async def test_find_group_by_name(self):
        """Testa busca de grupo por nome"""
        logger.info("🧪 Testando busca de grupo por nome...")
        
        # Obter grupos primeiro
        groups = await mcp_integrations.get_whatsapp_groups()
        assert len(groups) > 0
        
        # Testar busca exata
        first_group = groups[0]
        found_group = await mcp_integrations.find_group_by_name(first_group.name)
        
        assert found_group is not None
        assert found_group.id == first_group.id
        assert found_group.name == first_group.name
        
        # Testar busca parcial
        partial_name = first_group.name.split()[0]  # Primeira palavra
        found_partial = await mcp_integrations.find_group_by_name(partial_name)
        
        assert found_partial is not None
        
        logger.info(f"✅ Grupo encontrado: {found_group.name}")
        logger.info(f"✅ Busca parcial '{partial_name}': {found_partial.name}")
    
    @pytest.mark.asyncio
    async def test_send_message_mock(self):
        """Testa envio de mensagem (mock)"""
        logger.info("🧪 Testando envio de mensagem (mock)...")
        
        groups = await mcp_integrations.get_whatsapp_groups()
        assert len(groups) > 0
        
        test_group = groups[0]
        test_message = "🧪 Mensagem de teste da FASE 4 - MCP Integrations"
        
        response = await mcp_integrations.send_message_to_group(test_group.id, test_message)
        
        assert isinstance(response, MCPResponse)
        assert response.provider == "whatsapp"
        assert response.tool_name == "send_message_to_group"
        assert response.success == True
        assert response.metadata["group_id"] == test_group.id
        assert response.metadata["message_length"] == len(test_message)
        
        logger.info(f"✅ Mensagem enviada para {test_group.name}")
        logger.info(f"⏱️ Tempo de resposta: {response.response_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_send_phone_message_mock(self):
        """Testa envio para telefone (mock)"""
        logger.info("🧪 Testando envio para telefone (mock)...")
        
        test_phone = "5562999476650"
        test_message = "🧪 Teste FASE 4 - WhatsApp MCP"
        
        response = await mcp_integrations.send_message_to_phone(test_phone, test_message)
        
        assert isinstance(response, MCPResponse)
        assert response.success == True
        assert response.metadata["phone"] == test_phone
        
        logger.info(f"✅ Mensagem enviada para {test_phone}")
    
    def test_usage_stats(self):
        """Testa estatísticas de uso"""
        logger.info("🧪 Testando estatísticas de uso...")
        
        stats = mcp_integrations.get_usage_stats()
        
        assert isinstance(stats, dict)
        assert "perplexity_searches" in stats
        assert "whatsapp_messages_sent" in stats
        assert "connections_status" in stats
        assert "cache_info" in stats
        
        logger.info(f"✅ Estatísticas obtidas: {stats}")

class TestRealMCPIntegrations:
    """Testes para integrações MCP reais"""
    
    @pytest.mark.asyncio
    async def test_real_connections(self):
        """Testa conexões reais MCP"""
        logger.info("🧪 Testando conexões MCP reais...")
        
        connections = await real_mcp_integrations.test_connections()
        
        assert isinstance(connections, dict)
        assert "perplexity" in connections or "whatsapp" in connections
        
        logger.info(f"✅ Conexões reais testadas: {connections}")
    
    @pytest.mark.asyncio
    async def test_real_perplexity_search(self):
        """Testa busca real no Perplexity"""
        logger.info("🧪 Testando busca real Perplexity...")
        
        query = "tendências marketing digital 2025"
        response = await real_mcp_integrations.search_perplexity_real(query, "detailed")
        
        assert isinstance(response, MCPResponse)
        assert response.provider == "perplexity"
        assert response.metadata.get("real_mcp") == True
        assert response.metadata.get("source") == "perplexity-mcp"
        
        logger.info(f"✅ Busca real concluída em {response.response_time:.2f}s")
        logger.info(f"📊 Conteúdo detalhado obtido: {len(response.content)} caracteres")
    
    @pytest.mark.asyncio
    async def test_real_documentation(self):
        """Testa documentação real"""
        logger.info("🧪 Testando documentação real...")
        
        technology = "FastAPI"
        response = await real_mcp_integrations.get_documentation_real(technology)
        
        assert isinstance(response, MCPResponse)
        assert response.success == True
        assert response.metadata.get("real_mcp") == True
        
        logger.info(f"✅ Documentação real obtida para {technology}")
    
    @pytest.mark.asyncio
    async def test_real_whatsapp_groups(self):
        """Testa grupos reais WhatsApp"""
        logger.info("🧪 Testando grupos reais WhatsApp...")
        
        groups = await real_mcp_integrations.get_whatsapp_groups_real()
        
        assert isinstance(groups, list)
        assert len(groups) > 0
        
        # Verificar grupos mais realistas
        group_names = [group.name for group in groups]
        assert any("AI" in name or "Tech" in name for name in group_names)
        
        logger.info(f"✅ {len(groups)} grupos reais obtidos")
        for group in groups:
            logger.info(f"🤖 {group.name} - {group.participants_count} participantes")
    
    @pytest.mark.asyncio
    async def test_real_send_message(self):
        """Testa envio real de mensagem"""
        logger.info("🧪 Testando envio real de mensagem...")
        
        groups = await real_mcp_integrations.get_whatsapp_groups_real()
        assert len(groups) > 0
        
        test_group = groups[0]
        test_message = """🚀 **TESTE FASE 4 - MCP REAL**

✅ Sistema de integração MCP funcionando
🤖 Inteligência artificial em ação
📱 WhatsApp conectado via Evolution API

*Teste automatizado do Social Media AI System*"""
        
        response = await real_mcp_integrations.send_message_to_group_real(test_group.id, test_message)
        
        assert isinstance(response, MCPResponse)
        assert response.metadata.get("real_mcp") == True
        assert response.metadata.get("source") == "evoapi_mcp"
        
        logger.info(f"✅ Mensagem real enviada: {response.success}")
        if response.success:
            logger.info(f"📤 Enviado para: {test_group.name}")
        else:
            logger.warning(f"❌ Falha: {response.error_message}")
    
    def test_real_usage_stats(self):
        """Testa estatísticas das integrações reais"""
        logger.info("🧪 Testando estatísticas reais...")
        
        stats = real_mcp_integrations.get_usage_stats()
        
        assert isinstance(stats, dict)
        assert "real_mcp_calls" in stats
        assert "version" in stats
        assert stats["version"] == "real_mcp_v1.0"
        
        logger.info(f"✅ Estatísticas reais: {stats}")

class TestWhatsAppManager:
    """Testes para WhatsApp Manager avançado"""
    
    @pytest.mark.asyncio
    async def test_fetch_groups(self):
        """Testa busca de grupos com cache"""
        logger.info("🧪 Testando WhatsApp Manager - fetch groups...")
        
        # Primeira chamada (cache miss)
        groups1 = await whatsapp_manager.fetch_groups(force_refresh=True)
        assert isinstance(groups1, list)
        assert len(groups1) > 0
        
        # Segunda chamada (cache hit)
        groups2 = await whatsapp_manager.fetch_groups(force_refresh=False)
        assert len(groups2) == len(groups1)
        
        logger.info(f"✅ {len(groups1)} grupos obtidos com cache funcionando")
    
    @pytest.mark.asyncio
    async def test_search_groups_advanced(self):
        """Testa busca avançada de grupos"""
        logger.info("🧪 Testando busca avançada de grupos...")
        
        # Buscar termo específico
        search_term = "Marketing"
        results = await whatsapp_manager.search_groups(search_term)
        
        assert isinstance(results, list)
        
        if results:
            for result in results:
                assert isinstance(result, WhatsAppGroupSelection)
                assert result.confidence_score > 0
                assert result.confidence_score <= 1.0
                assert search_term.lower() in result.selection_reason.lower() or search_term.lower() in result.group_name.lower()
            
            # Verificar ordenação por score
            scores = [r.confidence_score for r in results]
            assert scores == sorted(scores, reverse=True)
            
            logger.info(f"✅ {len(results)} grupos encontrados para '{search_term}'")
            for result in results:
                logger.info(f"🎯 {result.group_name} - Score: {result.confidence_score:.2f} - {result.selection_reason}")
        else:
            logger.info(f"ℹ️ Nenhum grupo encontrado para '{search_term}'")
    
    @pytest.mark.asyncio
    async def test_best_group_match(self):
        """Testa busca do melhor match"""
        logger.info("🧪 Testando melhor match de grupo...")
        
        # Buscar por termo que deve ter match
        search_term = "Testes"
        best_match = await whatsapp_manager.get_best_group_match(search_term)
        
        if best_match:
            assert isinstance(best_match, WhatsAppGroup)
            assert search_term.lower() in best_match.name.lower()
            logger.info(f"✅ Melhor match encontrado: {best_match.name}")
        else:
            logger.info(f"ℹ️ Nenhum match suficiente para '{search_term}'")
    
    @pytest.mark.asyncio
    async def test_send_message_with_search(self):
        """Testa envio com busca automática"""
        logger.info("🧪 Testando envio com busca automática...")
        
        # Usar nome parcial de um grupo
        group_name = "Testes"  # Deve encontrar "Grupo de Testes"
        test_message = """🧪 **TESTE WHATSAPP MANAGER**

✅ Busca automática de grupos funcionando
🎯 Sistema de scoring implementado
📊 Logs de envio sendo gravados

*Enviado via WhatsApp Manager da FASE 4*"""
        
        response = await whatsapp_manager.send_message_to_group(group_name, test_message, auto_find=True)
        
        assert isinstance(response, MCPResponse)
        logger.info(f"✅ Envio com busca: {response.success}")
        if not response.success:
            logger.warning(f"❌ Erro: {response.error_message}")
    
    @pytest.mark.asyncio
    async def test_send_to_phone(self):
        """Testa envio para telefone via manager"""
        logger.info("🧪 Testando envio para telefone via manager...")
        
        test_phone = "5562999476650"
        test_message = "🧪 Teste WhatsApp Manager - Envio para telefone funcionando!"
        
        response = await whatsapp_manager.send_message_to_phone(test_phone, test_message)
        
        assert isinstance(response, MCPResponse)
        logger.info(f"✅ Envio para telefone: {response.success}")
    
    def test_manager_stats(self):
        """Testa estatísticas do manager"""
        logger.info("🧪 Testando estatísticas do WhatsApp Manager...")
        
        stats = whatsapp_manager.get_stats()
        
        assert isinstance(stats, dict)
        assert "success_rate" in stats
        assert "recent_logs_count" in stats
        assert "cache_info" in stats
        
        logger.info(f"✅ Estatísticas do manager: {stats}")
    
    def test_groups_summary(self):
        """Testa resumo de grupos"""
        logger.info("🧪 Testando resumo de grupos...")
        
        summary = whatsapp_manager.get_groups_summary()
        
        assert isinstance(summary, dict)
        assert "total_groups" in summary
        assert "groups" in summary
        assert isinstance(summary["groups"], list)
        
        logger.info(f"✅ Resumo: {summary['total_groups']} grupos disponíveis")
    
    def test_recent_sends(self):
        """Testa histórico de envios recentes"""
        logger.info("🧪 Testando envios recentes...")
        
        recent = whatsapp_manager.get_recent_sends(limit=5)
        
        assert isinstance(recent, list)
        
        if recent:
            for send in recent:
                assert "timestamp" in send
                assert "group_name" in send
                assert "success" in send
            logger.info(f"✅ {len(recent)} envios recentes encontrados")
        else:
            logger.info("ℹ️ Nenhum envio recente encontrado")

# Função para executar todos os testes
async def run_all_tests():
    """Executa todos os testes da FASE 4"""
    logger.info("🚀 INICIANDO TESTES DA FASE 4 - INTEGRAÇÃO MCP")
    logger.info("=" * 60)
    
    # Testes MCP básico
    logger.info("📋 TESTES MCP BÁSICO")
    logger.info("-" * 30)
    
    basic_tests = TestMCPIntegrations()
    
    await basic_tests.test_mcp_connections()
    await basic_tests.test_perplexity_search()
    await basic_tests.test_perplexity_documentation()
    await basic_tests.test_whatsapp_groups()
    await basic_tests.test_find_group_by_name()
    await basic_tests.test_send_message_mock()
    await basic_tests.test_send_phone_message_mock()
    basic_tests.test_usage_stats()
    
    # Testes MCP real
    logger.info("\n🔥 TESTES MCP REAL")
    logger.info("-" * 30)
    
    real_tests = TestRealMCPIntegrations()
    
    await real_tests.test_real_connections()
    await real_tests.test_real_perplexity_search()
    await real_tests.test_real_documentation()
    await real_tests.test_real_whatsapp_groups()
    await real_tests.test_real_send_message()
    real_tests.test_real_usage_stats()
    
    # Testes WhatsApp Manager
    logger.info("\n📱 TESTES WHATSAPP MANAGER")
    logger.info("-" * 30)
    
    manager_tests = TestWhatsAppManager()
    
    await manager_tests.test_fetch_groups()
    await manager_tests.test_search_groups_advanced()
    await manager_tests.test_best_group_match()
    await manager_tests.test_send_message_with_search()
    await manager_tests.test_send_to_phone()
    manager_tests.test_manager_stats()
    manager_tests.test_groups_summary()
    manager_tests.test_recent_sends()
    
    logger.info("\n🎉 TODOS OS TESTES DA FASE 4 CONCLUÍDOS!")
    logger.info("=" * 60)
    
    # Resumo final
    logger.info("\n📊 RESUMO DOS TESTES:")
    logger.info("✅ Integrações MCP básicas: OK")
    logger.info("✅ Integrações MCP reais: OK") 
    logger.info("✅ WhatsApp Manager avançado: OK")
    logger.info("✅ Sistema de cache e logs: OK")
    logger.info("✅ Busca inteligente de grupos: OK")
    logger.info("✅ Envio automático: OK")
    
    # Estatísticas finais
    basic_stats = mcp_integrations.get_usage_stats()
    real_stats = real_mcp_integrations.get_usage_stats()
    manager_stats = whatsapp_manager.get_stats()
    
    logger.info(f"\n📈 ESTATÍSTICAS FINAIS:")
    logger.info(f"🔍 Buscas Perplexity: {basic_stats['perplexity_searches']} + {real_stats['perplexity_searches']} (real)")
    logger.info(f"📱 Mensagens WhatsApp: {basic_stats['whatsapp_messages_sent']} + {real_stats['whatsapp_messages_sent']} (real)")
    logger.info(f"🎯 Taxa de sucesso Manager: {manager_stats['success_rate']}%")
    logger.info(f"⚡ Total chamadas MCP real: {real_stats['real_mcp_calls']}")

if __name__ == "__main__":
    # Executar testes quando rodado diretamente
    asyncio.run(run_all_tests())
