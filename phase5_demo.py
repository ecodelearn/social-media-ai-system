"""
FASE 5 DEMO - Sistema de Exportação e Saídas Organizadas
======================================================

Demonstração completa do sistema de exportação e organização
de conteúdo gerado pelos agentes.

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - FASE 5
Data: 24/05/2025
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from core.exporters import content_exporter
from core.orchestrator import content_orchestrator
from core.visual_prompt_engine import VisualPromptEngine

async def demo_complete_workflow_with_export():
    """
    Demo completo: Geração de conteúdo + Exportação organizada
    """
    
    print("🚀 FASE 5 DEMO - Sistema de Exportação e Saídas Organizadas")
    print("=" * 60)
    
    # Tópico para demonstração
    topic = "Inteligência Artificial no Marketing Digital 2025"
    
    print(f"\n📝 Tópico: {topic}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    
    # ETAPA 1: Executar workflow completo (Fases 1-4)
    print("\n" + "="*50)
    print("🎬 ETAPA 1: Executando workflow completo...")
    print("="*50)
    
    try:
        # Executar orquestração completa
        crew_results = await content_orchestrator.execute_full_workflow(topic)
        
        print(f"✅ Workflow executado com sucesso!")
        print(f"📊 Resultado final: {len(crew_results.get('final_result', ''))} caracteres")
        
    except Exception as e:
        print(f"❌ Erro no workflow: {e}")
        # Simular resultados para continuar o demo
        crew_results = simulate_crew_results(topic)
        print("🔄 Usando resultados simulados para continuar o demo...")
    
    # ETAPA 2: Preparar dados adicionais
    print("\n" + "="*50)
    print("🔍 ETAPA 2: Preparando dados para exportação...")
    print("="*50)
    
    # Obter dados de pesquisa simulados
    research_data = {
        "search_results": [
            {
                "title": "Tendências de IA no Marketing 2025",
                "summary": "Principais inovações esperadas para o próximo ano",
                "source": "Perplexity AI",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "keywords": ["IA", "marketing digital", "automação", "personalização"],
        "search_timestamp": datetime.now().isoformat()
    }
    
    # Obter prompts visuais
    try:
        visual_engine = VisualPromptEngine()
        visual_results = await visual_engine.generate_visual_prompts(topic)
        visual_prompts = visual_results.get("prompts", [])
        print(f"✅ Prompts visuais gerados: {len(visual_prompts)}")
    except Exception as e:
        print(f"⚠️ Simulando prompts visuais: {e}")
        visual_prompts = [
            "Professional AI-powered marketing dashboard with futuristic holographic displays, sleek interface design, blue and purple gradient colors, modern office setting, high-tech atmosphere",
            "Abstract representation of artificial intelligence in marketing, neural network patterns, data flow visualization, digital marketing icons, clean minimalist style, corporate colors",
            "Marketing team collaborating with AI assistants, diverse professionals, modern workspace, interactive screens, vibrant colors, productive atmosphere"
        ]
    
    print(f"📊 Dados de pesquisa preparados")
    print(f"🎨 Prompts visuais: {len(visual_prompts)}")
    
    # ETAPA 3: Executar exportação
    print("\n" + "="*50)
    print("📦 ETAPA 3: Executando exportação organizada...")
    print("="*50)
    
    try:
        # Exportar lote completo
        export_batch = await content_exporter.export_content_batch(
            topic=topic,
            crew_results=crew_results,
            research_data=research_data,
            visual_prompts=visual_prompts
        )
        
        print(f"✅ Exportação concluída!")
        print(f"🆔 Batch ID: {export_batch.batch_id}")
        print(f"📱 Plataformas exportadas: {len(export_batch.platforms)}")
        
        # Mostrar detalhes das plataformas
        for platform_content in export_batch.platforms:
            print(f"  📲 {platform_content.platform.title()}: {platform_content.metadata['char_count']} chars")
        
    except Exception as e:
        print(f"❌ Erro na exportação: {e}")
        return
    
    # ETAPA 4: Verificar arquivos gerados
    print("\n" + "="*50)
    print("📁 ETAPA 4: Verificando arquivos gerados...")
    print("="*50)
    
    output_dir = Path("output")
    
    # Verificar estrutura de diretórios
    directories_to_check = [
        "content/by_platform",
        "content/by_date",
        "prompts/dall_e",
        "analytics/daily",
        "history"
    ]
    
    for dir_path in directories_to_check:
        full_path = output_dir / dir_path
        if full_path.exists():
            files_count = len(list(full_path.glob("*")))
            print(f"✅ {dir_path}: {files_count} arquivos")
        else:
            print(f"❌ {dir_path}: Não encontrado")
    
    # ETAPA 5: Demonstrar consulta de histórico
    print("\n" + "="*50)
    print("📈 ETAPA 5: Consultando histórico e analytics...")
    print("="*50)
    
    try:
        # Obter histórico
        history = await content_exporter.get_export_history(limit=5)
        print(f"📋 Histórico de exportações: {len(history)} registros")
        
        if history:
            latest = history[-1]
            print(f"  🕐 Último: {latest['topic'][:50]}...")
            print(f"  📱 Plataformas: {', '.join(latest['platforms'])}")
        
        # Obter analytics
        analytics = await content_exporter.get_analytics_summary()
        print(f"\n📊 Analytics do mês:")
        print(f"  📦 Lotes: {analytics['monthly']['batches']}")
        print(f"  📄 Conteúdos: {analytics['monthly']['content_pieces']}")
        print(f"  📱 Plataformas únicas: {analytics['monthly']['unique_platforms']}")
        
        print(f"\n📊 Analytics do dia:")
        print(f"  📦 Lotes: {analytics['daily']['batches']}")
        print(f"  📄 Conteúdos: {analytics['daily']['content_pieces']}")
        
    except Exception as e:
        print(f"⚠️ Erro ao consultar analytics: {e}")
    
    # ETAPA 6: Mostrar arquivos específicos
    print("\n" + "="*50)
    print("🔍 ETAPA 6: Exemplos de arquivos gerados...")
    print("="*50)
    
    try:
        # Encontrar arquivo MD mais recente
        platform_dirs = list((output_dir / "content" / "by_platform").glob("*"))
        
        if platform_dirs:
            sample_platform = platform_dirs[0]
            md_files = list(sample_platform.glob("*.md"))
            
            if md_files:
                sample_file = md_files[-1]  # Mais recente
                print(f"📄 Exemplo de arquivo MD: {sample_file.name}")
                
                # Mostrar primeiras linhas
                with open(sample_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')[:15]
                    preview = '\n'.join(lines)
                    print(f"📖 Preview:")
                    print("-" * 40)
                    print(preview)
                    print("-" * 40)
                    if len(lines) > 15:
                        print("... (arquivo continua)")
        
        # Mostrar prompts visuais salvos
        prompts_file = output_dir / "prompts" / "dall_e" / f"prompts_{datetime.now().strftime('%Y-%m-%d')}.md"
        
        if prompts_file.exists():
            print(f"\n🎨 Prompts visuais salvos: {prompts_file.name}")
            
            with open(prompts_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')[-20:]  # Últimas 20 linhas
                preview = '\n'.join(lines)
                print(f"🎭 Últimos prompts:")
                print("-" * 40)
                print(preview)
                print("-" * 40)
        
    except Exception as e:
        print(f"⚠️ Erro ao mostrar arquivos: {e}")
    
    # FINALIZAÇÃO
    print("\n" + "="*60)
    print("🎉 FASE 5 DEMO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    
    print(f"\n✅ RESULTADOS ALCANÇADOS:")
    print(f"  📦 Lote exportado: {export_batch.batch_id}")
    print(f"  📱 Plataformas: {len(export_batch.platforms)}")
    print(f"  🎨 Prompts visuais: {len(export_batch.visual_prompts)}")
    print(f"  📁 Arquivos organizados por plataforma, data e tópico")
    print(f"  📊 Analytics automáticas atualizadas")
    print(f"  📋 Histórico consultável mantido")
    
    print(f"\n🎯 FUNCIONALIDADES DEMONSTRADAS:")
    print(f"  ✅ Exportação automática por plataforma")
    print(f"  ✅ Arquivos MD bem formatados")
    print(f"  ✅ Prompts visuais organizados")
    print(f"  ✅ Sistema de histórico")
    print(f"  ✅ Analytics básicas funcionando")
    print(f"  ✅ Estrutura de diretórios automática")
    
    print(f"\n📂 ESTRUTURA CRIADA:")
    print(f"  📁 output/content/by_platform/")
    print(f"  📁 output/content/by_date/")
    print(f"  📁 output/prompts/dall_e/")
    print(f"  📁 output/analytics/daily/")
    print(f"  📁 output/analytics/monthly/")
    print(f"  📁 output/history/")
    
    print(f"\n⏰ Demo finalizado em: {datetime.now().strftime('%H:%M:%S')}")
    
    return export_batch

def simulate_crew_results(topic: str) -> dict:
    """Simular resultados do CrewAI para fins de demonstração"""
    
    return {
        "final_result": f"""# {topic}

## Instagram
🚀 A IA está revolucionando o marketing digital! Em 2025, veremos automação inteligente, personalização extrema e ROI otimizado.

✨ Principais tendências:
• Chatbots mais humanos
• Análise preditiva avançada
• Conteúdo gerado por IA
• Segmentação hiper-personalizada

#IA #MarketingDigital #Automacao #Tecnologia #Inovacao #Marketing2025 #IA

## LinkedIn
A Inteligência Artificial está transformando fundamentalmente como fazemos marketing digital. Em 2025, esperamos ver uma revolução completa na forma como as empresas se conectam com seus clientes.

🔍 Análise Preditiva Avançada
As ferramentas de IA agora podem prever comportamentos de compra com precisão de 90%+, permitindo campanhas ultra-direcionadas.

🤖 Automação Inteligente
Chatbots evoluídos que mantêm conversas naturais e resolvem problemas complexos, melhorando drasticamente a experiência do cliente.

📊 Personalização em Escala
Cada cliente recebe uma experiência única, adaptada às suas preferências e histórico de comportamento.

💡 Conteúdo Gerado por IA
Criação automática de conteúdo relevante e envolvente, mantendo a autenticidade da marca.

O futuro do marketing é agora. As empresas que abraçarem essas tecnologias terão vantagem competitiva significativa.

#InteligenciaArtificial #MarketingDigital #Inovacao #Tecnologia #Marketing2025

## Twitter
🤖 IA no marketing 2025: automação inteligente + personalização extrema = ROI explosivo! 

As empresas que não se adaptarem ficarão para trás. O futuro é agora! 

#IA #Marketing #Tech2025

## Facebook
A revolução da Inteligência Artificial no Marketing Digital está apenas começando!

🎯 Imagine um mundo onde cada cliente recebe exatamente o conteúdo que deseja, no momento perfeito, através do canal ideal. Isso não é mais ficção científica - é a realidade de 2025!

📈 As tendências que estão moldando o futuro:

🔮 Análise Preditiva que antecipa desejos
🤖 Chatbots que conversam como humanos  
🎨 Conteúdo criado automaticamente por IA
📊 Segmentação hiper-personalizada
⚡ Automação que otimiza campanhas em tempo real

💰 Empresas já estão vendo:
• 300% de aumento no ROI
• 85% de redução no tempo de criação
• 92% de melhoria na satisfação do cliente

O marketing tradicional está morto. Longa vida ao marketing inteligente! 🚀

#InteligenciaArtificial #MarketingDigital #Automacao #Inovacao #Marketing2025 #IA #Tecnologia

## YouTube
🎬 DESCRIÇÃO COMPLETA: Inteligência Artificial no Marketing Digital 2025

Descubra como a IA está revolucionando completamente o marketing digital e o que esperar para 2025!

📚 NESTE VÍDEO VOCÊ VAI APRENDER:
• As 5 principais tendências de IA no marketing
• Como a automação está mudando o jogo
• Ferramentas práticas que você pode usar hoje
• Casos de sucesso reais de empresas
• Previsões para os próximos anos

🚀 TIMESTAMPS:
00:00 - Introdução
02:30 - Análise Preditiva Avançada
05:45 - Chatbots Inteligentes
08:20 - Personalização em Escala
11:15 - Conteúdo Gerado por IA
14:30 - Ferramentas Recomendadas
17:00 - Casos de Sucesso
20:15 - Previsões 2025
22:45 - Conclusão

💡 RECURSOS MENCIONADOS:
• Link para ferramentas de IA: [em breve]
• E-book gratuito: "IA no Marketing 2025"
• Planilha de ROI calculadora

👍 GOSTOU? Deixe seu like, compartilhe e se inscreva para mais conteúdo sobre tecnologia e marketing!

🔔 Ative o sininho para não perder nenhuma novidade!

#IA #MarketingDigital #Tecnologia #Automacao #Marketing2025 #InteligenciaArtificial #Inovacao #DigitalMarketing #AI #Tech
""",
        "execution_time": "2.5 minutos",
        "agents_used": ["Pesquisador", "Redator", "Designer", "Editor"],
        "approved": True
    }

async def main():
    """Função principal do demo"""
    try:
        export_batch = await demo_complete_workflow_with_export()
        
        # Verificar se a exportação foi bem-sucedida
        if export_batch:
            print(f"\n🎯 EXPORTAÇÃO REALIZADA COM SUCESSO!")
            print(f"🆔 ID do Lote: {export_batch.batch_id}")
            print(f"📂 Verifique a pasta 'output/' para ver todos os arquivos gerados")
        
    except Exception as e:
        print(f"\n❌ ERRO NO DEMO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
