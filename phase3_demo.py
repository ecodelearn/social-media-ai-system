#!/usr/bin/env python3
"""
Demo da Fase 3 - Orquestração Completa End-to-End

Este demo demonstra o sistema completo funcionando:
1. 🔍 Pesquisa via Perplexity MCP
2. 🤖 Criação de conteúdo via 4 agentes CrewAI
3. 📱 Envio automático via WhatsApp MCP

FASE 3: ORCHESTRATION - 100% IMPLEMENTADA

Autor: Sistema de IA Colaborativo
Versão: 1.0.0
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('phase3_demo.log')
    ]
)

logger = logging.getLogger(__name__)

# Imports do sistema
try:
    from core.workflows import content_workflow, create_content_complete, get_workflow_statistics
    from core.real_mcp_integrations import real_mcp_integrations
    from core.agents import social_agents, get_agents_status, get_agents_info
    from core.llm_manager import llm_manager
    from config.settings import SystemSettings
    SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.error(f"Erro ao importar sistema: {e}")
    SYSTEM_AVAILABLE = False

class Phase3Demo:
    """Demonstração completa da Fase 3 - Orquestração End-to-End"""
    
    def __init__(self):
        """Inicializa o demo"""
        self.logger = logging.getLogger(__name__)
        
        if not SYSTEM_AVAILABLE:
            raise RuntimeError("Sistema não disponível para demonstração")
        
        # Componentes do sistema
        self.workflow_system = content_workflow
        self.mcp_integrations = real_mcp_integrations
        self.agents_system = social_agents
        
        # Configurações do demo
        self.demo_topics = [
            "Inteligência Artificial e Futuro do Trabalho",
            "Marketing Digital para Pequenas Empresas",
            "Sustentabilidade e Tecnologia Verde",
            "Transformação Digital nas Empresas",
            "Empreendedorismo Inovador 2025"
        ]
        
        # Resultados dos testes
        self.demo_results = []
        
        self.logger.info("🎬 Phase 3 Demo System inicializado")
    
    async def run_complete_demo(self) -> Dict[str, Any]:
        """Executa demonstração completa da Fase 3"""
        demo_start = time.time()
        
        try:
            self.logger.info("🚀 Iniciando demonstração completa da Fase 3")
            
            # === VERIFICAÇÕES INICIAIS ===
            self.logger.info("🔧 Executando verificações iniciais...")
            system_status = await self._check_system_status()
            
            if not system_status["ready"]:
                raise RuntimeError(f"Sistema não está pronto: {system_status}")
            
            # === DEMO 1: WORKFLOW BÁSICO (SEM ENVIO) ===
            self.logger.info("📝 Demo 1: Workflow básico de criação de conteúdo...")
            basic_result = await self._demo_basic_workflow()
            
            # === DEMO 2: WORKFLOW COMPLETO COM AUTO-ENVIO ===
            self.logger.info("📱 Demo 2: Workflow completo com envio automático...")
            complete_result = await self._demo_complete_workflow()
            
            # === DEMO 3: MÚLTIPLOS WORKFLOWS PARALELOS ===
            self.logger.info("⚡ Demo 3: Múltiplos workflows em paralelo...")
            parallel_result = await self._demo_parallel_workflows()
            
            # === ANÁLISE DOS RESULTADOS ===
            self.logger.info("📊 Analisando resultados da demonstração...")
            analysis = await self._analyze_demo_results()
            
            # === ESTATÍSTICAS FINAIS ===
            final_stats = await self._get_final_statistics()
            
            demo_time = time.time() - demo_start
            
            demo_summary = {
                "success": True,
                "execution_time": demo_time,
                "system_status": system_status,
                "demo_results": {
                    "basic_workflow": basic_result,
                    "complete_workflow": complete_result,
                    "parallel_workflows": parallel_result
                },
                "analysis": analysis,
                "final_statistics": final_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Demonstração da Fase 3 concluída em {demo_time:.2f}s")
            return demo_summary
            
        except Exception as e:
            demo_time = time.time() - demo_start
            error_summary = {
                "success": False,
                "error": str(e),
                "execution_time": demo_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.error(f"❌ Erro na demonstração: {e}")
            return error_summary
    
    async def _check_system_status(self) -> Dict[str, Any]:
        """Verifica status de todos os componentes do sistema"""
        status = {
            "ready": False,
            "components": {},
            "errors": []
        }
        
        try:
            # Verificar LLM Manager
            llm_status = llm_manager.get_provider_status()
            status["components"]["llm_manager"] = {
                "available": bool(llm_status),
                "providers": llm_status
            }
            
            # Verificar Agentes
            agents_status = get_agents_status()
            agents_info = get_agents_info()
            status["components"]["agents"] = {
                "available": all(agents_status.values()),
                "agents_status": agents_status,
                "agents_info": agents_info
            }
            
            # Verificar MCP Integrations
            mcp_connections = await self.mcp_integrations.test_connections()
            mcp_stats = self.mcp_integrations.get_usage_stats()
            status["components"]["mcp_integrations"] = {
                "available": any(mcp_connections.values()),
                "connections": mcp_connections,
                "usage_stats": mcp_stats
            }
            
            # Verificar Workflow System
            workflow_stats = get_workflow_statistics()
            status["components"]["workflow_system"] = {
                "available": True,
                "statistics": workflow_stats
            }
            
            # Determinar se o sistema está pronto
            ready_checks = [
                status["components"]["llm_manager"]["available"],
                status["components"]["agents"]["available"],
                status["components"]["mcp_integrations"]["available"],
                status["components"]["workflow_system"]["available"]
            ]
            
            status["ready"] = all(ready_checks)
            
            if not status["ready"]:
                status["errors"].append("Nem todos os componentes estão disponíveis")
            
            self.logger.info(f"🔍 Status do sistema: {'✅ Pronto' if status['ready'] else '❌ Não pronto'}")
            
        except Exception as e:
            status["errors"].append(f"Erro na verificação: {e}")
            self.logger.error(f"❌ Erro na verificação do sistema: {e}")
        
        return status
    
    async def _demo_basic_workflow(self) -> Dict[str, Any]:
        """Demonstra workflow básico sem envio automático"""
        topic = self.demo_topics[0]
        
        try:
            self.logger.info(f"🎯 Criando conteúdo para: {topic}")
            
            result = await create_content_complete(
                topic=topic,
                platforms=["instagram", "linkedin", "whatsapp"],
                target_audience="Profissionais de tecnologia",
                objective="Educação e engajamento",
                tone="Profissional e acessível",
                auto_send=False  # Não enviar automaticamente
            )
            
            demo_result = {
                "success": result.success,
                "topic": topic,
                "execution_time": result.execution_time,
                "status": result.status.value,
                "content_created": bool(result.crew_result and result.crew_result.final_content),
                "research_completed": bool(result.perplexity_research and result.perplexity_research.success),
                "content_length": len(result.crew_result.final_content) if result.crew_result else 0
            }
            
            self.demo_results.append(("basic_workflow", demo_result))
            
            if result.success:
                self.logger.info(f"✅ Workflow básico concluído: {result.status.value}")
            else:
                self.logger.error(f"❌ Falha no workflow básico: {result.error_message}")
            
            return demo_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "topic": topic,
                "error": str(e)
            }
            self.logger.error(f"❌ Erro no demo básico: {e}")
            return error_result
    
    async def _demo_complete_workflow(self) -> Dict[str, Any]:
        """Demonstra workflow completo com envio automático"""
        topic = self.demo_topics[1]
        
        try:
            self.logger.info(f"🎯 Criando e enviando conteúdo para: {topic}")
            
            result = await create_content_complete(
                topic=topic,
                platforms=["whatsapp", "instagram"],
                target_audience="Empreendedores e pequenos empresários",
                objective="Gerar leads e compartilhamentos",
                tone="Amigável e prático",
                auto_send=True,  # Enviar automaticamente
                max_groups=2    # Máximo 2 grupos para o demo
            )
            
            demo_result = {
                "success": result.success,
                "topic": topic,
                "execution_time": result.execution_time,
                "status": result.status.value,
                "content_created": bool(result.crew_result and result.crew_result.final_content),
                "research_completed": bool(result.perplexity_research and result.perplexity_research.success),
                "messages_sent": len(result.whatsapp_results),
                "successful_sends": sum(1 for r in result.whatsapp_results if r.success),
                "groups_targeted": len(result.selected_groups),
                "group_names": [g.name for g in result.selected_groups]
            }
            
            self.demo_results.append(("complete_workflow", demo_result))
            
            if result.success:
                self.logger.info(
                    f"✅ Workflow completo concluído: "
                    f"{demo_result['successful_sends']}/{demo_result['messages_sent']} mensagens enviadas"
                )
            else:
                self.logger.error(f"❌ Falha no workflow completo: {result.error_message}")
            
            return demo_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "topic": topic,
                "error": str(e)
            }
            self.logger.error(f"❌ Erro no demo completo: {e}")
            return error_result
    
    async def _demo_parallel_workflows(self) -> Dict[str, Any]:
        """Demonstra múltiplos workflows executando em paralelo"""
        parallel_topics = self.demo_topics[2:5]  # 3 tópicos
        
        try:
            self.logger.info(f"⚡ Executando {len(parallel_topics)} workflows em paralelo...")
            
            # Criar tasks para execução paralela
            tasks = []
            for i, topic in enumerate(parallel_topics):
                task = create_content_complete(
                    topic=topic,
                    platforms=["instagram", "whatsapp"],
                    target_audience="Público geral interessado em inovação",
                    objective="Viralização e engajamento",
                    auto_send=False,  # Não enviar para não sobrecarregar
                    workflow_id=f"parallel_{i+1}_{int(time.time())}"
                )
                tasks.append(task)
            
            # Executar todos em paralelo
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            parallel_time = time.time() - start_time
            
            # Analisar resultados
            successful_workflows = 0
            failed_workflows = 0
            total_content_length = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_workflows += 1
                    self.logger.error(f"❌ Workflow paralelo {i+1} falhou: {result}")
                else:
                    if result.success:
                        successful_workflows += 1
                        if result.crew_result and result.crew_result.final_content:
                            total_content_length += len(result.crew_result.final_content)
                    else:
                        failed_workflows += 1
            
            demo_result = {
                "success": successful_workflows > 0,
                "topics": parallel_topics,
                "execution_time": parallel_time,
                "total_workflows": len(parallel_topics),
                "successful_workflows": successful_workflows,
                "failed_workflows": failed_workflows,
                "total_content_length": total_content_length,
                "avg_execution_time": parallel_time / len(parallel_topics)
            }
            
            self.demo_results.append(("parallel_workflows", demo_result))
            
            self.logger.info(
                f"⚡ Workflows paralelos concluídos: "
                f"{successful_workflows}/{len(parallel_topics)} sucessos em {parallel_time:.2f}s"
            )
            
            return demo_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "topics": parallel_topics,
                "error": str(e)
            }
            self.logger.error(f"❌ Erro nos workflows paralelos: {e}")
            return error_result
    
    async def _analyze_demo_results(self) -> Dict[str, Any]:
        """Analisa os resultados de todos os demos"""
        analysis = {
            "total_demos": len(self.demo_results),
            "successful_demos": 0,
            "failed_demos": 0,
            "performance_metrics": {},
            "quality_assessment": {},
            "recommendations": []
        }
        
        try:
            # Contar sucessos e falhas
            for demo_type, result in self.demo_results:
                if result.get("success", False):
                    analysis["successful_demos"] += 1
                else:
                    analysis["failed_demos"] += 1
            
            # Calcular métricas de performance
            execution_times = [
                result.get("execution_time", 0) 
                for _, result in self.demo_results 
                if "execution_time" in result
            ]
            
            if execution_times:
                analysis["performance_metrics"] = {
                    "avg_execution_time": sum(execution_times) / len(execution_times),
                    "min_execution_time": min(execution_times),
                    "max_execution_time": max(execution_times),
                    "total_execution_time": sum(execution_times)
                }
            
            # Avaliar qualidade
            success_rate = analysis["successful_demos"] / max(analysis["total_demos"], 1)
            analysis["quality_assessment"] = {
                "success_rate": success_rate * 100,
                "system_reliability": "High" if success_rate >= 0.8 else "Medium" if success_rate >= 0.5 else "Low",
                "ready_for_production": success_rate >= 0.8
            }
            
            # Gerar recomendações
            if success_rate >= 0.8:
                analysis["recommendations"].append("✅ Sistema pronto para produção")
                analysis["recommendations"].append("✅ Fase 3 completamente implementada")
            elif success_rate >= 0.5:
                analysis["recommendations"].append("⚠️ Sistema funcional mas precisa de ajustes")
                analysis["recommendations"].append("🔧 Revisar componentes com falhas")
            else:
                analysis["recommendations"].append("❌ Sistema requer correções significativas")
                analysis["recommendations"].append("🔧 Revisar todas as integrações")
            
            self.logger.info(f"📊 Análise concluída: {success_rate*100:.1f}% de sucesso")
            
        except Exception as e:
            analysis["error"] = str(e)
            self.logger.error(f"❌ Erro na análise: {e}")
        
        return analysis
    
    async def _get_final_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas finais de todos os componentes"""
        stats = {}
        
        try:
            # Estatísticas do Workflow
            stats["workflow"] = get_workflow_statistics()
            
            # Estatísticas MCP
            stats["mcp"] = self.mcp_integrations.get_usage_stats()
            
            # Status dos Agentes
            stats["agents"] = {
                "status": get_agents_status(),
                "info": get_agents_info()
            }
            
            # Estatísticas do Demo
            stats["demo"] = {
                "total_topics_tested": len(set(self.demo_topics)),
                "total_demos_executed": len(self.demo_results),
                "demo_results": self.demo_results
            }
            
        except Exception as e:
            stats["error"] = str(e)
            self.logger.error(f"❌ Erro ao obter estatísticas: {e}")
        
        return stats
    
    def save_demo_report(self, results: Dict[str, Any], filename: str = None) -> str:
        """Salva relatório detalhado do demo"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phase3_demo_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"📄 Relatório salvo: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar relatório: {e}")
            return ""

async def main():
    """Função principal do demo"""
    print("🎬 DEMO FASE 3 - ORQUESTRAÇÃO COMPLETA END-TO-END")
    print("=" * 60)
    print()
    
    try:
        # Criar instância do demo
        demo = Phase3Demo()
        
        # Executar demonstração completa
        print("🚀 Iniciando demonstração da Fase 3...")
        results = await demo.run_complete_demo()
        
        # Exibir resumo
        print("\n📊 RESUMO DA DEMONSTRAÇÃO")
        print("-" * 40)
        
        if results["success"]:
            print("✅ Status: SUCESSO")
            print(f"⏱️  Tempo total: {results['execution_time']:.2f}s")
            
            # Exibir resultados dos demos
            demo_results = results["demo_results"]
            
            print(f"\n📝 Demo Básico: {'✅' if demo_results['basic_workflow']['success'] else '❌'}")
            print(f"📱 Demo Completo: {'✅' if demo_results['complete_workflow']['success'] else '❌'}")
            print(f"⚡ Demo Paralelo: {'✅' if demo_results['parallel_workflows']['success'] else '❌'}")
            
            # Exibir análise
            analysis = results["analysis"]
            print(f"\n📈 Taxa de Sucesso: {analysis['quality_assessment']['success_rate']:.1f}%")
            print(f"🎯 Confiabilidade: {analysis['quality_assessment']['system_reliability']}")
            print(f"🚀 Pronto para Produção: {'✅' if analysis['quality_assessment']['ready_for_production'] else '❌'}")
            
            # Exibir recomendações
            print("\n💡 RECOMENDAÇÕES:")
            for rec in analysis["recommendations"]:
                print(f"   {rec}")
            
        else:
            print("❌ Status: FALHA")
            print(f"❌ Erro: {results.get('error', 'Erro desconhecido')}")
        
        # Salvar relatório
        report_file = demo.save_demo_report(results)
        if report_file:
            print(f"\n📄 Relatório detalhado salvo: {report_file}")
        
        print("\n" + "=" * 60)
        print("🎬 DEMONSTRAÇÃO DA FASE 3 CONCLUÍDA")
        
        # Retornar código de saída apropriado
        return 0 if results["success"] else 1
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        logger.error(f"Erro crítico no demo: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        exit(1)
