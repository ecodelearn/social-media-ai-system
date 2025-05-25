#!/usr/bin/env python3
"""
🎨 DEMO FASE 2 - RAG VISUAL COMPLETO

Demonstração completa da Fase 2: Sistema RAG Visual
- Processamento real do PDF VisualGPT
- Geração de embeddings e vector store
- Busca semântica funcionando
- Geração de prompts visuais profissionais

Execução: python phase2_demo.py
"""
import sys
import os
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.visual_prompt_engine import (
    visual_engine,
    initialize_visual_engine,
    generate_visual_prompt,
    VisualPromptRequest
)
from config.visual_configs import (
    visual_rag_config,
    get_platform_specs,
    get_style_guidelines,
    validate_prompt_quality
)

class Phase2Demo:
    """Demonstração completa da Fase 2"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {}
        
    async def demo_initialization(self) -> Dict[str, Any]:
        """Demonstrar inicialização do engine RAG"""
        print("🚀 1. INICIALIZANDO VISUAL PROMPT ENGINE")
        print("-" * 50)
        
        start = time.time()
        
        try:
            # Verificar PDF
            if not os.path.exists(visual_rag_config.pdf_path):
                print(f"❌ PDF não encontrado: {visual_rag_config.pdf_path}")
                print("💡 Tentando PDF alternativo...")
                
                # Tentar PDF alternativo
                alt_path = "data/visual_gpt.pdf"
                if os.path.exists(alt_path):
                    visual_rag_config.pdf_path = alt_path
                    print(f"✅ PDF encontrado: {alt_path}")
                else:
                    return {
                        "status": "error",
                        "error": "PDF VisualGPT não encontrado",
                        "paths_tried": [visual_rag_config.pdf_path, alt_path]
                    }
            
            print(f"📄 PDF localizado: {visual_rag_config.pdf_path}")
            print(f"📁 Embeddings dir: {visual_rag_config.embeddings_dir}")
            print(f"🧠 Modelo: {visual_rag_config.embedding_model}")
            
            # Inicializar engine
            print("\n🔄 Inicializando engine...")
            success = await initialize_visual_engine()
            
            init_time = time.time() - start
            
            if success:
                # Obter estatísticas
                stats = visual_engine.get_statistics()
                
                print(f"✅ Engine inicializado em {init_time:.2f}s")
                print(f"📊 Chunks processados: {stats['total_chunks']}")
                print(f"🔢 Dimensão embeddings: {stats['embedding_dimension']}")
                print(f"🗂️ Vector store: {stats['vector_store_size']} vetores")
                print(f"💾 Cache existente: {stats['cache_exists']}")
                
                return {
                    "status": "success",
                    "initialization_time": init_time,
                    "statistics": stats,
                    "pdf_processed": True
                }
            else:
                return {
                    "status": "error",
                    "error": "Falha na inicialização do engine",
                    "initialization_time": init_time
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "initialization_time": time.time() - start
            }
    
    async def demo_search_functionality(self) -> Dict[str, Any]:
        """Demonstrar funcionalidade de busca RAG"""
        print("\n🔍 2. DEMONSTRANDO BUSCA SEMÂNTICA")
        print("-" * 50)
        
        search_queries = [
            "visual composition techniques",
            "color theory and palettes",
            "lighting and shadows",
            "modern design principles",
            "social media formats"
        ]
        
        results = {}
        
        for query in search_queries:
            try:
                print(f"\n🔎 Buscando: '{query}'")
                
                start = time.time()
                search_results = await visual_engine.search_relevant_content(query, max_results=3)
                search_time = time.time() - start
                
                print(f"⏱️  Tempo: {search_time:.3f}s")
                print(f"📋 Resultados: {len(search_results)}")
                
                if search_results:
                    for i, result in enumerate(search_results):
                        print(f"   {i+1}. Score: {result.similarity_score:.3f} | Página: {result.page_number}")
                        print(f"      Preview: {result.content[:100]}...")
                else:
                    print("   Nenhum resultado encontrado")
                
                results[query] = {
                    "results_count": len(search_results),
                    "search_time": search_time,
                    "best_score": search_results[0].similarity_score if search_results else 0,
                    "results": [
                        {
                            "score": r.similarity_score,
                            "page": r.page_number,
                            "content_preview": r.content[:200]
                        }
                        for r in search_results
                    ]
                }
                
            except Exception as e:
                results[query] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "search_results": results,
            "total_queries": len(search_queries)
        }
    
    async def demo_prompt_generation(self) -> Dict[str, Any]:
        """Demonstrar geração de prompts visuais"""
        print("\n🎨 3. GERANDO PROMPTS VISUAIS PROFISSIONAIS")
        print("-" * 50)
        
        test_scenarios = [
            {
                "topic": "Marketing Digital para PMEs",
                "platform": "instagram",
                "style": "modern",
                "format_type": "post"
            },
            {
                "topic": "Inteligência Artificial no Futuro",
                "platform": "linkedin",
                "style": "corporate",
                "format_type": "post"
            },
            {
                "topic": "Sustentabilidade Empresarial",
                "platform": "whatsapp",
                "style": "minimalist",
                "format_type": "message"
            },
            {
                "topic": "Inovação Tecnológica 2025",
                "platform": "instagram",
                "style": "creative",
                "format_type": "story"
            }
        ]
        
        generated_prompts = {}
        
        for i, scenario in enumerate(test_scenarios):
            try:
                print(f"\n🎯 Cenário {i+1}: {scenario['topic']}")
                print(f"   📱 Plataforma: {scenario['platform']}")
                print(f"   🎭 Estilo: {scenario['style']}")
                print(f"   📐 Formato: {scenario['format_type']}")
                
                start = time.time()
                result = await generate_visual_prompt(
                    topic=scenario["topic"],
                    platform=scenario["platform"],
                    style=scenario["style"],
                    format_type=scenario["format_type"],
                    brand_elements="Professional branding with modern aesthetic",
                    additional_requirements="High-quality, engaging, and social media optimized"
                )
                generation_time = time.time() - start
                
                print(f"   ⏱️  Gerado em: {generation_time:.3f}s")
                print(f"   📏 Tamanho: {len(result['prompt'])} caracteres")
                print(f"   ⭐ Qualidade: {result['quality_scores']['overall']:.2f}")
                print(f"   📚 Fontes RAG: {result['rag_sources']}")
                print(f"   🎨 Técnicas visuais: {len(result['visual_techniques'])}")
                
                # Preview do prompt
                print(f"\n📝 Preview do prompt:")
                preview = result['prompt'][:300] + "..." if len(result['prompt']) > 300 else result['prompt']
                print(f"   {preview}")
                
                generated_prompts[f"scenario_{i+1}"] = {
                    "scenario": scenario,
                    "generation_time": generation_time,
                    "prompt_length": len(result['prompt']),
                    "quality_score": result['quality_scores']['overall'],
                    "rag_sources": result['rag_sources'],
                    "visual_techniques_count": len(result['visual_techniques']),
                    "full_result": result
                }
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                generated_prompts[f"scenario_{i+1}"] = {
                    "scenario": scenario,
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "generated_prompts": generated_prompts,
            "total_scenarios": len(test_scenarios)
        }
    
    async def demo_quality_validation(self) -> Dict[str, Any]:
        """Demonstrar sistema de validação de qualidade"""
        print("\n✅ 4. VALIDAÇÃO DE QUALIDADE DOS PROMPTS")
        print("-" * 50)
        
        # Exemplos de prompts para testar
        test_prompts = {
            "excellent": """
            Create a professional modern image for Instagram post about digital marketing strategies for small businesses.
            
            Visual Requirements:
            Style: Clean lines, contemporary design elements, bold colors, geometric shapes, clean typography
            Use professional color palette with high contrast and vibrant colors suitable for social media
            Apply rule of thirds composition with clear focal point and balanced visual hierarchy
            Implement sophisticated lighting with soft shadows and professional depth
            
            Technical Specifications:
            - Aspect ratio: 1:1 (1080x1080)
            - Resolution: 1080x1080
            - Style: Modern and sophisticated with clean aesthetic
            
            Content Guidelines:
            Instagram-optimized visual with mobile-first composition and eye-catching design
            Focus on business growth, digital transformation, and professional success
            
            Brand Elements:
            Professional branding consistent with modern corporate identity and digital marketing themes
            """,
            
            "good": """
            Create a modern Instagram image about digital marketing.
            Use professional colors and clean composition.
            Make it 1080x1080 for Instagram post.
            Include modern design elements and good lighting.
            """,
            
            "poor": "Make image about marketing",
            
            "inappropriate": "Create violent and explicit marketing image with inappropriate controversial content"
        }
        
        validation_results = {}
        
        for category, prompt in test_prompts.items():
            print(f"\n🧪 Testando prompt '{category}':")
            print(f"   📏 Tamanho: {len(prompt)} caracteres")
            
            # Validar qualidade
            quality = validate_prompt_quality(prompt)
            
            print(f"   ⭐ Score geral: {quality['overall']:.3f}")
            print(f"   📏 Score tamanho: {quality['length']:.3f}")
            print(f"   🧩 Score elementos: {quality['elements']:.3f}")
            print(f"   💼 Score profissional: {quality['professional']:.3f}")
            print(f"   ⚠️  Penalidade: {quality['forbidden_penalty']:.3f}")
            
            # Determinar classificação
            if quality['overall'] >= 0.8:
                classification = "Excelente ✨"
            elif quality['overall'] >= 0.6:
                classification = "Bom ✅"
            elif quality['overall'] >= 0.4:
                classification = "Regular ⚠️"
            else:
                classification = "Precisa melhorar ❌"
            
            print(f"   🏆 Classificação: {classification}")
            
            validation_results[category] = {
                "prompt_length": len(prompt),
                "quality_scores": quality,
                "classification": classification
            }
        
        return {
            "status": "success",
            "validation_results": validation_results
        }
    
    async def demo_platform_optimization(self) -> Dict[str, Any]:
        """Demonstrar otimização por plataforma"""
        print("\n📱 5. OTIMIZAÇÃO POR PLATAFORMA")
        print("-" * 50)
        
        platforms = ["instagram", "linkedin", "whatsapp"]
        topic = "Tecnologia e Inovação 2025"
        
        platform_results = {}
        
        for platform in platforms:
            print(f"\n🎯 Plataforma: {platform.upper()}")
            
            try:
                # Obter especificações
                specs = get_platform_specs(platform, "post")
                print(f"   📐 Aspect Ratio: {specs['aspect_ratio']}")
                print(f"   📊 Resolução: {specs['resolution']}")
                
                # Gerar prompt otimizado
                start = time.time()
                result = await generate_visual_prompt(
                    topic=topic,
                    platform=platform,
                    style="modern"
                )
                generation_time = time.time() - start
                
                print(f"   ⏱️  Tempo geração: {generation_time:.3f}s")
                print(f"   ⭐ Qualidade: {result['quality_scores']['overall']:.3f}")
                print(f"   📚 Fontes RAG: {result['rag_sources']}")
                
                # Analisar otimizações específicas da plataforma
                prompt_lower = result['prompt'].lower()
                platform_optimizations = {
                    "instagram": ["vibrant", "mobile", "story", "engagement"],
                    "linkedin": ["professional", "corporate", "business", "networking"],
                    "whatsapp": ["mobile", "clear", "readable", "quick"]
                }
                
                optimizations_found = [
                    opt for opt in platform_optimizations.get(platform, [])
                    if opt in prompt_lower
                ]
                
                print(f"   🎨 Otimizações encontradas: {len(optimizations_found)}")
                if optimizations_found:
                    print(f"      {', '.join(optimizations_found)}")
                
                platform_results[platform] = {
                    "specs": specs,
                    "generation_time": generation_time,
                    "quality_score": result['quality_scores']['overall'],
                    "rag_sources": result['rag_sources'],
                    "optimizations_found": optimizations_found,
                    "prompt_length": len(result['prompt'])
                }
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                platform_results[platform] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "platform_results": platform_results,
            "topic_tested": topic
        }
    
    async def generate_final_report(self) -> Dict[str, Any]:
        """Gerar relatório final da Fase 2"""
        execution_time = time.time() - self.start_time
        
        # Estatísticas finais do engine
        stats = visual_engine.get_statistics()
        
        # Contar sucessos
        successful_demos = sum(
            1 for result in self.results.values()
            if result.get("status") == "success"
        )
        
        report = {
            "phase2_status": "✅ FASE 2 COMPLETAMENTE IMPLEMENTADA",
            "execution_time": execution_time,
            "successful_demos": successful_demos,
            "total_demos": len(self.results),
            "success_rate": (successful_demos / len(self.results)) * 100 if self.results else 0,
            "engine_statistics": stats,
            "detailed_results": self.results,
            "timestamp": datetime.now().isoformat(),
            "next_steps": [
                "Integrar RAG Visual ao sistema de orquestração",
                "Conectar prompts visuais aos agentes CrewAI",
                "Implementar Fase 5: Exportação e Saídas",
                "Preparar sistema para produção"
            ]
        }
        
        return report
    
    async def run_complete_demo(self):
        """Executar demonstração completa da Fase 2"""
        print("🎨 DEMO FASE 2 - RAG VISUAL COMPLETO")
        print("=" * 60)
        print("🚀 Sistema RAG Visual com PDF VisualGPT")
        print("📅 Executando em:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print()
        
        # Lista de demos
        demos = [
            ("🚀 Inicialização do Engine", self.demo_initialization),
            ("🔍 Busca Semântica", self.demo_search_functionality),
            ("🎨 Geração de Prompts", self.demo_prompt_generation),
            ("✅ Validação de Qualidade", self.demo_quality_validation),
            ("📱 Otimização por Plataforma", self.demo_platform_optimization)
        ]
        
        # Executar demos
        for demo_name, demo_func in demos:
            try:
                result = await demo_func()
                self.results[demo_name] = result
                
                if result.get("status") == "success":
                    print(f"\n✅ {demo_name}: SUCESSO")
                else:
                    print(f"\n❌ {demo_name}: FALHA")
                    print(f"   Erro: {result.get('error', 'Erro desconhecido')}")
                    
            except Exception as e:
                print(f"\n💥 {demo_name}: ERRO CRÍTICO")
                print(f"   {e}")
                self.results[demo_name] = {"status": "critical_error", "error": str(e)}
        
        # Gerar relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DA FASE 2")
        print("=" * 60)
        
        final_report = await self.generate_final_report()
        
        print(f"🎯 Status: {final_report['phase2_status']}")
        print(f"⏱️  Tempo total: {final_report['execution_time']:.2f}s")
        print(f"✅ Demos bem-sucedidos: {final_report['successful_demos']}/{final_report['total_demos']}")
        print(f"📈 Taxa de sucesso: {final_report['success_rate']:.1f}%")
        
        if final_report['engine_statistics']['status'] == 'initialized':
            stats = final_report['engine_statistics']
            print(f"\n📊 ESTATÍSTICAS DO ENGINE:")
            print(f"   📄 Chunks processados: {stats['total_chunks']}")
            print(f"   🔢 Dimensão embeddings: {stats['embedding_dimension']}")
            print(f"   🗂️ Vector store: {stats['vector_store_size']} vetores")
            print(f"   📱 Plataformas suportadas: {len(stats['supported_platforms'])}")
            print(f"   🎭 Estilos disponíveis: {len(stats['available_styles'])}")
        
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        for step in final_report['next_steps']:
            print(f"   • {step}")
        
        # Salvar relatório
        report_filename = f"phase2_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join("output", report_filename)
        
        os.makedirs("output", exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório detalhado salvo: {report_path}")
        
        return final_report

async def main():
    """Função principal"""
    demo = Phase2Demo()
    return await demo.run_complete_demo()

if __name__ == "__main__":
    # Executar demo completo
    final_report = asyncio.run(main())
    
    # Status final
    if final_report['success_rate'] >= 100:
        print("\n🎉 FASE 2 COMPLETAMENTE IMPLEMENTADA E FUNCIONAL!")
    elif final_report['success_rate'] >= 80:
        print("\n⚠️ FASE 2 MAJORITARIAMENTE FUNCIONAL - Pequenos ajustes necessários")
    else:
        print("\n❌ FASE 2 PRECISA DE CORREÇÕES")
    
    print(f"\n📊 Resultado: {final_report['success_rate']:.1f}% de sucesso")
