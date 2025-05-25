"""
Configurações específicas para o sistema de RAG Visual
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class VisualRAGConfig:
    """Configurações do sistema RAG Visual"""
    
    # Configurações do PDF
    pdf_path: str = "data/VISUAL GPT.pdf"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Configurações de Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embeddings_dir: str = "data/embeddings"
    
    # Configurações do Vector Store
    vector_store_type: str = "faiss"  # ou "chroma"
    similarity_threshold: float = 0.7
    max_results: int = 5
    
    # Configurações de busca
    search_strategy: str = "semantic"  # semantic, keyword, hybrid
    rerank_results: bool = True
    
    def __post_init__(self):
        """Criar diretórios necessários"""
        os.makedirs(self.embeddings_dir, exist_ok=True)


@dataclass
class PromptTemplateConfig:
    """Templates para geração de prompts visuais"""
    
    # Template base para prompts DALL-E
    base_template: str = """
    Create a professional {style} image for {platform} social media post about {topic}.
    
    Visual Requirements:
    {visual_requirements}
    
    Technical Specifications:
    - Aspect ratio: {aspect_ratio}
    - Resolution: {resolution}
    - Style: {detailed_style}
    
    Content Guidelines:
    {content_guidelines}
    
    Brand Elements:
    {brand_elements}
    """
    
    # Templates específicos por plataforma
    platform_templates: Dict[str, str] = None
    
    # Estilos visuais disponíveis
    visual_styles: List[str] = None
    
    # Aspectos e resoluções por plataforma
    platform_specs: Dict[str, Dict[str, str]] = None
    
    def __post_init__(self):
        if self.platform_templates is None:
            self.platform_templates = {
                "instagram": """
                Instagram-optimized visual with:
                - High contrast and vibrant colors
                - Clear focal point
                - Mobile-first composition
                - Story-friendly vertical format
                """,
                
                "linkedin": """
                LinkedIn professional visual with:
                - Clean, corporate aesthetic
                - Professional color palette
                - Business-focused imagery
                - Horizontal layout preferred
                """,
                
                "whatsapp": """
                WhatsApp-friendly visual with:
                - Clear and readable on mobile
                - Engaging but not overwhelming
                - Square format works best
                - Quick visual understanding
                """
            }
        
        if self.visual_styles is None:
            self.visual_styles = [
                "minimalist",
                "modern",
                "corporate",
                "creative",
                "artistic",
                "photography",
                "illustration",
                "infographic",
                "flat_design",
                "3d_render"
            ]
        
        if self.platform_specs is None:
            self.platform_specs = {
                "instagram": {
                    "post": "1:1 (1080x1080)",
                    "story": "9:16 (1080x1920)",
                    "reel": "9:16 (1080x1920)",
                    "carousel": "1:1 (1080x1080)"
                },
                "linkedin": {
                    "post": "1.91:1 (1200x628)",
                    "article": "16:9 (1280x720)",
                    "story": "9:16 (1080x1920)"
                },
                "whatsapp": {
                    "status": "9:16 (1080x1920)",
                    "message": "1:1 (1080x1080)",
                    "group": "1:1 (1080x1080)"
                }
            }


@dataclass
class QualityConfig:
    """Configurações para controle de qualidade dos prompts"""
    
    # Critérios de qualidade
    min_prompt_length: int = 50
    max_prompt_length: int = 500
    required_elements: List[str] = None
    
    # Filtros de conteúdo
    forbidden_words: List[str] = None
    professional_keywords: List[str] = None
    
    # Scores de qualidade
    min_quality_score: float = 0.8
    creativity_weight: float = 0.3
    clarity_weight: float = 0.4
    relevance_weight: float = 0.3
    
    def __post_init__(self):
        if self.required_elements is None:
            self.required_elements = [
                "style description",
                "color palette",
                "composition",
                "lighting",
                "mood/atmosphere"
            ]
        
        if self.forbidden_words is None:
            self.forbidden_words = [
                "explicit",
                "violent",
                "inappropriate",
                "controversial"
            ]
        
        if self.professional_keywords is None:
            self.professional_keywords = [
                "professional",
                "clean",
                "modern",
                "sophisticated",
                "elegant",
                "minimalist",
                "corporate",
                "high-quality"
            ]


# Instâncias globais das configurações
visual_rag_config = VisualRAGConfig()
prompt_template_config = PromptTemplateConfig()
quality_config = QualityConfig()


def get_platform_specs(platform: str, format_type: str = "post") -> Dict[str, str]:
    """
    Obter especificações técnicas para uma plataforma específica
    
    Args:
        platform: Nome da plataforma (instagram, linkedin, whatsapp)
        format_type: Tipo de formato (post, story, etc.)
    
    Returns:
        Dicionário com especificações técnicas
    """
    specs = prompt_template_config.platform_specs.get(platform, {})
    aspect_ratio = specs.get(format_type, "1:1 (1080x1080)")
    
    return {
        "aspect_ratio": aspect_ratio,
        "resolution": aspect_ratio.split("(")[1].split(")")[0] if "(" in aspect_ratio else "1080x1080",
        "platform": platform.title(),
        "format": format_type.title()
    }


def get_style_guidelines(style: str) -> str:
    """
    Obter diretrizes detalhadas para um estilo visual específico
    
    Args:
        style: Nome do estilo visual
    
    Returns:
        String com diretrizes detalhadas
    """
    style_guidelines = {
        "minimalist": "Clean lines, plenty of white space, limited color palette, simple typography, focus on essential elements only",
        "modern": "Contemporary design elements, bold colors, geometric shapes, clean typography, current trends",
        "corporate": "Professional appearance, conservative colors, clean layout, trustworthy design elements, business-appropriate",
        "creative": "Artistic expression, unique composition, experimental colors, innovative design elements, eye-catching",
        "artistic": "Creative interpretation, painterly effects, artistic techniques, expressive colors, unique perspective",
        "photography": "Realistic photographic style, natural lighting, authentic moments, high-quality imagery, professional photography",
        "illustration": "Hand-drawn or digital illustration style, artistic interpretation, creative visual storytelling",
        "infographic": "Data visualization, clear information hierarchy, educational design, easy-to-understand graphics",
        "flat_design": "Flat colors, simple shapes, no gradients or shadows, clean and simple aesthetic",
        "3d_render": "Three-dimensional rendered imagery, depth and perspective, realistic materials and lighting"
    }
    
    return style_guidelines.get(style, "Professional and visually appealing design")


def validate_prompt_quality(prompt: str) -> Dict[str, float]:
    """
    Validar a qualidade de um prompt gerado
    
    Args:
        prompt: Prompt a ser validado
    
    Returns:
        Dicionário com scores de qualidade
    """
    # Calcular scores básicos
    length_score = 1.0 if quality_config.min_prompt_length <= len(prompt) <= quality_config.max_prompt_length else 0.5
    
    # Verificar elementos obrigatórios
    elements_found = sum(1 for element in quality_config.required_elements if element.lower() in prompt.lower())
    elements_score = elements_found / len(quality_config.required_elements)
    
    # Verificar palavras profissionais
    professional_words = sum(1 for word in quality_config.professional_keywords if word.lower() in prompt.lower())
    professional_score = min(professional_words / 3, 1.0)  # Normalizar para max 1.0
    
    # Verificar palavras proibidas
    forbidden_found = sum(1 for word in quality_config.forbidden_words if word.lower() in prompt.lower())
    forbidden_penalty = forbidden_found * 0.2  # Penalidade por palavra proibida
    
    # Score final
    final_score = (
        length_score * 0.2 +
        elements_score * 0.4 +
        professional_score * 0.4 -
        forbidden_penalty
    )
    
    return {
        "overall": max(0, min(1, final_score)),
        "length": length_score,
        "elements": elements_score,
        "professional": professional_score,
        "forbidden_penalty": forbidden_penalty
    }


if __name__ == "__main__":
    # Teste das configurações
    print("🎨 Configurações Visuais Carregadas!")
    print(f"📁 Embeddings: {visual_rag_config.embeddings_dir}")
    print(f"🔍 Modelo: {visual_rag_config.embedding_model}")
    print(f"📱 Plataformas: {list(prompt_template_config.platform_specs.keys())}")
    print(f"🎭 Estilos: {prompt_template_config.visual_styles}")
    
    # Teste de especificações
    specs = get_platform_specs("instagram", "post")
    print(f"📸 Instagram Post: {specs}")
    
    # Teste de diretrizes de estilo
    guidelines = get_style_guidelines("minimalist")
    print(f"✨ Minimalist: {guidelines}")
