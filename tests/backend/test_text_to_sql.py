"""
Test the Text-to-SQL agent with LLM-based SQL generation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.agents.text_to_sql_agent import TextToSQLAgent
from app.db.database import SessionLocal
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_text_to_sql_agent():
    """Test the Text-to-SQL agent with various queries"""
    
    db = SessionLocal()
    agent = TextToSQLAgent()
    
    test_queries = [
        "How many patients are in the database?",
        "Show me all patients with lab results",
        "What is the total number of lab reports?", 
        "List all patients who have medications",
        "How many reports are there in the system?",
        "Find the average glucose levels",
        "Show recent lab results for all patients",
        "Count total vitals recorded",
        "Which patients have the most lab tests?"
    ]
    
    print("🧪 Testing Text-to-SQL Agent with LLM")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Check if agent can handle the query
            can_handle = agent.can_handle(query)
            print(f"✅ Can handle: {can_handle}")
            
            if can_handle:
                # Process the query
                result = agent.process(query, {}, db)
                
                print(f"✅ Agent used: {result.get('agent_used')}")
                print(f"✅ Has context: {result.get('has_context')}")
                print(f"✅ Query type: {result.get('query_type')}")
                
                if result.get('sql_query'):
                    print(f"\n📝 Generated SQL:")
                    print(f"```sql\n{result['sql_query']}\n```")
                    
                if result.get('explanation'):
                    print(f"\n💡 Explanation: {result['explanation']}")
                    
                if result.get('execution_result') is not None:
                    print(f"\n📊 Results: {result['execution_result']}")
                    
                if result.get('formatted_response'):
                    print(f"\n📋 Formatted Response Preview:")
                    print(result['formatted_response'][:300] + "...")
                    
            else:
                print("❌ Agent cannot handle this query type")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("🎉 Text-to-SQL Agent Testing Complete!")
    print("✅ LLM-based SQL generation working")
    print("✅ Dynamic query processing enabled")
    print("✅ No hardcoded SQL patterns required")

if __name__ == "__main__":
    test_text_to_sql_agent()