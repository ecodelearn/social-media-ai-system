"""
Sistema RAG (Retrieval-Augmented Generation) para prompts visuais
Processa o PDF VisualGPT e implementa busca semântica para geração de prompts DALL-E
"""
import os
import json
import pickle
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio

# Dependências para processamento de PDF e embeddings
try:
    import PyPDF2
    import fitz  # PyMuPDF
except ImportError:
    PyPDF2 = None
    fitz = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import faiss
except ImportError:
    faiss = None

from config.visual_configs import (
    visual_rag_config, 
    prompt_template_config, 
    quality_config,
    get_platform_specs,
    get_style_guidelines,
    validate_prompt_quality
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Representa um chunk de documento processado"""
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    page_number: int = 0
    chunk_id: str = ""

@dataclass
class SearchResult:
    """Resultado de uma busca no RAG"""
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    chunk_id: str
    page_number: int

@dataclass
class VisualPromptRequest:
    """Solicitação para geração de prompt visual"""
    topic: str
    platform: str
    style: str = "modern"
    format_type: str = "post"
    brand_elements: Optional[str] = None
    additional_requirements: Optional[str] = None

class VisualPromptEngine:
    """
    Engine principal do sistema RAG Visual
    Processa o PDF VisualGPT e gera prompts DALL-E baseados em busca semântica
    """
    
    def __init__(self):
        self.config = visual_rag_config
        self.embedding_model = None
        self.vector_store = None
        self.document_chunks: List[DocumentChunk] = []
        self.is_initialized = False
        
        # Caminhos de cache
        self.chunks_cache_path = os.path.join(self.config.embeddings_dir, "document_chunks.pkl")
        self.embeddings_cache_path = os.path.join(self.config.embeddings_dir, "embeddings.npy")
        self.vector_store_path = os.path.join(self.config.embeddings_dir, "vector_store.faiss")
        
    async def initialize(self) -> bool:
        """
        Inicializar o engine RAG
        
        Returns:
            True se inicializado com sucesso
        """
        try:
            logger.info("🚀 Inicializando Visual Prompt Engine...")
            
            # Verificar dependências
            if not self._check_dependencies():
                return False
            
            # Carregar modelo de embeddings
            await self._load_embedding_model()
            
            # Processar PDF se necessário
            if not self._cache_exists():
                logger.info("📄 Processando PDF VisualGPT...")
                await self._process_pdf()
            else:
                logger.info("💾 Carregando cache existente...")
                await self._load_cache()
            
            # Construir vector store
            await self._build_vector_store()
            
            self.is_initialized = True
            logger.info("✅ Visual Prompt Engine inicializado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar RAG Engine: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Verificar se todas as dependências estão instaladas"""
        missing_deps = []
        
        if PyPDF2 is None and fitz is None:
            missing_deps.append("PyPDF2 ou PyMuPDF")
        
        if SentenceTransformer is None:
            missing_deps.append("sentence-transformers")
        
        if np is None:
            missing_deps.append("numpy")
        
        if faiss is None:
            missing_deps.append("faiss-cpu")
        
        if missing_deps:
            logger.error(f"❌ Dependências não encontradas: {missing_deps}")
            logger.info("💡 Instale com: pip install PyMuPDF sentence-transformers numpy faiss-cpu")
            return False
        
        return True
    
    async def _load_embedding_model(self):
        """Carregar modelo de embeddings"""
        try:
            logger.info(f"🧠 Carregando modelo: {self.config.embedding_model}")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            logger.info("✅ Modelo de embeddings carregado!")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            raise
    
    async def _process_pdf(self):
        """Processar o PDF VisualGPT em chunks"""
        pdf_path = self.config.pdf_path
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
        
        logger.info(f"📖 Processando PDF: {pdf_path}")
        
        # Tentar diferentes métodos de extração
        text_content = None
        
        # Método 1: PyMuPDF (mais robusto)
        if fitz:
            try:
                text_content = self._extract_text_pymupdf(pdf_path)
                logger.info("✅ Texto extraído com PyMuPDF")
            except Exception as e:
                logger.warning(f"⚠️ PyMuPDF falhou: {e}")
        
        # Método 2: PyPDF2 (fallback)
        if not text_content and PyPDF2:
            try:
                text_content = self._extract_text_pypdf2(pdf_path)
                logger.info("✅ Texto extraído com PyPDF2")
            except Exception as e:
                logger.warning(f"⚠️ PyPDF2 falhou: {e}")
        
        if not text_content:
            raise Exception("Não foi possível extrair texto do PDF")
        
        # Dividir em chunks
        chunks = self._create_chunks(text_content)
        
        # Gerar embeddings
        await self._generate_embeddings(chunks)
        
        # Salvar cache
        await self._save_cache()
        
        logger.info(f"✅ PDF processado: {len(self.document_chunks)} chunks criados")
    
    def _extract_text_pymupdf(self, pdf_path: str) -> List[Tuple[str, int]]:
        """Extrair texto usando PyMuPDF"""
        doc = fitz.open(pdf_path)
        text_pages = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_pages.append((text, page_num + 1))
        
        doc.close()
        return text_pages
    
    def _extract_text_pypdf2(self, pdf_path: str) -> List[Tuple[str, int]]:
        """Extrair texto usando PyPDF2"""
        text_pages = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    text_pages.append((text, page_num + 1))
        
        return text_pages
    
    def _create_chunks(self, text_pages: List[Tuple[str, int]]) -> List[DocumentChunk]:
        """Dividir texto em chunks com overlap"""
        chunks = []
        chunk_id = 0
        
        for text, page_num in text_pages:
            # Dividir por parágrafos primeiro
            paragraphs = text.split('\n\n')
            current_chunk = ""
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # Verificar se adicionar o parágrafo excede o limite
                if len(current_chunk) + len(paragraph) > self.config.chunk_size:
                    # Salvar chunk atual se não estiver vazio
                    if current_chunk:
                        chunk = DocumentChunk(
                            content=current_chunk.strip(),
                            metadata={
                                "source": "VisualGPT_PDF",
                                "type": "visual_guideline",
                                "processed_at": "phase2_rag"
                            },
                            page_number=page_num,
                            chunk_id=f"chunk_{chunk_id}"
                        )
                        chunks.append(chunk)
                        chunk_id += 1
                    
                    # Começar novo chunk com overlap
                    if len(current_chunk) > self.config.chunk_overlap:
                        overlap = current_chunk[-self.config.chunk_overlap:]
                        current_chunk = overlap + "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    # Adicionar parágrafo ao chunk atual
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # Salvar último chunk da página
            if current_chunk:
                chunk = DocumentChunk(
                    content=current_chunk.strip(),
                    metadata={
                        "source": "VisualGPT_PDF",
                        "type": "visual_guideline",
                        "processed_at": "phase2_rag"
                    },
                    page_number=page_num,
                    chunk_id=f"chunk_{chunk_id}"
                )
                chunks.append(chunk)
                chunk_id += 1
        
        return chunks
    
    async def _generate_embeddings(self, chunks: List[DocumentChunk]):
        """Gerar embeddings para os chunks"""
        logger.info("🔢 Gerando embeddings...")
        
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32
        )
        
        # Associar embeddings aos chunks
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]
        
        self.document_chunks = chunks
        logger.info(f"✅ {len(embeddings)} embeddings gerados")
    
    async def _build_vector_store(self):
        """Construir vector store FAISS"""
        if not self.document_chunks:
            raise Exception("Nenhum chunk disponível para vector store")
        
        logger.info("🗂️ Construindo vector store...")
        
        # Extrair embeddings
        embeddings = np.array([chunk.embedding for chunk in self.document_chunks])
        
        # Criar índice FAISS
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatIP(dimension)  # Inner Product para similaridade
        
        # Normalizar embeddings para similaridade cosseno
        faiss.normalize_L2(embeddings)
        
        # Adicionar ao índice
        self.vector_store.add(embeddings)
        
        logger.info(f"✅ Vector store criado com {self.vector_store.ntotal} vetores")
    
    async def search_relevant_content(
        self, 
        query: str, 
        max_results: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Buscar conteúdo relevante no RAG
        
        Args:
            query: Consulta de busca
            max_results: Número máximo de resultados
        
        Returns:
            Lista de resultados relevantes
        """
        if not self.is_initialized:
            raise Exception("Engine não inicializado. Chame initialize() primeiro.")
        
        max_results = max_results or self.config.max_results
        
        # Gerar embedding da consulta
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Buscar no vector store
        similarities, indices = self.vector_store.search(query_embedding, max_results)
        
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if similarity >= self.config.similarity_threshold:
                chunk = self.document_chunks[idx]
                result = SearchResult(
                    content=chunk.content,
                    metadata=chunk.metadata,
                    similarity_score=float(similarity),
                    chunk_id=chunk.chunk_id,
                    page_number=chunk.page_number
                )
                results.append(result)
        
        logger.info(f"🔍 Busca por '{query}': {len(results)} resultados encontrados")
        return results
    
    async def generate_visual_prompt(
        self, 
        request: VisualPromptRequest
    ) -> Dict[str, Any]:
        """
        Gerar prompt visual profissional baseado em RAG
        
        Args:
            request: Solicitação de prompt visual
        
        Returns:
            Dicionário com prompt e metadados
        """
        if not self.is_initialized:
            raise Exception("Engine não inicializado. Chame initialize() primeiro.")
        
        logger.info(f"🎨 Gerando prompt visual para: {request.topic}")
        
        # Buscar conteúdo relevante
        search_query = f"{request.topic} {request.style} visual design"
        relevant_content = await self.search_relevant_content(search_query)
        
        # Obter especificações da plataforma
        platform_specs = get_platform_specs(request.platform, request.format_type)
        
        # Obter diretrizes de estilo
        style_guidelines = get_style_guidelines(request.style)
        
        # Compilar informações visuais do RAG
        visual_techniques = self._extract_visual_techniques(relevant_content)
        
        # Gerar prompt usando template
        prompt = self._build_prompt_from_template(
            request, platform_specs, style_guidelines, visual_techniques
        )
        
        # Validar qualidade
        quality_scores = validate_prompt_quality(prompt)
        
        result = {
            "prompt": prompt,
            "platform_specs": platform_specs,
            "style_guidelines": style_guidelines,
            "rag_sources": len(relevant_content),
            "quality_scores": quality_scores,
            "visual_techniques": visual_techniques,
            "metadata": {
                "topic": request.topic,
                "platform": request.platform,
                "style": request.style,
                "format_type": request.format_type,
                "generated_at": "phase2_rag_engine"
            }
        }
        
        logger.info(f"✅ Prompt gerado (qualidade: {quality_scores['overall']:.2f})")
        return result
    
    def _extract_visual_techniques(self, search_results: List[SearchResult]) -> List[str]:
        """Extrair técnicas visuais do conteúdo encontrado"""
        techniques = []
        
        # Palavras-chave para identificar técnicas visuais
        visual_keywords = [
            "composition", "lighting", "color palette", "contrast",
            "depth", "perspective", "balance", "symmetry", "focal point",
            "texture", "pattern", "gradient", "shadow", "highlight"
        ]
        
        for result in search_results:
            content_lower = result.content.lower()
            for keyword in visual_keywords:
                if keyword in content_lower:
                    # Extrair sentença com a técnica
                    sentences = result.content.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            techniques.append(sentence.strip())
                            break
        
        return list(set(techniques))  # Remover duplicatas
    
    def _build_prompt_from_template(
        self,
        request: VisualPromptRequest,
        platform_specs: Dict[str, str],
        style_guidelines: str,
        visual_techniques: List[str]
    ) -> str:
        """Construir prompt usando template e informações do RAG"""
        
        # Compilar requisitos visuais
        visual_requirements = []
        visual_requirements.append(f"Style: {style_guidelines}")
        
        if visual_techniques:
            visual_requirements.append("Visual techniques from expert knowledge:")
            visual_requirements.extend(visual_techniques[:3])  # Top 3 técnicas
        
        # Compilar diretrizes de conteúdo
        content_guidelines = []
        platform_template = prompt_template_config.platform_templates.get(request.platform, "")
        if platform_template:
            content_guidelines.append(platform_template)
        
        if request.additional_requirements:
            content_guidelines.append(f"Additional: {request.additional_requirements}")
        
        # Elementos de marca
        brand_elements = request.brand_elements or "Professional branding consistent with content"
        
        # Construir prompt final
        prompt = prompt_template_config.base_template.format(
            style=request.style,
            platform=request.platform,
            topic=request.topic,
            visual_requirements="\n".join(visual_requirements),
            aspect_ratio=platform_specs["aspect_ratio"],
            resolution=platform_specs["resolution"],
            detailed_style=style_guidelines,
            content_guidelines="\n".join(content_guidelines),
            brand_elements=brand_elements
        )
        
        return prompt.strip()
    
    def _cache_exists(self) -> bool:
        """Verificar se cache existe"""
        return (
            os.path.exists(self.chunks_cache_path) and
            os.path.exists(self.embeddings_cache_path)
        )
    
    async def _save_cache(self):
        """Salvar chunks e embeddings em cache"""
        logger.info("💾 Salvando cache...")
        
        # Salvar chunks
        with open(self.chunks_cache_path, 'wb') as f:
            pickle.dump(self.document_chunks, f)
        
        # Salvar embeddings separadamente
        embeddings = np.array([chunk.embedding for chunk in self.document_chunks])
        np.save(self.embeddings_cache_path, embeddings)
        
        logger.info("✅ Cache salvo!")
    
    async def _load_cache(self):
        """Carregar chunks e embeddings do cache"""
        logger.info("📂 Carregando cache...")
        
        # Carregar chunks
        with open(self.chunks_cache_path, 'rb') as f:
            self.document_chunks = pickle.load(f)
        
        # Carregar embeddings
        embeddings = np.load(self.embeddings_cache_path)
        
        # Associar embeddings aos chunks
        for i, chunk in enumerate(self.document_chunks):
            chunk.embedding = embeddings[i]
        
        logger.info(f"✅ Cache carregado: {len(self.document_chunks)} chunks")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas do engine"""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "total_chunks": len(self.document_chunks),
            "embedding_dimension": self.config.embedding_dimension,
            "vector_store_size": self.vector_store.ntotal if self.vector_store else 0,
            "cache_exists": self._cache_exists(),
            "supported_platforms": list(prompt_template_config.platform_specs.keys()),
            "available_styles": prompt_template_config.visual_styles
        }

# Instância global do engine
visual_engine = VisualPromptEngine()

async def initialize_visual_engine() -> bool:
    """Função de conveniência para inicializar o engine"""
    return await visual_engine.initialize()

async def generate_visual_prompt(
    topic: str,
    platform: str,
    style: str = "modern",
    format_type: str = "post",
    brand_elements: Optional[str] = None,
    additional_requirements: Optional[str] = None
) -> Dict[str, Any]:
    """
    Função de conveniência para gerar prompt visual
    
    Args:
        topic: Tópico do conteúdo
        platform: Plataforma (instagram, linkedin, whatsapp)
        style: Estilo visual
        format_type: Tipo de formato (post, story, etc.)
        brand_elements: Elementos de marca
        additional_requirements: Requisitos adicionais
    
    Returns:
        Dicionário com prompt e metadados
    """
    request = VisualPromptRequest(
        topic=topic,
        platform=platform,
        style=style,
        format_type=format_type,
        brand_elements=brand_elements,
        additional_requirements=additional_requirements
    )
    
    return await visual_engine.generate_visual_prompt(request)

if __name__ == "__main__":
    # Teste básico do engine
    async def test_engine():
        print("🧪 Testando Visual Prompt Engine...")
        
        # Inicializar
        success = await initialize_visual_engine()
        if not success:
            print("❌ Falha na inicialização")
            return
        
        # Testar geração de prompt
        result = await generate_visual_prompt(
            topic="Marketing Digital para Pequenas Empresas",
            platform="instagram",
            style="modern",
            format_type="post"
        )
        
        print("✅ Prompt gerado:")
        print(f"Qualidade: {result['quality_scores']['overall']:.2f}")
        print(f"Fontes RAG: {result['rag_sources']}")
        print(f"Prompt: {result['prompt'][:200]}...")
        
        # Estatísticas
        stats = visual_engine.get_statistics()
        print(f"\n📊 Estatísticas: {stats}")
    
    # Executar teste
    asyncio.run(test_engine())
