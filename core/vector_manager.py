import os
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
import PyPDF2
import docx
from pathlib import Path

@dataclass
class Document:
    """Document representation"""
    content: str
    metadata: Dict[str, Any]
    doc_id: str
    chunk_id: str = None

class VectorManager:
    """Vector database manager for RAG functionality"""
    
    def __init__(self, 
                 persist_directory: str = "./data/vector_store",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        
        self.logger = logging.getLogger(__name__)
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.logger.info(f"VectorManager initialized with {self.collection.count()} documents")
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load and process document from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.pdf':
                content = self._load_pdf(file_path)
            elif ext == '.txt':
                content = self._load_txt(file_path)
            elif ext in ['.docx', '.doc']:
                content = self._load_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            # Create document ID
            doc_id = self._generate_doc_id(file_path, content)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(content)
            
            documents = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                doc = Document(
                    content=chunk,
                    metadata={
                        "source": str(file_path),
                        "doc_id": doc_id,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_type": ext,
                        "file_size": file_path.stat().st_size
                    },
                    doc_id=doc_id,
                    chunk_id=chunk_id
                )
                documents.append(doc)
            
            self.logger.info(f"Loaded document {file_path.name} with {len(chunks)} chunks")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error loading document {file_path}: {e}")
            raise
    
    def _load_pdf(self, file_path: Path) -> str:
        """Load PDF content"""
        content = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        except Exception as e:
            self.logger.error(f"Error reading PDF {file_path}: {e}")
            raise
        return content.strip()
    
    def _load_txt(self, file_path: Path) -> str:
        """Load text file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _load_docx(self, file_path: Path) -> str:
        """Load DOCX content"""
        try:
            doc = docx.Document(file_path)
            content = []
            for paragraph in doc.paragraphs:
                content.append(paragraph.text)
            return "\n".join(content)
        except Exception as e:
            self.logger.error(f"Error reading DOCX {file_path}: {e}")
            raise
    
    def _generate_doc_id(self, file_path: Path, content: str) -> str:
        """Generate unique document ID"""
        file_info = f"{file_path.name}_{file_path.stat().st_size}_{len(content)}"
        return hashlib.md5(file_info.encode()).hexdigest()
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        try:
            # Check if documents already exist
            existing_ids = set(self.collection.get()["ids"])
            new_documents = [doc for doc in documents if doc.chunk_id not in existing_ids]
            
            if not new_documents:
                self.logger.info("All documents already exist in vector store")
                return True
            
            # Prepare data for ChromaDB
            texts = [doc.content for doc in new_documents]
            metadatas = [doc.metadata for doc in new_documents]
            ids = [doc.chunk_id for doc in new_documents]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Added {len(new_documents)} new document chunks to vector store")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def search(self, 
               query: str, 
               n_results: int = 5, 
               similarity_threshold: float = 0.7,
               filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=filter_metadata
            )
            
            # Process results
            search_results = []
            for i in range(len(results["ids"][0])):
                # Calculate similarity score (ChromaDB returns distances)
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= similarity_threshold:
                    search_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity,
                        "chunk_id": results["ids"][0][i]
                    })
            
            self.logger.info(f"Found {len(search_results)} relevant documents for query")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_context(self, 
                    query: str, 
                    max_context_length: int = 4000,
                    n_results: int = 10) -> Tuple[str, List[Dict]]:
        """Get relevant context for RAG"""
        search_results = self.search(query, n_results=n_results)
        
        if not search_results:
            return "", []
        
        # Build context string
        context_parts = []
        current_length = 0
        used_results = []
        
        for result in search_results:
            content = result["content"]
            content_length = len(content)
            
            if current_length + content_length <= max_context_length:
                context_parts.append(content)
                current_length += content_length
                used_results.append(result)
            else:
                break
        
        context = "\n\n".join(context_parts)
        return context, used_results
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document by ID"""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                self.logger.info(f"Deleted document {doc_id} with {len(results['ids'])} chunks")
                return True
            else:
                self.logger.warning(f"Document {doc_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in vector store"""
        try:
            results = self.collection.get()
            
            # Group by document
            documents = {}
            for i, metadata in enumerate(results["metadatas"]):
                doc_id = metadata["doc_id"]
                if doc_id not in documents:
                    documents[doc_id] = {
                        "doc_id": doc_id,
                        "source": metadata["source"],
                        "file_type": metadata["file_type"],
                        "file_size": metadata["file_size"],
                        "chunk_count": 0
                    }
                documents[doc_id]["chunk_count"] += 1
            
            return list(documents.values())
            
        except Exception as e:
            self.logger.error(f"Error listing documents: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            total_chunks = self.collection.count()
            documents = self.list_documents()
            
            return {
                "total_documents": len(documents),
                "total_chunks": total_chunks,
                "collection_name": self.collection.name,
                "embedding_model": self.embedding_model.get_sentence_embedding_dimension(),
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {}
    
    def clear_all(self) -> bool:
        """Clear all documents from vector store"""
        try:
            # Delete collection and recreate
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info("Cleared all documents from vector store")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing vector store: {e}")
            return False 