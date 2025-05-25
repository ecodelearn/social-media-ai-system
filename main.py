#!/usr/bin/env python3
"""
Social Media AI System - Main Entry Point

Sistema avançado de orquestração de agentes IA para criação de conteúdo profissional 
para redes sociais.

Autor: Sistema de IA Colaborativo
Versão: 1.0.0
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Adicionar o diretório atual ao path para imports
sys.path.append(str(Path(__file__).parent))

def print_banner():
    """Exibe o banner inicial do sistema"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    🚀 SOCIAL MEDIA AI SYSTEM                     ║
    ║                                                                  ║
    ║        Sistema avançado de criação de conteúdo para              ║
    ║              Instagram • WhatsApp • LinkedIn                     ║
    ║                                                                  ║
    ║    🔍 Pesquisa Automática  •  ✍️ Redação SEO  •  🎨 Prompts     ║
    ║    🎬 Editor IA Rigoroso   •  📱 Envio WhatsApp  •  💾 Export   ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"    📅 Iniciado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"    🏗️ Versão: 1.0.0 - Fase 1 (Desenvolvimento)")
    print(f"    👨‍💻 Desenvolvido por: Sistema de IA Colaborativo")
    print("")

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO AMBIENTE...")
    
    # Verificar se o arquivo .env existe
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado!")
        print("📝 Copiando .env.example para .env...")
        
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Arquivo .env criado a partir do .env.example")
            print("🔧 Configure suas chaves de API no arquivo .env")
        else:
            print("❌ Arquivo .env.example não encontrado!")
            return False
    
    # Carregar variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Variáveis de ambiente carregadas")
    except ImportError:
        print("❌ python-dotenv não instalado. Execute: pip install python-dotenv")
        return False
    
    # Verificar chaves de API obrigatórias
    required_keys = {
        "GOOGLE_API_KEY": "Google Gemini (agentes Pesquisador e Redator)",
        "OPENAI_API_KEY": "OpenAI GPT-4o-mini (agentes Visual e Editor)"
    }
    
    missing_keys = []
    for key, description in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"  🔑 {key} - {description}")
    
    if missing_keys:
        print("❌ CHAVES DE API OBRIGATÓRIAS NÃO CONFIGURADAS:")
        for key in missing_keys:
            print(key)
        print("")
        print("📝 Configure as chaves no arquivo .env e execute novamente.")
        return False
    
    print("✅ Chaves de API obrigatórias configuradas")
    
    # Verificar dependências
    try:
        import crewai
        print("✅ CrewAI disponível")
    except ImportError:
        print("❌ CrewAI não instalado. Execute: pip install -r requirements.txt")
        return False
    
    try:
        import openai
        print("✅ OpenAI disponível")
    except ImportError:
        print("❌ OpenAI não instalado. Execute: pip install -r requirements.txt")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI disponível")
    except ImportError:
        print("❌ Google Generative AI não instalado. Execute: pip install -r requirements.txt")
        return False
    
    return True

def show_development_status():
    """Mostra o status atual do desenvolvimento"""
    print("📊 STATUS DO DESENVOLVIMENTO:")
    print("")
    
    phases = [
        ("🎯 FASE 1: FUNDAÇÃO", "🔄 EM DESENVOLVIMENTO", "yellow"),
        ("🎯 FASE 2: RAG VISUAL", "⏳ AGUARDANDO", "gray"),
        ("🎯 FASE 3: ORQUESTRAÇÃO", "⏳ AGUARDANDO", "gray"),
        ("🎯 FASE 4: INTEGRAÇÃO MCP", "⏳ AGUARDANDO", "gray"),
        ("🎯 FASE 5: SAÍDAS E EXPORTAÇÃO", "⏳ AGUARDANDO", "gray"),
        ("🎯 FASE 6: PREPARAÇÃO API", "⏳ AGUARDANDO", "gray"),
    ]
    
    for phase, status, _ in phases:
        print(f"    {phase:<30} {status}")
    
    print("")
    print("🏗️ ESTRUTURA ATUAL:")
    print("    ✅ Pastas organizadas")
    print("    ✅ Documentação completa") 
    print("    ✅ Roadmap detalhado")
    print("    🔄 Implementando configurações")
    print("")

def show_next_steps():
    """Mostra os próximos passos do desenvolvimento"""
    print("⏭️ PRÓXIMOS PASSOS (FASE 1):")
    print("")
    print("    1. 🔧 Implementar config/settings.py")
    print("    2. 🧠 Criar core/llm_manager.py") 
    print("    3. 🤖 Definir core/agents.py")
    print("    4. 🔗 Configurar core/mcp_integrations.py")
    print("")
    print("📚 DOCUMENTAÇÃO DISPONÍVEL:")
    print("    📋 DEVELOPMENT_ROADMAP.md - Roadmap completo")
    print("    🎯 PROJECT_CONTEXT.md - Contexto e filosofia")
    print("    📖 README.md - Documentação principal")
    print("")

def show_menu():
    """Exibe o menu principal"""
    print("🎯 MENU PRINCIPAL:")
    print("")
    print("    1. 🚀 Desenvolver Fase 1 (Configurações)")
    print("    2. 📋 Ver Roadmap Completo")
    print("    3. 🎯 Ver Contexto do Projeto")
    print("    4. 🔧 Verificar Configuração")
    print("    5. 📊 Ver Status Desenvolvimento")
    print("    6. ❌ Sair")
    print("")

def open_file(filepath):
    """Abre um arquivo no editor padrão do sistema"""
    import subprocess
    import platform
    
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        elif platform.system() == "Windows":  # Windows
            os.startfile(filepath)
        else:  # Linux
            subprocess.call(["xdg-open", filepath])
        print(f"📂 Arquivo {filepath} aberto no editor padrão")
    except Exception as e:
        print(f"❌ Erro ao abrir arquivo: {e}")
        print(f"📝 Abra manualmente: {filepath}")

async def develop_phase1():
    """Inicia o desenvolvimento da Fase 1"""
    print("🚀 INICIANDO DESENVOLVIMENTO DA FASE 1...")
    print("")
    print("📁 A Fase 1 inclui:")
    print("    🔧 Configurações do sistema")
    print("    🧠 Gerenciador de LLMs")
    print("    🤖 Definição dos 4 agentes")
    print("    🔗 Integrações MCP básicas")
    print("")
    
    # Por enquanto, apenas mostrar o que seria feito
    print("🔄 Esta funcionalidade será implementada em breve...")
    print("📝 Continue acompanhando o desenvolvimento no roadmap!")
    print("")

def main():
    """Função principal"""
    print_banner()
    
    # Verificar ambiente
    if not check_environment():
        print("❌ Configuração incompleta. Corrija os problemas acima e execute novamente.")
        sys.exit(1)
    
    print("")
    show_development_status()
    show_next_steps()
    
    # Menu principal
    while True:
        show_menu()
        
        try:
            choice = input("🔢 Escolha uma opção (1-6): ").strip()
            print("")
            
            if choice == "1":
                asyncio.run(develop_phase1())
                
            elif choice == "2":
                print("📋 Abrindo DEVELOPMENT_ROADMAP.md...")
                open_file("DEVELOPMENT_ROADMAP.md")
                
            elif choice == "3":
                print("🎯 Abrindo PROJECT_CONTEXT.md...")
                open_file("PROJECT_CONTEXT.md")
                
            elif choice == "4":
                print("🔧 Verificando configuração novamente...")
                check_environment()
                
            elif choice == "5":
                show_development_status()
                
            elif choice == "6":
                print("👋 Obrigado por usar o Social Media AI System!")
                print("🚀 Continue acompanhando o desenvolvimento!")
                sys.exit(0)
                
            else:
                print("❌ Opção inválida. Escolha entre 1-6.")
            
            print("")
            input("⏳ Pressione ENTER para continuar...")
            print("\n" + "="*70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Sistema interrompido pelo usuário. Até logo!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            print("🔄 Retornando ao menu principal...")

if __name__ == "__main__":
    main()
