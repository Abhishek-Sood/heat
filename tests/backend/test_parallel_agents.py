#!/usr/bin/env python3
"""
Test script for parallel multi-agent execution
Demonstrates how the system now handles queries requiring both patient context and research
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.agents.langgraph_orchestrator import get_orchestrator
import time

def test_parallel_agents():
    """Test parallel execution of multiple agents"""
    print("🚀 Testing Parallel Multi-Agent Execution...")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = get_orchestrator()
    
    # Test queries that should trigger BOTH agents
    parallel_test_queries = [
        {
            'query': "should i recommend aspirin to patient 2",
            'patient_id': 2,
            'expected_agents': ['patient_context', 'pubmed_rag'],
            'description': "Aspirin recommendation - needs BOTH patient data AND research"
        },
        {
            'query': "what does research say about metformin for patient 5 with diabetes?",
            'patient_id': 5, 
            'expected_agents': ['patient_context', 'pubmed_rag'],
            'description': "Drug research query with patient - needs BOTH contexts"
        },
        {
            'query': "show me evidence-based treatment for patient 1's hypertension",
            'patient_id': 1,
            'expected_agents': ['patient_context', 'pubmed_rag'], 
            'description': "Evidence-based treatment - needs BOTH patient and research"
        }
    ]
    
    # Test queries that should trigger SINGLE agents
    single_agent_queries = [
        {
            'query': "what is patient 3's latest glucose level?",
            'patient_id': 3,
            'expected_agents': ['patient_context'],
            'description': "Patient query only - just database lookup"
        },
        {
            'query': "what does latest research say about statins?",
            'patient_id': None,
            'expected_agents': ['pubmed_rag'],
            'description': "Research query only - just literature search"
        },
        {
            'query': "what time is it?", 
            'patient_id': None,
            'expected_agents': [],
            'description': "General query - no specialized agents"
        }
    ]
    
    print("🎯 Testing PARALLEL Agent Execution...")
    print("-" * 50)
    
    for i, test_case in enumerate(parallel_test_queries, 1):
        print(f"\n🔄 Parallel Test {i}: {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")
        print(f"Patient ID: {test_case['patient_id']}")
        
        # Time the parallel dispatch
        start_time = time.time()
        result = orchestrator.dispatch(
            test_case['query'],
            {'patient_id': test_case['patient_id']},
            db=None  # Would be actual DB session in real usage
        )
        dispatch_time = time.time() - start_time
        
        print(f"⚡ Total dispatch time: {dispatch_time:.3f}s")
        print(f"🎯 Agents used: {result['agents_used']}")
        print(f"📚 Has RAG context: {'Yes' if result['has_rag_context'] else 'No'}")
        print(f"👤 Has patient context: {'Yes' if result['has_patient_context'] else 'No'}")
        print(f"🆔 Patient ID resolved: {result.get('patient_id', 'None')}")
        
        # Check if expected agents were triggered
        expected = set(test_case['expected_agents'])
        actual = set(result['agents_used'])
        
        if expected.issubset(actual):
            print("✅ Expected agents triggered correctly")
        else:
            print(f"❌ Expected {expected}, got {actual}")
            
        print("-" * 30)
    
    print("\n🎯 Testing SINGLE Agent Execution...")
    print("-" * 50)
    
    for i, test_case in enumerate(single_agent_queries, 1):
        print(f"\n🔄 Single Test {i}: {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")
        
        start_time = time.time()
        result = orchestrator.dispatch(
            test_case['query'],
            {'patient_id': test_case['patient_id']},
            db=None
        )
        dispatch_time = time.time() - start_time
        
        print(f"⚡ Dispatch time: {dispatch_time:.3f}s")
        print(f"🎯 Agents used: {result['agents_used']}")
        
        expected = set(test_case['expected_agents'])
        actual = set(result['agents_used'])
        
        if expected == actual:
            print("✅ Correct agent routing")
        else:
            print(f"❌ Expected {expected}, got {actual}")
            
        print("-" * 30)
    
    print(f"\n🏆 Parallel Multi-Agent System Benefits:")
    print("  • Multiple agents run concurrently (not sequentially)")
    print("  • Patient context + Research context retrieved in parallel") 
    print("  • Automatic patient ID extraction from queries")
    print("  • Intelligent routing - only needed agents execute")
    print("  • Comprehensive medical decision support")
    print("  • Error isolation - if one agent fails, others continue")

def test_patient_id_extraction():
    """Test automatic patient ID extraction from queries"""
    print("\n🔍 Testing Patient ID Extraction...")
    print("=" * 50)
    
    orchestrator = get_orchestrator()
    
    id_extraction_tests = [
        "should i recommend aspirin to patient 2",
        "what is patient 15's blood pressure?", 
        "patient 007 needs new medication",
        "check labs for patient 123",
        "is patient 5 diabetic?"
    ]
    
    for query in id_extraction_tests:
        result = orchestrator.dispatch(query, {}, db=None)
        extracted_id = result.get('patient_id')
        
        print(f"Query: \"{query}\"")
        print(f"Extracted Patient ID: {extracted_id}")
        print(f"Agents: {result['agents_used']}")
        print("-" * 30)

if __name__ == "__main__":
    test_parallel_agents()
    test_patient_id_extraction()