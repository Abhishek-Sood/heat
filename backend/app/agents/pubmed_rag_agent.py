from ..rag.retriever import get_rag_context
from ..core.logging import setup_logging
from ..core.config import get_settings
from groq import Groq
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("pubmed_rag_agent")
settings = get_settings()

class PubMedRAGAgent:
    """
    Handles research paper queries using PubMed RAG pipeline.
    Only activated for research/literature-related queries.
    """
    
    def __init__(self):
        self.name = "pubmed_rag"
        self.description = "Retrieves relevant PubMed research papers for medical literature queries"
        
    def can_handle(self, query: str) -> bool:
        """
        Uses LLM semantic understanding to determine if medical literature research is needed.
        No keyword matching - analyzes semantic intent for research needs.
        """
        try:
            if not settings.GROQ_API_KEY:
                # Fallback: be conservative about research needs
                return False
            
            # Semantic analysis for research literature needs
            analysis_prompt = f"""
Analyze if this medical query requires scientific literature research:

Query: "{query}"

Does this query need:
- Medical research evidence or studies
- Clinical trial data or findings
- Scientific literature or publications
- Drug mechanism or research-based information
- Evidence-based medical guidelines

Answer: YES (if research literature needed) or NO (if can be answered without research)

Response:"""

            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a medical research need analyzer. Respond only with YES or NO."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return "YES" in result
            
        except Exception as e:
            logger.error(f"LLM classification failed for PubMed RAG agent: {e}")
            # Conservative fallback - don't fetch research if unsure
            return False
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in research_keywords)
    
    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process research query and return RAG context with citations.
        
        Args:
            query: User query
            context: Additional context (patient data, etc.)
            
        Returns:
            Dict with 'rag_context', 'has_context', 'agent_used'
        """
        try:
            logger.info(f"Processing PubMed RAG query: {query[:100]}...")
            
            # Get RAG context from our pipeline
            rag_context = get_rag_context(query)
            
            if rag_context:
                logger.info("Successfully retrieved PubMed research context")
                return {
                    'rag_context': rag_context,
                    'has_context': True,
                    'agent_used': self.name,
                    'message': 'Retrieved relevant PubMed research papers'
                }
            else:
                logger.info("No relevant PubMed papers found")
                return {
                    'rag_context': '',
                    'has_context': False,
                    'agent_used': self.name,
                    'message': 'No relevant research papers found for this query'
                }
                
        except Exception as e:
            logger.error(f"Error in PubMed RAG agent: {str(e)}")
            return {
                'rag_context': '',
                'has_context': False,
                'agent_used': self.name,
                'error': str(e),
                'message': 'Error retrieving research papers'
            }