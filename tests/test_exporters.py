"""
TESTES - Sistema de Exportação e Saídas Organizadas
=================================================

Testes completos para o módulo de exportação de conteúdo.

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - FASE 5
Data: 24/05/2025
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.exporters import ContentExporter, ContentOutput, ExportBatch

class TestContentExporter:
    """Testes para o exportador de conteúdo"""
    
    @pytest.fixture
    def temp_dir(self):
        """Diretório temporário para testes"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def exporter(self, temp_dir):
        """Exportador configurado com diretório temporário"""
        with patch('core.exporters.PROJECT_ROOT', temp_path):
            exporter = ContentExporter()
            return exporter
    
    @pytest.fixture
    def sample_crew_results(self):
        """Resultados simulados do CrewAI"""
        return {
            "final_result": """# IA no Marketing Digital

## Instagram
🚀 A IA está revolucionando o marketing digital! 

#IA #MarketingDigital #Automacao

## LinkedIn
A Inteligência Artificial está transformando fundamentalmente como fazemos marketing digital.

Principais tendências:
• Automação inteligente
• Personalização extrema
• ROI otimizado

#InteligenciaArtificial #MarketingDigital #Inovacao

## Twitter
🤖 IA no marketing 2025: automação + personalização = sucesso!

#IA #Marketing #Tech2025
""",
            "execution_time": "2.5 minutos",
            "agents_used": ["Pesquisador", "Redator", "Designer", "Editor"],
            "approved": True
        }
    
    @pytest.fixture
    def sample_research_data(self):
        """Dados de pesquisa simulados"""
        return {
            "search_results": [
                {
                    "title": "Tendências de IA 2025",
                    "summary": "Principais inovações esperadas",
                    "source": "Perplexity AI",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "keywords": ["IA", "marketing", "automação"],
            "search_timestamp": datetime.now().isoformat()
        }
    
    @pytest.fixture
    def sample_visual_prompts(self):
        """Prompts visuais simulados"""
        return [
            "Professional AI dashboard with futuristic design",
            "Abstract AI neural network visualization",
            "Marketing team with AI assistants collaboration"
        ]
    
    def test_directory_creation(self, exporter):
        """Testar criação automática de diretórios"""
        
        # Verificar se os diretórios foram criados
        assert exporter.content_dir.exists()
        assert exporter.prompts_dir.exists()
        assert exporter.analytics_dir.exists()
        assert exporter.history_dir.exists()
        
        # Verificar subdiretórios
        assert (exporter.content_dir / "by_platform").exists()
        assert (exporter.content_dir / "by_date").exists()
        assert (exporter.prompts_dir / "dall_e").exists()
        assert (exporter.analytics_dir / "daily").exists()
        assert (exporter.analytics_dir / "monthly").exists()
    
    def test_generate_ids(self, exporter):
        """Testar geração de IDs únicos"""
        
        # Testar ID de conteúdo
        content_id1 = exporter._generate_content_id("IA Marketing", "instagram")
        content_id2 = exporter._generate_content_id("IA Marketing", "linkedin")
        
        assert len(content_id1) == 8
        assert len(content_id2) == 8
        assert content_id1 != content_id2  # Diferentes plataformas
        
        # Testar ID de lote
        batch_id1 = exporter._generate_batch_id("IA Marketing")
        batch_id2 = exporter._generate_batch_id("Outro Tema")
        
        assert len(batch_id1) == 12
        assert len(batch_id2) == 12
        assert batch_id1 != batch_id2  # Diferentes temas
    
    def test_extract_platform_content(self, exporter, sample_crew_results):
        """Testar extração de conteúdo por plataforma"""
        
        # Testar extração do Instagram
        instagram_content = exporter._extract_platform_content(
            "instagram", sample_crew_results, "IA Marketing"
        )
        
        assert instagram_content is not None
        assert "IA está revolucionando" in instagram_content["content"]
        assert "#IA" in instagram_content["hashtags"]
        assert len(instagram_content["hashtags"]) <= 30  # Limite do Instagram
        
        # Testar extração do LinkedIn
        linkedin_content = exporter._extract_platform_content(
            "linkedin", sample_crew_results, "IA Marketing"
        )
        
        assert linkedin_content is not None
        assert "Inteligência Artificial" in linkedin_content["content"]
        assert "#InteligenciaArtificial" in linkedin_content["hashtags"]
        assert len(linkedin_content["hashtags"]) <= 10  # Limite do LinkedIn
    
    def test_parse_platform_section(self, exporter):
        """Testar parseamento de seção da plataforma"""
        
        section = """🚀 A IA está revolucionando o marketing!

Principais tendências:
• Automação
• Personalização

#IA #Marketing #Tecnologia #Inovacao"""
        
        result = exporter._parse_platform_section(section, "instagram")
        
        assert result["title"] == "🚀 A IA está revolucionando o marketing!"
        assert "Principais tendências" in result["content"]
        assert "#IA" in result["hashtags"]
        assert "#Marketing" in result["hashtags"]
        assert len(result["hashtags"]) <= 30  # Limite Instagram
    
    def test_create_generic_platform_content(self, exporter):
        """Testar criação de conteúdo genérico"""
        
        content = "Este é um conteúdo muito longo que precisa ser truncado porque excede o limite de caracteres da plataforma Twitter que tem apenas 280 caracteres máximos e este texto definitivamente vai ultrapassar esse limite para testar a funcionalidade de truncamento automático."
        
        result = exporter._create_generic_platform_content(
            content, "twitter", "IA Marketing"
        )
        
        assert len(result["content"]) <= 280  # Limite do Twitter
        assert result["content"].endswith("...")  # Truncado
        assert "#IA" in result["hashtags"]
        assert "#Marketing" in result["hashtags"]
        assert "#twitter" in result["hashtags"]
    
    @pytest.mark.asyncio
    async def test_export_content_batch(
        self, 
        exporter, 
        sample_crew_results, 
        sample_research_data, 
        sample_visual_prompts
    ):
        """Testar exportação completa de lote"""
        
        topic = "IA no Marketing Digital"
        
        # Executar exportação
        export_batch = await exporter.export_content_batch(
            topic=topic,
            crew_results=sample_crew_results,
            research_data=sample_research_data,
            visual_prompts=sample_visual_prompts
        )
        
        # Verificar estrutura do lote
        assert export_batch.topic == topic
        assert export_batch.batch_id is not None
        assert len(export_batch.batch_id) == 12
        assert len(export_batch.platforms) > 0
        assert len(export_batch.visual_prompts) == 3
        
        # Verificar plataformas exportadas
        platform_names = [p.platform for p in export_batch.platforms]
        expected_platforms = ["instagram", "linkedin", "twitter"]
        
        for platform in expected_platforms:
            assert platform in platform_names
        
        # Verificar metadados
        assert export_batch.export_metadata["total_platforms"] > 0
        assert export_batch.export_metadata["total_visual_prompts"] == 3
    
    @pytest.mark.asyncio
    async def test_save_platform_markdown(self, exporter):
        """Testar salvamento de arquivo Markdown"""
        
        # Criar conteúdo de teste
        content = ContentOutput(
            platform="instagram",
            title="Teste IA Marketing",
            content="Conteúdo de teste sobre IA",
            hashtags=["#IA", "#Marketing"],
            visual_prompt="Prompt visual de teste",
            created_at=datetime.now().isoformat(),
            topic="IA Marketing",
            id="test123",
            metadata={
                "word_count": 5,
                "char_count": 25,
                "hashtag_count": 2,
                "platform_config": {"max_chars": 2200}
            }
        )
        
        # Criar lote mock
        batch = ExportBatch(
            topic="IA Marketing",
            created_at=datetime.now().isoformat(),
            batch_id="batch123",
            platforms=[content],
            research_data={},
            visual_prompts=[],
            export_metadata={}
        )
        
        # Salvar arquivo
        await exporter._save_platform_markdown(content, batch)
        
        # Verificar se arquivo foi criado
        platform_dir = exporter.content_dir / "by_platform" / "instagram"
        md_files = list(platform_dir.glob("*.md"))
        
        assert len(md_files) > 0
        
        # Verificar conteúdo do arquivo
        with open(md_files[0], 'r', encoding='utf-8') as f:
            file_content = f.read()
            
        assert "# Teste IA Marketing" in file_content
        assert "**Plataforma**: Instagram" in file_content
        assert "Conteúdo de teste sobre IA" in file_content
        assert "#IA #Marketing" in file_content
        assert "Prompt visual de teste" in file_content
    
    @pytest.mark.asyncio
    async def test_save_batch_json(self, exporter):
        """Testar salvamento de lote em JSON"""
        
        # Criar lote de teste
        batch = ExportBatch(
            topic="IA Marketing",
            created_at="2025-05-24T22:00:00",
            batch_id="batch123",
            platforms=[],
            research_data={"test": "data"},
            visual_prompts=["prompt1", "prompt2"],
            export_metadata={"total_platforms": 0}
        )
        
        # Salvar JSON
        await exporter._save_batch_json(batch)
        
        # Verificar se arquivo foi criado
        date_dir = exporter.content_dir / "by_date" / "2025-05"
        json_files = list(date_dir.glob("*.json"))
        
        assert len(json_files) > 0
        
        # Verificar conteúdo do JSON
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        assert data["topic"] == "IA Marketing"
        assert data["batch_id"] == "batch123"
        assert data["research_data"]["test"] == "data"
        assert len(data["visual_prompts"]) == 2
    
    @pytest.mark.asyncio
    async def test_save_visual_prompts(self, exporter):
        """Testar salvamento de prompts visuais"""
        
        # Criar lote com prompts
        batch = ExportBatch(
            topic="IA Marketing",
            created_at=datetime.now().isoformat(),
            batch_id="batch123",
            platforms=[],
            research_data={},
            visual_prompts=[
                "Prompt DALL-E 1: AI dashboard",
                "Prompt DALL-E 2: Neural network"
            ],
            export_metadata={}
        )
        
        # Salvar prompts
        await exporter._save_visual_prompts(batch)
        
        # Verificar arquivo de prompts
        today = datetime.now().strftime("%Y-%m-%d")
        prompts_file = exporter.prompts_dir / "dall_e" / f"prompts_{today}.md"
        
        assert prompts_file.exists()
        
        # Verificar conteúdo
        with open(prompts_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        assert "## IA Marketing" in content
        assert "### Prompt 1" in content
        assert "AI dashboard" in content
        assert "Neural network" in content
    
    @pytest.mark.asyncio
    async def test_save_to_history(self, exporter):
        """Testar salvamento no histórico"""
        
        # Criar lote de teste
        batch = ExportBatch(
            topic="IA Marketing",
            created_at=datetime.now().isoformat(),
            batch_id="batch123",
            platforms=[],
            research_data={},
            visual_prompts=["prompt1"],
            export_metadata={}
        )
        
        # Salvar no histórico
        await exporter._save_to_history(batch)
        
        # Verificar arquivo de histórico
        history_file = exporter.history_dir / "export_history.json"
        assert history_file.exists()
        
        # Verificar conteúdo
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        assert len(history) > 0
        assert history[-1]["batch_id"] == "batch123"
        assert history[-1]["topic"] == "IA Marketing"
    
    @pytest.mark.asyncio
    async def test_update_analytics(self, exporter):
        """Testar atualização de analytics"""
        
        # Criar lote com conteúdo
        content1 = ContentOutput(
            platform="instagram", title="Test", content="", hashtags=[],
            visual_prompt="", created_at="", topic="", id="",
            metadata={}
        )
        content2 = ContentOutput(
            platform="linkedin", title="Test", content="", hashtags=[],
            visual_prompt="", created_at="", topic="", id="",
            metadata={}
        )
        
        batch = ExportBatch(
            topic="IA Marketing",
            created_at=datetime.now().isoformat(),
            batch_id="batch123",
            platforms=[content1, content2],
            research_data={},
            visual_prompts=[],
            export_metadata={}
        )
        
        # Atualizar analytics
        await exporter._update_analytics(batch)
        
        # Verificar analytics diária
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = exporter.analytics_dir / "daily" / f"{today}.json"
        
        assert daily_file.exists()
        
        with open(daily_file, 'r', encoding='utf-8') as f:
            daily_stats = json.load(f)
            
        assert daily_stats["total_batches"] >= 1
        assert daily_stats["total_content"] >= 2
        assert "instagram" in daily_stats["platforms_used"]
        assert "linkedin" in daily_stats["platforms_used"]
        assert "IA Marketing" in daily_stats["topics"]
    
    @pytest.mark.asyncio
    async def test_get_export_history(self, exporter):
        """Testar obtenção do histórico"""
        
        # Criar histórico simulado
        history_data = [
            {
                "batch_id": "batch1",
                "topic": "Tema 1",
                "created_at": "2025-05-24T20:00:00",
                "platforms": ["instagram", "linkedin"],
                "total_content": 2,
                "visual_prompts_count": 1
            },
            {
                "batch_id": "batch2",
                "topic": "Tema 2",
                "created_at": "2025-05-24T21:00:00",
                "platforms": ["twitter"],
                "total_content": 1,
                "visual_prompts_count": 2
            }
        ]
        
        # Salvar histórico
        history_file = exporter.history_dir / "export_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f)
        
        # Obter histórico
        history = await exporter.get_export_history(limit=5)
        
        assert len(history) == 2
        assert history[0]["batch_id"] == "batch1"
        assert history[1]["batch_id"] == "batch2"
        
        # Testar limite
        history_limited = await exporter.get_export_history(limit=1)
        assert len(history_limited) == 1
        assert history_limited[0]["batch_id"] == "batch2"  # Mais recente
    
    @pytest.mark.asyncio
    async def test_get_analytics_summary(self, exporter):
        """Testar resumo de analytics"""
        
        # Criar analytics simuladas
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        daily_stats = {
            "total_batches": 2,
            "total_content": 5,
            "platforms_used": ["instagram", "linkedin", "instagram"],
            "topics": ["IA", "Marketing"],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        monthly_stats = {
            "total_batches": 10,
            "total_content": 25,
            "platforms_used": ["instagram"] * 10 + ["linkedin"] * 8 + ["twitter"] * 7,
            "topics": ["IA"] * 5 + ["Marketing"] * 3 + ["Tech"] * 2,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Salvar analytics
        daily_file = exporter.analytics_dir / "daily" / f"{today}.json"
        monthly_file = exporter.analytics_dir / "monthly" / f"{month}.json"
        
        with open(daily_file, 'w', encoding='utf-8') as f:
            json.dump(daily_stats, f)
        
        with open(monthly_file, 'w', encoding='utf-8') as f:
            json.dump(monthly_stats, f)
        
        # Obter summary
        summary = await exporter.get_analytics_summary()
        
        # Verificar dados mensais
        assert summary["monthly"]["batches"] == 10
        assert summary["monthly"]["content_pieces"] == 25
        assert summary["monthly"]["unique_platforms"] == 3  # instagram, linkedin, twitter
        assert "instagram" in summary["monthly"]["platforms"]
        assert summary["monthly"]["topics_count"] == 3  # IA, Marketing, Tech
        
        # Verificar dados diários
        assert summary["daily"]["batches"] == 2
        assert summary["daily"]["content_pieces"] == 5
        assert summary["daily"]["unique_platforms"] == 2  # instagram, linkedin
        assert summary["daily"]["topics_count"] == 2  # IA, Marketing

async def test_full_export_workflow():
    """Teste completo do workflow de exportação"""
    
    print("\n🧪 Testando workflow completo de exportação...")
    
    # Usar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        with patch('core.exporters.PROJECT_ROOT', temp_path):
            exporter = ContentExporter()
            
            # Dados de teste
            topic = "IA no Marketing Digital"
            crew_results = {
                "final_result": """# IA no Marketing

## Instagram
🚀 IA revolucionando marketing!
#IA #Marketing

## LinkedIn
Análise completa sobre IA no marketing digital.
#InteligenciaArtificial #Marketing

## Twitter
🤖 IA + Marketing = Futuro!
#IA #Tech
""",
                "execution_time": "2 min",
                "approved": True
            }
            
            research_data = {
                "keywords": ["IA", "marketing"],
                "timestamp": datetime.now().isoformat()
            }
            
            visual_prompts = [
                "AI dashboard design",
                "Marketing automation visual"
            ]
            
            # Executar exportação
            batch = await exporter.export_content_batch(
                topic=topic,
                crew_results=crew_results,
                research_data=research_data,
                visual_prompts=visual_prompts
            )
            
            # Verificações
            assert batch is not None
            assert batch.topic == topic
            assert len(batch.platforms) >= 3  # Instagram, LinkedIn, Twitter
            assert len(batch.visual_prompts) == 2
            
            # Verificar arquivos criados
            assert (temp_path / "output" / "content" / "by_platform").exists()
            assert (temp_path / "output" / "prompts" / "dall_e").exists()
            assert (temp_path / "output" / "analytics" / "daily").exists()
            assert (temp_path / "output" / "history").exists()
            
            # Verificar analytics
            summary = await exporter.get_analytics_summary()
            assert summary["daily"]["batches"] >= 1
            assert summary["daily"]["content_pieces"] >= 3
            
            print("✅ Workflow de exportação testado com sucesso!")

if __name__ == "__main__":
    # Executar teste básico
    asyncio.run(test_full_export_workflow())
    print("\n🎉 Todos os testes passaram!")
