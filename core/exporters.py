"""
EXPORTERS - Sistema de Exportação e Saídas Organizadas
=====================================================

Módulo responsável por organizar e exportar todo o conteúdo gerado
pelo sistema em formatos estruturados e profissionais.

Autor: Sistema de IA Colaborativo
Versão: 1.0.0 - FASE 5
Data: 24/05/2025
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import hashlib

from config.settings import SystemSettings

@dataclass
class ContentOutput:
    """Estrutura padronizada para conteúdo exportado"""
    platform: str
    title: str
    content: str
    hashtags: List[str]
    visual_prompt: str
    created_at: str
    topic: str
    id: str
    metadata: Dict[str, Any]

@dataclass
class ExportBatch:
    """Lote de exportação com múltiplas plataformas"""
    topic: str
    created_at: str
    batch_id: str
    platforms: List[ContentOutput]
    research_data: Dict[str, Any]
    visual_prompts: List[str]
    export_metadata: Dict[str, Any]

class ContentExporter:
    """
    Exportador principal de conteúdo gerado pelos agentes
    
    Responsabilidades:
    - Organizar conteúdo por plataforma
    - Gerar arquivos MD estruturados
    - Salvar prompts visuais
    - Criar histórico consultável
    - Gerar analytics básicas
    """
    
    def __init__(self):
        self.output_dir = SystemSettings.PROJECT_ROOT / "output"
        self.content_dir = self.output_dir / "content"
        self.prompts_dir = self.output_dir / "prompts"
        self.analytics_dir = self.output_dir / "analytics"
        self.history_dir = self.output_dir / "history"
        
        # Criar diretórios necessários
        self._ensure_directories()
        
        # Configurações de plataformas
        self.platform_configs = {
            "instagram": {
                "max_chars": 2200,
                "hashtag_limit": 30,
                "format": "visual_first"
            },
            "linkedin": {
                "max_chars": 3000,
                "hashtag_limit": 10,
                "format": "professional"
            },
            "twitter": {
                "max_chars": 280,
                "hashtag_limit": 5,
                "format": "concise"
            },
            "facebook": {
                "max_chars": 63206,
                "hashtag_limit": 20,
                "format": "storytelling"
            },
            "youtube": {
                "max_chars": 5000,
                "hashtag_limit": 15,
                "format": "descriptive"
            }
        }
    
    def _ensure_directories(self):
        """Criar estrutura de diretórios necessária"""
        directories = [
            self.content_dir,
            self.prompts_dir,
            self.analytics_dir,
            self.history_dir,
            self.content_dir / "by_platform",
            self.content_dir / "by_date",
            self.content_dir / "by_topic",
            self.prompts_dir / "dall_e",
            self.prompts_dir / "midjourney",
            self.analytics_dir / "daily",
            self.analytics_dir / "monthly"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _generate_content_id(self, topic: str, platform: str) -> str:
        """Gerar ID único para o conteúdo"""
        timestamp = datetime.now().isoformat()
        content_string = f"{topic}_{platform}_{timestamp}"
        return hashlib.md5(content_string.encode()).hexdigest()[:8]
    
    def _generate_batch_id(self, topic: str) -> str:
        """Gerar ID único para o lote de exportação"""
        timestamp = datetime.now().isoformat()
        batch_string = f"batch_{topic}_{timestamp}"
        return hashlib.md5(batch_string.encode()).hexdigest()[:12]
    
    async def export_content_batch(
        self, 
        topic: str,
        crew_results: Dict[str, Any],
        research_data: Dict[str, Any],
        visual_prompts: List[str]
    ) -> ExportBatch:
        """
        Exportar lote completo de conteúdo gerado pelos agentes
        
        Args:
            topic: Tópico do conteúdo
            crew_results: Resultados dos agentes CrewAI
            research_data: Dados da pesquisa
            visual_prompts: Lista de prompts visuais
            
        Returns:
            ExportBatch: Lote exportado com todas as informações
        """
        
        batch_id = self._generate_batch_id(topic)
        created_at = datetime.now().isoformat()
        
        # Extrair conteúdo por plataforma
        platforms_content = []
        
        for platform in self.platform_configs.keys():
            # Buscar conteúdo específico da plataforma nos resultados
            platform_content = self._extract_platform_content(
                platform, crew_results, topic
            )
            
            if platform_content:
                content_output = ContentOutput(
                    platform=platform,
                    title=platform_content.get("title", f"Conteúdo para {platform.title()}"),
                    content=platform_content.get("content", ""),
                    hashtags=platform_content.get("hashtags", []),
                    visual_prompt=platform_content.get("visual_prompt", ""),
                    created_at=created_at,
                    topic=topic,
                    id=self._generate_content_id(topic, platform),
                    metadata={
                        "word_count": len(platform_content.get("content", "").split()),
                        "char_count": len(platform_content.get("content", "")),
                        "hashtag_count": len(platform_content.get("hashtags", [])),
                        "platform_config": self.platform_configs[platform]
                    }
                )
                platforms_content.append(content_output)
        
        # Criar lote de exportação
        export_batch = ExportBatch(
            topic=topic,
            created_at=created_at,
            batch_id=batch_id,
            platforms=platforms_content,
            research_data=research_data,
            visual_prompts=visual_prompts,
            export_metadata={
                "total_platforms": len(platforms_content),
                "total_visual_prompts": len(visual_prompts),
                "export_timestamp": created_at,
                "crew_execution_time": crew_results.get("execution_time", "N/A")
            }
        )
        
        # Salvar lote
        await self._save_export_batch(export_batch)
        
        # Atualizar analytics
        await self._update_analytics(export_batch)
        
        return export_batch
    
    def _extract_platform_content(
        self, 
        platform: str, 
        crew_results: Dict[str, Any], 
        topic: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extrair conteúdo específico da plataforma dos resultados do crew
        
        Args:
            platform: Nome da plataforma
            crew_results: Resultados do CrewAI
            topic: Tópico do conteúdo
            
        Returns:
            Dict com conteúdo da plataforma ou None
        """
        
        # Buscar no resultado final
        final_result = crew_results.get("final_result", "")
        
        # Tentar extrair seção específica da plataforma
        platform_markers = {
            "instagram": ["## Instagram", "**Instagram**", "### Instagram"],
            "linkedin": ["## LinkedIn", "**LinkedIn**", "### LinkedIn"],
            "twitter": ["## Twitter", "**Twitter**", "### Twitter"],
            "facebook": ["## Facebook", "**Facebook**", "### Facebook"],
            "youtube": ["## YouTube", "**YouTube**", "### YouTube"]
        }
        
        markers = platform_markers.get(platform, [])
        
        for marker in markers:
            if marker in final_result:
                # Extrair seção da plataforma
                platform_section = self._extract_section_after_marker(
                    final_result, marker
                )
                
                if platform_section:
                    return self._parse_platform_section(platform_section, platform)
        
        # Se não encontrou seção específica, criar conteúdo genérico
        return self._create_generic_platform_content(final_result, platform, topic)
    
    def _extract_section_after_marker(self, text: str, marker: str) -> str:
        """Extrair seção do texto após um marcador"""
        lines = text.split('\n')
        start_idx = -1
        
        for i, line in enumerate(lines):
            if marker in line:
                start_idx = i + 1
                break
        
        if start_idx == -1:
            return ""
        
        # Encontrar próximo marcador de seção ou fim
        end_idx = len(lines)
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if line.startswith('##') or line.startswith('**') and line.endswith('**'):
                end_idx = i
                break
        
        return '\n'.join(lines[start_idx:end_idx]).strip()
    
    def _parse_platform_section(self, section: str, platform: str) -> Dict[str, Any]:
        """Parsear seção da plataforma extraída"""
        
        # Extrair hashtags
        hashtags = []
        hashtag_lines = [line for line in section.split('\n') if '#' in line]
        for line in hashtag_lines:
            tags = [tag.strip() for tag in line.split() if tag.startswith('#')]
            hashtags.extend(tags)
        
        # Remover hashtags do conteúdo principal
        content_lines = []
        for line in section.split('\n'):
            if not (line.strip().startswith('#') and len(line.strip().split()) > 3):
                content_lines.append(line)
        
        content = '\n'.join(content_lines).strip()
        
        # Extrair título (primeira linha não vazia)
        title = ""
        for line in content.split('\n'):
            if line.strip():
                title = line.strip()
                break
        
        return {
            "title": title,
            "content": content,
            "hashtags": hashtags[:self.platform_configs[platform]["hashtag_limit"]],
            "visual_prompt": f"Criar imagem profissional para {platform} sobre: {title}"
        }
    
    def _create_generic_platform_content(
        self, 
        content: str, 
        platform: str, 
        topic: str
    ) -> Dict[str, Any]:
        """Criar conteúdo genérico adaptado para a plataforma"""
        
        config = self.platform_configs[platform]
        
        # Adaptar tamanho do conteúdo
        if len(content) > config["max_chars"]:
            content = content[:config["max_chars"]-10] + "..."
        
        # Gerar hashtags básicas
        topic_words = topic.lower().split()
        hashtags = [f"#{word}" for word in topic_words[:3]]
        hashtags.append(f"#{platform}")
        hashtags.append("#IA")
        
        return {
            "title": f"Conteúdo sobre {topic}",
            "content": content,
            "hashtags": hashtags[:config["hashtag_limit"]],
            "visual_prompt": f"Criar imagem profissional para {platform} sobre {topic}"
        }
    
    async def _save_export_batch(self, batch: ExportBatch):
        """Salvar lote de exportação em múltiplos formatos"""
        
        # 1. Salvar por plataforma
        for platform_content in batch.platforms:
            await self._save_platform_markdown(platform_content, batch)
        
        # 2. Salvar lote completo
        await self._save_batch_json(batch)
        
        # 3. Salvar prompts visuais
        await self._save_visual_prompts(batch)
        
        # 4. Adicionar ao histórico
        await self._save_to_history(batch)
    
    async def _save_platform_markdown(self, content: ContentOutput, batch: ExportBatch):
        """Salvar conteúdo da plataforma em formato Markdown"""
        
        # Arquivo por plataforma
        platform_dir = self.content_dir / "by_platform" / content.platform
        platform_dir.mkdir(exist_ok=True)
        
        filename = f"{content.id}_{content.platform}_{batch.created_at[:10]}.md"
        filepath = platform_dir / filename
        
        # Gerar conteúdo Markdown
        md_content = f"""# {content.title}

**Plataforma**: {content.platform.title()}  
**Tópico**: {content.topic}  
**Data**: {content.created_at[:19]}  
**ID**: {content.id}  

## Conteúdo

{content.content}

## Hashtags

{' '.join(content.hashtags)}

## Prompt Visual

{content.visual_prompt}

## Metadados

- **Palavras**: {content.metadata['word_count']}
- **Caracteres**: {content.metadata['char_count']}
- **Hashtags**: {content.metadata['hashtag_count']}
- **Limite da plataforma**: {content.metadata['platform_config']['max_chars']} caracteres

---

*Gerado automaticamente pelo Social Media AI System - FASE 5*
"""
        
        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    async def _save_batch_json(self, batch: ExportBatch):
        """Salvar lote completo em formato JSON"""
        
        # Arquivo por data
        date_dir = self.content_dir / "by_date" / batch.created_at[:7]  # YYYY-MM
        date_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"batch_{batch.batch_id}_{batch.created_at[:10]}.json"
        filepath = date_dir / filename
        
        # Converter para JSON
        batch_dict = asdict(batch)
        
        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(batch_dict, f, indent=2, ensure_ascii=False)
    
    async def _save_visual_prompts(self, batch: ExportBatch):
        """Salvar prompts visuais organizados"""
        
        # Arquivo DALL-E
        dalle_dir = self.prompts_dir / "dall_e"
        dalle_file = dalle_dir / f"prompts_{batch.created_at[:10]}.md"
        
        with open(dalle_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## {batch.topic} - {batch.created_at[:19]}\n\n")
            
            for i, prompt in enumerate(batch.visual_prompts, 1):
                f.write(f"### Prompt {i}\n")
                f.write(f"```\n{prompt}\n```\n\n")
            
            # Prompts específicos por plataforma
            for platform_content in batch.platforms:
                f.write(f"### {platform_content.platform.title()}\n")
                f.write(f"```\n{platform_content.visual_prompt}\n```\n\n")
            
            f.write("---\n\n")
    
    async def _save_to_history(self, batch: ExportBatch):
        """Adicionar lote ao histórico consultável"""
        
        history_file = self.history_dir / "export_history.json"
        
        # Carregar histórico existente
        history = []
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # Adicionar novo lote (resumido)
        history_entry = {
            "batch_id": batch.batch_id,
            "topic": batch.topic,
            "created_at": batch.created_at,
            "platforms": [p.platform for p in batch.platforms],
            "total_content": len(batch.platforms),
            "visual_prompts_count": len(batch.visual_prompts)
        }
        
        history.append(history_entry)
        
        # Manter apenas os últimos 1000 registros
        if len(history) > 1000:
            history = history[-1000:]
        
        # Salvar histórico atualizado
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    async def _update_analytics(self, batch: ExportBatch):
        """Atualizar analytics do sistema"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        # Analytics diária
        daily_file = self.analytics_dir / "daily" / f"{today}.json"
        daily_stats = self._load_analytics(daily_file)
        
        daily_stats["total_batches"] += 1
        daily_stats["total_content"] += len(batch.platforms)
        daily_stats["platforms_used"].extend([p.platform for p in batch.platforms])
        daily_stats["topics"].append(batch.topic)
        daily_stats["last_updated"] = datetime.now().isoformat()
        
        self._save_analytics(daily_file, daily_stats)
        
        # Analytics mensal
        monthly_file = self.analytics_dir / "monthly" / f"{month}.json"
        monthly_stats = self._load_analytics(monthly_file)
        
        monthly_stats["total_batches"] += 1
        monthly_stats["total_content"] += len(batch.platforms)
        monthly_stats["platforms_used"].extend([p.platform for p in batch.platforms])
        monthly_stats["topics"].append(batch.topic)
        monthly_stats["last_updated"] = datetime.now().isoformat()
        
        self._save_analytics(monthly_file, monthly_stats)
    
    def _load_analytics(self, filepath: Path) -> Dict[str, Any]:
        """Carregar analytics existentes ou criar novo"""
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "total_batches": 0,
            "total_content": 0,
            "platforms_used": [],
            "topics": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_analytics(self, filepath: Path, stats: Dict[str, Any]):
        """Salvar analytics atualizadas"""
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    
    async def get_export_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obter histórico de exportações"""
        
        history_file = self.history_dir / "export_history.json"
        
        if not history_file.exists():
            return []
        
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        return history[-limit:]
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Obter resumo das analytics"""
        
        # Analytics do mês atual
        month = datetime.now().strftime("%Y-%m")
        monthly_file = self.analytics_dir / "monthly" / f"{month}.json"
        monthly_stats = self._load_analytics(monthly_file)
        
        # Analytics do dia atual
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = self.analytics_dir / "daily" / f"{today}.json"
        daily_stats = self._load_analytics(daily_file)
        
        # Contar plataformas únicas
        monthly_platforms = list(set(monthly_stats["platforms_used"]))
        daily_platforms = list(set(daily_stats["platforms_used"]))
        
        return {
            "monthly": {
                "batches": monthly_stats["total_batches"],
                "content_pieces": monthly_stats["total_content"],
                "unique_platforms": len(monthly_platforms),
                "platforms": monthly_platforms,
                "topics_count": len(set(monthly_stats["topics"]))
            },
            "daily": {
                "batches": daily_stats["total_batches"],
                "content_pieces": daily_stats["total_content"],
                "unique_platforms": len(daily_platforms),
                "platforms": daily_platforms,
                "topics_count": len(set(daily_stats["topics"]))
            }
        }

# Instância global do exportador
content_exporter = ContentExporter()
