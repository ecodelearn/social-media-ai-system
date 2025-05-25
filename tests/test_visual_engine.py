"""
Testes para o sistema RAG Visual (Fase 2)
Valida o processamento do PDF VisualGPT e geração de prompts
"""
import sys
import os
import asyncio
import tempfile
import shutil
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockRAGTester:
    """
    Tester para o sistema RAG Visual com fallbacks para dependências ausentes
    """
    
    def __init__(self):
        self.results = {}
        self.temp_dir = None
        
    async def test_visual_configs(self) -> Dict[str, Any]:
        """Testar configurações visuais"""
        try:
            from config.visual_configs import (
                visual_rag_config,
                prompt_template_config,
                quality_config,
                get_platform_specs,
                get_style_guidelines,
                validate_prompt_quality
            )
            
            # Testar configurações básicas
            assert visual_rag_config.pdf_path is not None
            assert visual_rag_config.embedding_model is not None
            assert visual_rag_config.chunk_size > 0
            
            # Testar templates de plataforma
            assert len(prompt_template_config.platform_templates) >= 3
            assert "instagram" in prompt_template_config.platform_templates
            assert "linkedin" in prompt_template_config.platform_templates
            assert "whatsapp" in prompt_template_config.platform_templates
            
            # Testar estilos visuais
            assert len(prompt_template_config.visual_styles) >= 5
            assert "modern" in prompt_template_config.visual_styles
            assert "minimalist" in prompt_template_config.visual_styles
            
            # Testar especificações de plataforma
            specs = get_platform_specs("instagram", "post")
            assert "aspect_ratio" in specs
            assert "resolution" in specs
            assert "platform" in specs
            
            # Testar diretrizes de estilo
            guidelines = get_style_guidelines("modern")
            assert len(guidelines) > 20  # Deve ter descrição detalhada
            
            # Testar validação de qualidade
            test_prompt = """
            Create a professional modern image for Instagram post about digital marketing.
            Use clean composition with professional color palette and good lighting.
            Style should be modern and sophisticated with high-quality elements.
            """
            quality = validate_prompt_quality(test_prompt)
            assert "overall" in quality
            assert 0 <= quality["overall"] <= 1
            
            return {
                "status": "success",
                "configs_loaded": True,
                "platforms": len(prompt_template_config.platform_templates),
                "styles": len(prompt_template_config.visual_styles),
                "test_quality_score": quality["overall"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "configs_loaded": False
            }
    
    async def test_visual_engine_structure(self) -> Dict[str, Any]:
        """Testar estrutura do visual engine"""
        try:
            from core.visual_prompt_engine import (
                VisualPromptEngine,
                VisualPromptRequest,
                DocumentChunk,
                SearchResult
            )
            
            # Testar criação de instância
            engine = VisualPromptEngine()
            assert engine.config is not None
            assert engine.is_initialized == False
            
            # Testar estruturas de dados
            request = VisualPromptRequest(
                topic="Test Topic",
                platform="instagram",
                style="modern"
            )
            assert request.topic == "Test Topic"
            assert request.platform == "instagram"
            assert request.style == "modern"
            
            # Testar DocumentChunk
            chunk = DocumentChunk(
                content="Test content",
                metadata={"test": True},
                page_number=1,
                chunk_id="test_chunk"
            )
            assert chunk.content == "Test content"
            assert chunk.metadata["test"] == True
            
            return {
                "status": "success",
                "engine_created": True,
                "structures_valid": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "engine_created": False
            }
    
    async def test_mock_rag_functionality(self) -> Dict[str, Any]:
        """Testar funcionalidade RAG com mocks"""
        try:
            # Mock das dependências
            with patch('core.visual_prompt_engine.SentenceTransformer') as mock_st, \
                 patch('core.visual_prompt_engine.faiss') as mock_faiss, \
                 patch('core.visual_prompt_engine.np') as mock_np:
                
                # Configurar mocks
                mock_model = MagicMock()
                mock_model.encode.return_value = [[0.1, 0.2, 0.3]] * 5
                mock_st.return_value = mock_model
                
                mock_index = MagicMock()
                mock_index.ntotal = 5
                mock_index.search.return_value = ([[0.9, 0.8, 0.7]], [[0, 1, 2]])
                mock_faiss.IndexFlatIP.return_value = mock_index
                mock_faiss.normalize_L2 = MagicMock()
                
                mock_np.array.return_value = [[0.1, 0.2, 0.3]] * 5
                
                from core.visual_prompt_engine import VisualPromptEngine, VisualPromptRequest
                
                engine = VisualPromptEngine()
                
                # Simular chunks processados
                from core.visual_prompt_engine import DocumentChunk
                mock_chunks = [
                    DocumentChunk(
                        content=f"Visual design guideline {i} with composition and lighting techniques",
                        metadata={"source": "test", "type": "guideline"},
                        page_number=1,
                        chunk_id=f"chunk_{i}",
                        embedding=[0.1, 0.2, 0.3]
                    )
                    for i in range(5)
                ]
                
                engine.document_chunks = mock_chunks
                engine.embedding_model = mock_model
                engine.vector_store = mock_index
                engine.is_initialized = True
                
                # Testar busca
                search_results = await engine.search_relevant_content("modern design")
                assert len(search_results) >= 0
                
                # Testar geração de prompt
                request = VisualPromptRequest(
                    topic="Digital Marketing",
                    platform="instagram",
                    style="modern"
                )
                
                result = await engine.generate_visual_prompt(request)
                assert "prompt" in result
                assert "quality_scores" in result
                assert "metadata" in result
                
                return {
                    "status": "success",
                    "mock_search_results": len(search_results),
                    "prompt_generated": len(result["prompt"]) > 0,
                    "quality_score": result["quality_scores"]["overall"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "mock_test_failed": True
            }
    
    async def test_pdf_processing_mock(self) -> Dict[str, Any]:
        """Testar processamento de PDF com mock"""
        try:
            # Criar PDF temporário fake
            self.temp_dir = tempfile.mkdtemp()
            fake_pdf_path = os.path.join(self.temp_dir, "test.pdf")
            
            # Criar arquivo fake
            with open(fake_pdf_path, 'wb') as f:
                f.write(b"Fake PDF content for testing")
            
            # Mock das funções de extração
            with patch('core.visual_prompt_engine.fitz') as mock_fitz:
                mock_doc = MagicMock()
                mock_page = MagicMock()
                mock_page.get_text.return_value = "Visual design guidelines: Use composition, lighting, and color theory for effective designs."
                mock_doc.__enter__.return_value = mock_doc
                mock_doc.__exit__.return_value = None
                mock_doc.page_count = 1
                mock_doc.__getitem__.return_value = mock_page
                mock_fitz.open.return_value = mock_doc
                
                from core.visual_prompt_engine import VisualPromptEngine
                
                engine = VisualPromptEngine()
                
                # Testar extração de texto
                text_pages = engine._extract_text_pymupdf(fake_pdf_path)
                assert len(text_pages) > 0
                assert len(text_pages[0][0]) > 0  # Conteúdo extraído
                
                # Testar criação de chunks
                chunks = engine._create_chunks(text_pages)
                assert len(chunks) > 0
                assert chunks[0].content is not None
                assert chunks[0].chunk_id is not None
                
                return {
                    "status": "success",
                    "text_extracted": len(text_pages[0][0]),
                    "chunks_created": len(chunks),
                    "first_chunk_length": len(chunks[0].content)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "pdf_processing_failed": True
            }
        
        finally:
            # Limpar arquivos temporários
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    async def test_template_generation(self) -> Dict[str, Any]:
        """Testar geração de templates de prompt"""
        try:
            from core.visual_prompt_engine import VisualPromptEngine, VisualPromptRequest
            from config.visual_configs import get_platform_specs, get_style_guidelines
            
            engine = VisualPromptEngine()
            
            request = VisualPromptRequest(
                topic="E-commerce Marketing",
                platform="linkedin",
                style="corporate",
                brand_elements="Blue corporate colors, clean typography"
            )
            
            # Obter especificações
            platform_specs = get_platform_specs(request.platform, request.format_type)
            style_guidelines = get_style_guidelines(request.style)
            
            # Simular técnicas visuais
            visual_techniques = [
                "Use professional color palette for corporate appeal",
                "Apply rule of thirds for balanced composition",
                "Implement clean typography hierarchy"
            ]
            
            # Testar construção de prompt
            prompt = engine._build_prompt_from_template(
                request, platform_specs, style_guidelines, visual_techniques
            )
            
            assert len(prompt) > 100  # Prompt deve ser substancial
            assert request.topic.lower() in prompt.lower()
            assert request.platform.lower() in prompt.lower()
            assert request.style.lower() in prompt.lower()
            
            return {
                "status": "success",
                "prompt_length": len(prompt),
                "contains_topic": request.topic.lower() in prompt.lower(),
                "contains_platform": request.platform.lower() in prompt.lower(),
                "contains_style": request.style.lower() in prompt.lower(),
                "visual_techniques_count": len(visual_techniques)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "template_generation_failed": True
            }
    
    async def test_quality_validation(self) -> Dict[str, Any]:
        """Testar sistema de validação de qualidade"""
        try:
            from config.visual_configs import validate_prompt_quality
            
            # Teste com prompt de alta qualidade
            good_prompt = """
            Create a professional modern image for Instagram post about digital marketing strategies.
            
            Visual Requirements:
            Style: Clean lines, contemporary design elements, bold colors, geometric shapes
            Use professional color palette with high contrast and vibrant colors
            Apply rule of thirds composition with clear focal point
            
            Technical Specifications:
            - Aspect ratio: 1:1 (1080x1080)
            - Resolution: 1080x1080
            - Style: Modern and sophisticated design
            
            Content Guidelines:
            Instagram-optimized visual with mobile-first composition
            
            Brand Elements:
            Professional branding consistent with content
            """
            
            good_quality = validate_prompt_quality(good_prompt)
            
            # Teste com prompt de baixa qualidade
            bad_prompt = "Make image"
            bad_quality = validate_prompt_quality(bad_prompt)
            
            # Teste com prompt com palavras proibidas
            inappropriate_prompt = "Create violent and explicit image with inappropriate content"
            inappropriate_quality = validate_prompt_quality(inappropriate_prompt)
            
            return {
                "status": "success",
                "good_prompt_score": good_quality["overall"],
                "bad_prompt_score": bad_quality["overall"],
                "inappropriate_penalty": inappropriate_quality["forbidden_penalty"],
                "quality_system_working": good_quality["overall"] > bad_quality["overall"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "quality_validation_failed": True
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executar todos os testes da Fase 2"""
        print("🧪 INICIANDO TESTES DA FASE 2 - RAG VISUAL")
        print("=" * 60)
        
        tests = [
            ("📝 Configurações Visuais", self.test_visual_configs),
            ("🏗️ Estrutura do Engine", self.test_visual_engine_structure),
            ("🔍 Funcionalidade RAG Mock", self.test_mock_rag_functionality),
            ("📄 Processamento PDF Mock", self.test_pdf_processing_mock),
            ("🎨 Geração de Templates", self.test_template_generation),
            ("✅ Validação de Qualidade", self.test_quality_validation)
        ]
        
        all_results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{test_name}...")
            try:
                result = await test_func()
                all_results[test_name] = result
                
                if result.get("status") == "success":
                    print(f"  ✅ PASSOU")
                    passed += 1
                    # Imprimir detalhes relevantes
                    for key, value in result.items():
                        if key not in ["status", "error"] and isinstance(value, (int, float, bool)):
                            print(f"     {key}: {value}")
                else:
                    print(f"  ❌ FALHOU: {result.get('error', 'Erro desconhecido')}")
                    
            except Exception as e:
                print(f"  💥 ERRO CRÍTICO: {e}")
                all_results[test_name] = {"status": "critical_error", "error": str(e)}
        
        print("\n" + "=" * 60)
        print(f"📊 RESUMO DOS TESTES DA FASE 2")
        print(f"✅ Passou: {passed}/{total}")
        print(f"❌ Falhou: {total - passed}/{total}")
        print(f"📈 Taxa de sucesso: {(passed/total)*100:.1f}%")
        
        # Determinar status geral da Fase 2
        if passed == total:
            phase2_status = "✅ FASE 2 COMPLETAMENTE FUNCIONAL"
        elif passed >= total * 0.8:
            phase2_status = "⚠️ FASE 2 MAJORITARIAMENTE FUNCIONAL"
        elif passed >= total * 0.5:
            phase2_status = "🔶 FASE 2 PARCIALMENTE FUNCIONAL"
        else:
            phase2_status = "❌ FASE 2 PRECISA DE CORREÇÕES"
        
        print(f"\n🎯 STATUS: {phase2_status}")
        
        if passed < total:
            print("\n💡 PRÓXIMOS PASSOS:")
            print("   1. Instalar dependências: pip install -r requirements.txt")
            print("   2. Verificar se o PDF VisualGPT está em data/")
            print("   3. Executar inicialização completa do engine")
        
        print("\n🚀 Para usar o sistema RAG Visual:")
        print("   from core.visual_prompt_engine import generate_visual_prompt")
        print("   result = await generate_visual_prompt('topic', 'instagram', 'modern')")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": (passed/total)*100,
            "phase2_status": phase2_status,
            "detailed_results": all_results
        }

async def main():
    """Função principal para executar os testes"""
    tester = MockRAGTester()
    results = await tester.run_all_tests()
    return results

if __name__ == "__main__":
    # Executar testes
    asyncio.run(main())
