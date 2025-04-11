"""
Enhanced Financial QA module with advanced NLP capabilities.
This extends the standard FinancialQA with more sophisticated NLP techniques.
"""
import datetime
from typing import Dict, List, Tuple, Any

# Import the base FinancialQA class
from src.models.financial_qa import FinancialQA

# Import our advanced NLP module
from src.models.advanced_nlp import AdvancedNLP

class EnhancedFinancialQA(FinancialQA):
    """Enhanced Financial QA system with advanced NLP capabilities."""
    
    def __init__(self, use_transformers: bool = False):
        """
        Initialize enhanced financial QA system.
        
        Args:
            use_transformers: Whether to use Hugging Face transformers if available
        """
        # Initialize the base FinancialQA class
        super().__init__()
        
        # Initialize advanced NLP module
        self.advanced_nlp = AdvancedNLP(use_transformers=use_transformers)
        print("Enhanced Financial QA system initialized with advanced NLP capabilities")
    
    def answer_question(self, question: str) -> Tuple[str, List[str], List[Dict]]:
        """
        Answer a financial question using the LLM and context.
        
        Overrides the base method to use advanced NLP for better entity extraction
        and source relevance ranking.
        
        Args:
            question: Question to answer
            
        Returns:
            Tuple of answer, source files, and relevant sources
        """
        # Process query with advanced NLP
        query_info = self.advanced_nlp.process_query(question)
        
        # Extract entities in a format compatible with base class
        entity_matches = {
            "companies": query_info["entities"]["companies"],
            "sectors": query_info["entities"]["sectors"],
            "indices": query_info["entities"]["indices"],
            "keywords": query_info["entities"]["keywords"]
        }
        
        # Keep compatibility with base implementation
        self.current_entity_matches = entity_matches
        
        # Get context using the standard method (it uses the entity matches we just set)
        context = self._get_relevant_context(question)
        
        # Get answer from LLM
        if self.llm:
            answer = self.llm.generate_answer(question, context)
        else:
            # Fallback to simulated answer
            answer = self._get_simulated_answer(question, entity_matches)
        
        # Use advanced NLP to get more relevant sources
        relevant_sources = self.advanced_nlp.get_relevant_sources(self.news_articles, question)
        
        # Return the answer, source files, and relevant sources
        return answer, self.current_source_files, relevant_sources
    
    def _extract_entities_from_question(self, question: str) -> Dict[str, List[str]]:
        """
        Extract entities from a question using enhanced NLP techniques.
        
        Override the base method to use our advanced NLP module.
        
        Args:
            question: Question to extract entities from
            
        Returns:
            Dictionary with entity types and values
        """
        # Use advanced NLP to extract entities
        query_info = self.advanced_nlp.process_query(question)
        
        # Format the result to match the expected format
        entity_matches = {
            "companies": query_info["entities"]["companies"],
            "sectors": query_info["entities"]["sectors"],
            "indices": query_info["entities"]["indices"],
            "keywords": query_info["entities"]["keywords"]
        }
        
        # Save for reference
        self.current_entity_matches = entity_matches
        
        return entity_matches
    
    def _get_relevant_sources(self, question: str, entity_matches: Dict[str, List[str]]) -> List[Dict]:
        """
        Get relevant sources based on user query using advanced NLP matching.
        
        Override the base method to use our advanced NLP module.
        
        Args:
            question: User question
            entity_matches: Extracted entities from the question
            
        Returns:
            List of relevant sources
        """
        # Use the advanced NLP module to get relevant sources
        return self.advanced_nlp.get_relevant_sources(self.news_articles, question)


if __name__ == "__main__":
    # Example usage
    qa_system = EnhancedFinancialQA(use_transformers=False)
    
    # Example questions
    questions = [
        "Why did Jyothy Labs up today?",
        "What happened to Nifty this week?",
        "Any macro news impacting tech-focused funds?",
        "What does the last quarter say for the Swiggy?",
        "Why did TCS stock drop yesterday?",
        "Compare Reliance and TCS performance"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        answer, source_files, relevant_sources = qa_system.answer_question(question)
        print(f"Answer: {answer}")
        print(f"Source Files: {', '.join(source_files) if source_files else 'None'}")
        print(f"Relevant Sources:")
        for i, source in enumerate(relevant_sources):
            matches = ', '.join(source.get('matches', []))
            print(f"  {i+1}. {source['title']} (Score: {source.get('relevance_score', 0):.1f})")
            print(f"     Source: {source['source']} on {source['date']}")
            print(f"     Matches: {matches}")
        print("="*80) 