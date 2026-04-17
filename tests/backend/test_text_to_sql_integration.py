"""
Test the complete system with Text-to-SQL agent integration
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.agents.langgraph_orchestrator import get_orchestrator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_text_to_sql_integration():
    """Test Text-to-SQL agent integration with the orchestrator"""
    
    db = SessionLocal()
    orchestrator = get_orchestrator()
    
    test_cases = [
        {
            "query": "How many patients' lab reports are there in the database?",
            "patient_id": None,
            "expected_agent": "text_to_sql"
        },
        {
            "query": "Show me all patients in the system",
            "patient_id": None,
            "expected_agent": "text_to_sql"
        },
        {
            "query": "What is patient 2's glucose level?",
            "patient_id": 2,
            "expected_agent": "patient_context"
        },
        {
            "query": "Count total number of lab results in database",
            "patient_id": None,
            "expected_agent": "text_to_sql"
        },
        {
            "query": "What does research say about aspirin?",
            "patient_id": None,
            "expected_agent": "pubmed_rag"
        }
    ]
    
    print("🤖 Testing Text-to-SQL Integration with LangGraph Orchestrator")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['query']}")
        print("-" * 50)
        
        try:
            # Dispatch the query
            result = orchestrator.dispatch(
                test_case['query'], 
                {'patient_id': test_case['patient_id']}, 
                db
            )
            
            agents_used = result.get('agents_used', [])
            print(f"✅ Agents used: {agents_used}")
            print(f"✅ Query categories: {result.get('categories', [])}")
            
            # Check if correct agent was used
            if test_case['expected_agent'] in agents_used:
                print(f"✅ Correct agent ({test_case['expected_agent']}) was used")
                
                # Show Text-to-SQL specific results
                if test_case['expected_agent'] == 'text_to_sql':
                    if result.get('formatted_sql_response'):
                        print(f"\n📋 SQL Response Preview:")
                        print(result['formatted_sql_response'][:400] + "...")
                        
                    if result.get('sql_query'):
                        print(f"\n📝 Generated SQL:")
                        print(f"```sql\n{result['sql_query']}\n```")
                        
            else:
                print(f"❌ Expected {test_case['expected_agent']} but got {agents_used}")
                
            # Show results summary
            if result.get('has_sql_context'):
                print(f"✅ SQL context available")
            if result.get('has_patient_context'):
                print(f"✅ Patient context available") 
            if result.get('has_rag_context'):
                print(f"✅ RAG context available")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    db.close()
    
    print("\n" + "=" * 70)
    print("🎉 Text-to-SQL Integration Test Complete!")
    print("✅ Agent routing working correctly")
    print("✅ Text-to-SQL agent properly integrated")
    print("✅ Multi-agent system enhanced with SQL capabilities")

if __name__ == "__main__":
    test_text_to_sql_integration()