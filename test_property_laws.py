#!/usr/bin/env python3
"""
Test script to verify that all legal questions are properly recognized and answered.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import createMultiQueryChain, kb_retriever, generateRRF, generateResponse, MultiQuery, llm

def test_legal_questions_recognition():
    """Test that all legal questions are properly recognized and answered."""
    
    print("🧪 Testing Comprehensive Legal Questions Recognition")
    print("=" * 60)
    
    # Comprehensive test cases covering various legal topics
    test_queries = [
        # Property and Real Estate Law
        "Explain property laws",
        "What are property laws?",
        "How do property laws work?",
        "Tell me about real estate laws",
        
        # Criminal Law
        "What is the Indian Penal Code?",
        "What are the penalties for theft?",
        "Explain criminal law",
        "How does criminal procedure work?",
        
        # Constitutional Law
        "Explain fundamental rights",
        "What are constitutional rights?",
        "Tell me about the constitution",
        "How do fundamental rights work?",
        
        # Contract Law
        "How does contract law work?",
        "What is contract law?",
        "Explain contract formation",
        "Tell me about contract enforcement",
        
        # Family Law
        "Tell me about inheritance laws",
        "What are family laws?",
        "Explain marriage laws",
        "How do divorce laws work?",
        
        # Civil Law
        "What is civil law?",
        "Explain civil procedure",
        "How do civil cases work?",
        "Tell me about tort law",
        
        # Commercial Law
        "What is commercial law?",
        "Explain business laws",
        "How do corporate laws work?",
        "Tell me about trade laws",
        
        # Tax Law
        "What are tax laws?",
        "Explain income tax",
        "How does GST work?",
        "Tell me about tax procedures",
        
        # Labor Law
        "What are labor laws?",
        "Explain employment law",
        "How do worker rights work?",
        "Tell me about labor regulations",
        
        # General Legal Questions
        "What is legal advice?",
        "How do I file a case?",
        "What are my legal rights?",
        "Tell me about legal procedures",
        "What is the law about...",
        "How do laws work?",
        "What does the law say about...",
        "Can you explain legal concepts?",
        "What is legal terminology?",
        "How do legal systems work?"
    ]
    
    multi_query_chain = createMultiQueryChain(MultiQuery, llm)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        # Test multi-query generation
        multi_query_resp = multi_query_chain.invoke({
            "user_query": query, 
            "chat_history": []
        })
        
        print(f"Document retrieval required: {multi_query_resp.get('documentRetrievalRequired', False)}")
        print(f"Generated queries: {multi_query_resp.get('generatedQueries', [])}")
        
        # Test response generation
        if multi_query_resp.get('documentRetrievalRequired', False):
            queries = multi_query_resp.get('generatedQueries', [])
            
            # Retrieve documents
            all_retrieved_docs = []
            for q in queries:
                docs = kb_retriever.invoke(q)
                print(f"Retrieved {len(docs)} documents for: {q}")
                all_retrieved_docs.append(docs)
            
            # Rank documents
            ranked_documents = generateRRF(all_retrieved_docs)
            print(f"Ranked {len(ranked_documents)} documents after RRF")
            
            # Generate response
            response = generateResponse(query, ranked_documents, [], "english")
            print(f"Response preview: {response[:200]}...")
            
        else:
            # Generate response without documents
            response = generateResponse(query, [], [], "english")
            print(f"Response preview: {response[:200]}...")
        
        print(f"Response length: {len(response)} characters")
        
        # Check if response contains legal information
        legal_keywords = [
            "law", "legal", "right", "property", "contract", "penalty", "constitution", 
            "act", "code", "regulation", "procedure", "court", "judgment", "case", 
            "legal", "statute", "ordinance", "rule", "section", "article", "clause",
            "provision", "enforcement", "compliance", "violation", "offense", "crime",
            "civil", "criminal", "family", "inheritance", "marriage", "divorce",
            "tax", "gst", "income", "employment", "labor", "worker", "business",
            "corporate", "commercial", "trade", "contract", "agreement", "obligation",
            "duty", "liability", "responsibility", "authority", "jurisdiction"
        ]
        legal_content = any(keyword in response.lower() for keyword in legal_keywords)
        print(f"Contains legal content: {legal_content}")
        
        # Check if response refuses to answer
        refusal_phrases = [
            "i can only help with legal research questions",
            "i can only help with legal research",
            "please ask me about legal topics",
            "i cannot help with this",
            "i don't have information about this"
        ]
        refuses_to_answer = any(phrase in response.lower() for phrase in refusal_phrases)
        print(f"Refuses to answer: {refuses_to_answer}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_legal_questions_recognition()
