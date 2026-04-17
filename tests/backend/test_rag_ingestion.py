#!/usr/bin/env python3
"""
Test script for RAG pipeline ingestion
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.rag.ingest import ingest_pubmed_csv
from app.rag.retriever import retrieve_pubmed_chunks, get_rag_context

def create_sample_csv():
    """Create a sample PubMed CSV for testing"""
    import pandas as pd
    
    sample_data = [
        {
            'title': 'Effects of Aspirin on Cardiovascular Disease Prevention',
            'abstract': 'This study examines the effectiveness of low-dose aspirin in preventing cardiovascular events. Results show a 20% reduction in heart attack risk among high-risk patients. Side effects include increased bleeding risk. Regular monitoring is recommended for patients on long-term aspirin therapy.',
            'pubmed_id': '12345678'
        },
        {
            'title': 'Diabetes Management with Metformin: Long-term Outcomes',
            'abstract': 'Metformin remains the first-line treatment for type 2 diabetes management. This longitudinal study followed 1000 patients for 10 years. HbA1c levels decreased by 1.5% on average. Weight loss of 3-5kg was observed in 60% of patients. Gastrointestinal side effects were reported in 15% of cases.',
            'pubmed_id': '87654321'
        },
        {
            'title': 'Antibiotic Resistance Patterns in Hospital-Acquired Infections',
            'abstract': 'Analysis of antibiotic resistance patterns shows increasing resistance to first-line antibiotics. MRSA infections increased by 30% over the past 5 years. Combination therapy with vancomycin and rifampin shows promise. Hospital infection control measures are crucial for preventing spread.',
            'pubmed_id': '11223344'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    csv_path = os.path.join(os.path.dirname(__file__), 'sample_pubmed.csv')
    df.to_csv(csv_path, index=False)
    return csv_path

def test_ingestion():
    """Test the ingestion pipeline"""
    print("🧪 Testing RAG Pipeline Ingestion...")
    
    try:
        # Create sample CSV
        csv_path = create_sample_csv()
        print(f"📄 Created sample CSV: {csv_path}")
        
        # Ingest the data
        print("⚙️ Ingesting PubMed data...")
        num_chunks = ingest_pubmed_csv(csv_path)
        print(f"✅ Successfully ingested {num_chunks} chunks")
        
        # Test retrieval
        test_queries = [
            "aspirin cardiovascular prevention",
            "metformin diabetes treatment", 
            "antibiotic resistance hospital"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            chunks = retrieve_pubmed_chunks(query, top_k=2)
            print(f"📋 Retrieved {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                print(f"  [{i+1}] Title: {chunk['title']}")
                print(f"      PubMed ID: {chunk['pubmed_id']}")
                print(f"      Similarity: {chunk['similarity_score']:.3f}")
        
        # Test RAG context generation
        print(f"\n🤖 Testing RAG context generation...")
        rag_context = get_rag_context("What are the side effects of aspirin for cardiovascular prevention?")
        if rag_context:
            print("✅ RAG context generated successfully")
            print("📝 Sample context (first 200 chars):")
            print(rag_context[:200] + "..." if len(rag_context) > 200 else rag_context)
        else:
            print("❌ No RAG context generated")
        
        # Clean up
        os.remove(csv_path)
        print(f"\n🧹 Cleaned up sample CSV")
        
        print("\n🎉 RAG pipeline test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ingestion()