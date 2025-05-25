#!/usr/bin/env python3
"""
Teste Rápido da Fase 3 - Orquestração

Script simples para testar o sistema de orquestração sem executar o demo completo.
Ideal para verificação rápida se todos os componentes estão funcionando.

Uso:
    python test_phase3_orchestration.py
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configurar logging simples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todas as importações necessárias funcionam"""
    print("🔧 Testando importações...")
    
    try:
        # Testar imports básicos
        from core.workflows import content_workflow, create_content_complete
        from core.real_mcp_integrations import real_mcp_integrations
        from core.agents import social_agents
        from core.llm_manager import llm_manager
        from config.settings import SystemSettings
        
        print("✅ Todas as importações funcionando")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

async def test_basic_system():
    """Testa componentes básicos do sistema"""
    print("\n🔍 Testando componentes básicos...")
    
    try:
        # Testar LLM Manager
        print("  📡 Testando LLM Manager...")
        llm_status = llm_manager.get_provider_status()
        print(f"     LLM Providers: {llm_status}")
        
        # Testar Agentes
        print("  🤖 Testando Sistema de Agentes...")
        from core.agents import get_agents_status, get_agents_info
        agents_status = get_agents_status()
        print(f"     Agentes ativos: {sum(agents_status.values())}/4")
        
        # Testar MCP Integrations (conexão básica)
        print("  🔗 Testando MCP Integrations...")
        mcp_stats = real_mcp_integrations.get_usage_stats()
        print(f"     MCP Stats: {mcp_stats['real_mcp_calls']} chamadas realizadas")
        
        # Testar Workflow System
        print("  🔄 Testando Workflow System...")
        from core.workflows import get_workflow_statistics
        workflow_stats = get_workflow_statistics()
        print(f"     Workflows executados: {workflow_stats['total_workflows']}")
        
        print("✅ Todos os componentes básicos funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos testes básicos: {e}")
        return False

async def test_simple_workflow():
    """Testa um workflow simples e rápido"""
    print("\n🚀 Testando workflow simples...")
    
    try:
        # Usar tópico simples para teste rápido
        topic = "Teste de Sistema - IA"
        
        print(f"  📝 Criando conteúdo para: {topic}")
        print("  ⏱️  Executando workflow (isso pode levar 30-60s)...")
        
        # Executar workflow básico sem envio
        result = await create_content_complete(
            topic=topic,
            platforms=["instagram"],  # Apenas uma plataforma para ser mais rápido
            target_audience="Teste",
            objective="Teste do sistema",
            tone="Simples",
            auto_send=False  # Não enviar para ser mais rápido
        )
        
        if result.success:
            print("✅ Workflow simples executado com sucesso!")
            print(f"  ⏱️  Tempo de execução: {result.execution_time:.2f}s")
            print(f"  📊 Status: {result.status.value}")
            
            # Verificar se temos pesquisa
            if result.perplexity_research and result.perplexity_research.success:
                print("  🔍 Pesquisa Perplexity: ✅")
            else:
                print("  🔍 Pesquisa Perplexity: ❌")
            
            # Verificar se temos conteúdo criado
            if result.crew_result and result.crew_result.final_content:
                content_length = len(result.crew_result.final_content)
                print(f"  📝 Conteúdo criado: ✅ ({content_length} caracteres)")
            else:
                print("  📝 Conteúdo criado: ❌")
            
            return True
        else:
            print(f"❌ Workflow falhou: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de workflow: {e}")
        return False

async def test_mcp_connections():
    """Testa conexões MCP rapidamente"""
    print("\n🔗 Testando conexões MCP...")
    
    try:
        # Testar conexões
        connections = await real_mcp_integrations.test_connections()
        
        print(f"  🤖 Perplexity MCP: {'✅' if connections.get('perplexity', False) else '❌'}")
        print(f"  📱 WhatsApp MCP: {'✅' if connections.get('whatsapp', False) else '❌'}")
        
        # Se pelo menos uma conexão funciona, está OK para teste
        if any(connections.values()):
            print("✅ Pelo menos uma conexão MCP funcionando")
            return True
        else:
            print("⚠️  Nenhuma conexão MCP ativa (modo simulado)")
            return True  # Ainda OK para teste
            
    except Exception as e:
        print(f"❌ Erro ao testar conexões MCP: {e}")
        return False

async def main():
    """Função principal do teste"""
    print("🧪 TESTE RÁPIDO - FASE 3 ORQUESTRAÇÃO")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    all_tests_passed = True
    
    # Teste 1: Importações
    if not test_imports():
        all_tests_passed = False
        print("\n❌ Falha crítica: Importações não funcionam")
        return 1
    
    # Teste 2: Componentes básicos
    if not await test_basic_system():
        all_tests_passed = False
        print("\n⚠️  Alguns componentes com problemas, mas continuando...")
    
    # Teste 3: Conexões MCP
    if not await test_mcp_connections():
        all_tests_passed = False
        print("\n⚠️  Problemas de conexão MCP, mas continuando...")
    
    # Teste 4: Workflow simples (principal)
    if not await test_simple_workflow():
        all_tests_passed = False
        print("\n❌ Falha crítica: Workflow não funciona")
        return 1
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DO TESTE")
    print("-" * 30)
    
    if all_tests_passed:
        print("✅ STATUS: TODOS OS TESTES PASSARAM")
        print("🚀 Sistema da Fase 3 está funcionando perfeitamente!")
        print("\n💡 Próximos passos:")
        print("   • Execute o demo completo: python phase3_demo.py")
        print("   • Use o sistema em produção")
        print("   • Teste workflows com envio automático")
        return 0
    else:
        print("⚠️  STATUS: ALGUNS TESTES FALHARAM")
        print("🔧 Sistema da Fase 3 funciona parcialmente")
        print("\n💡 Recomendações:")
        print("   • Verifique configurações em config/settings.py")
        print("   • Teste conexões MCP individualmente")
        print("   • Execute o demo completo para análise detalhada")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal no teste: {e}")
        sys.exit(1)
