from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.logging import setup_logging
from ..core.config import get_settings
from groq import Groq
import logging

logger = logging.getLogger("text_to_sql_agent")
settings = get_settings()

class TextToSQLAgent:
    """
    Generates SQL queries from natural language for database-related questions.
    """
    
    def __init__(self):
        self.name = "text_to_sql"
        self.description = "Converts natural language queries to SQL and executes database operations"
        
        # Database schema information for generating accurate SQL
        self.schema_info = {
            'patients': ['id', 'name', 'dob', 'gender', 'contact', 'address', 'created_at', 'updated_at'],
            'lab_results': ['id', 'patient_id', 'timestamp', 'test_name', 'result', 'unit', 'reference_range'],
            'vitals': ['id', 'patient_id', 'timestamp', 'type', 'value', 'unit'],
            'medications': ['id', 'patient_id', 'name', 'dosage', 'frequency', 'start_date', 'end_date'],
            'reports': ['id', 'patient_id', 'content', 'created_at'],
            'alerts': ['id', 'patient_id', 'severity', 'created_at', 'resolved'],
            'conversations': ['id', 'patient_id', 'title', 'created_at'],
            'messages': ['id', 'conversation_id', 'role', 'content', 'timestamp']
        }
    
    def can_handle(self, query: str, context: Dict[str, Any] = None) -> bool:
        """
        Determines if the query is database-related using LLM classification - no keyword matching.
        """
        try:
            if not settings.GROQ_API_KEY:
                # Fallback: assume any query could potentially be database-related
                return True
            
            # Simple prompt that works with the model
            classification_prompt = f"Is the query '{query}' about database operations? Answer YES or NO."

            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "YES"
            
        except Exception as e:
            logger.warning(f"Error in LLM classification, defaulting to False: {e}")
            return False
    
    def process(self, query: str, context: Dict[str, Any], db: Session = None) -> Dict[str, Any]:
        """
        Generate SQL query based on natural language input and optionally execute it.
        
        Args:
            query: Natural language database query
            context: Additional context
            db: Database session (optional for execution)
            
        Returns:
            Dict containing generated SQL, explanation, and optional results
        """
        try:
            logger.info(f"Processing Text-to-SQL query: {query[:100]}...")
            
            # Generate SQL query based on the natural language input
            sql_query, explanation = self._generate_sql(query)
            
            result = {
                'agent_used': self.name,
                'has_context': True,
                'sql_query': sql_query,
                'explanation': explanation,
                'query_type': self._classify_query_type(query)
            }
            
            # Optionally execute the query if database session is provided
            if db and sql_query:
                try:
                    db_result = db.execute(text(sql_query)).fetchall()
                    result['execution_result'] = [dict(row._mapping) for row in db_result] if db_result else []
                    result['execution_success'] = True
                except Exception as exec_error:
                    logger.warning(f"Could not execute SQL query: {exec_error}")
                    result['execution_result'] = None
                    result['execution_success'] = False
                    result['execution_error'] = str(exec_error)
            
            # Format the response in markdown
            result['formatted_response'] = self._format_markdown_response(
                query, sql_query, explanation, result.get('execution_result')
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Text-to-SQL agent: {str(e)}")
            return {
                'agent_used': self.name,
                'has_context': False,
                'error': str(e),
                'formatted_response': f"**Error**: Unable to process database query: {str(e)}"
            }
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of database query using LLM - no keyword matching"""
        try:
            if not settings.GROQ_API_KEY:
                return 'general'
            
            classification_prompt = f"""Classify this database query into one of these categories:

Query: "{query}"

Categories:
- count: Questions asking for counts, totals, or numbers
- select: Questions asking to list, show, or retrieve data
- average: Questions asking for averages or means
- max: Questions asking for maximum values
- min: Questions asking for minimum values  
- general: All other types of queries

Answer with only the category name:"""

            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().lower()
            valid_types = ['count', 'select', 'average', 'max', 'min', 'general']
            return result if result in valid_types else 'general'
            
        except Exception as e:
            logger.warning(f"Error classifying query type: {e}")
            return 'general'
    
    def _generate_sql(self, query: str) -> tuple[str, str]:
        """Generate SQL query from natural language using LLM - no hardcoding"""
        try:
            # Build schema context for the LLM
            schema_context = self._build_schema_context()
            
            # Create the prompt for SQL generation (similar to your notebook approach)
            prompt = f"""Convert the following natural language question into a single executable PostgreSQL query.

Schema:
{schema_context}

Question: {query}

Requirements:
- Output only the raw SQL statement, nothing else
- Use explicit column names, not SELECT *
- Use table aliases for joins
- Handle NULL values appropriately
- Use PostgreSQL syntax
- Don't output in markdowns or backticks

SQL:"""

            # Use Groq to generate SQL (same as your notebook)
            if settings.GROQ_API_KEY:
                client = Groq(api_key=settings.GROQ_API_KEY)
                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )
                
                sql = response.choices[0].message.content.strip()
                # Clean the response - remove markdown code blocks if present
                sql = sql.replace("```sql", "").replace("```", "").strip()
                
                # Generate a simple explanation
                explanation = f"Generated SQL query to answer: {query}"
                
                return sql, explanation
            else:
                logger.error("GROQ_API_KEY not configured")
                return "", "Error: GROQ_API_KEY not configured"
                
        except Exception as e:
            logger.error(f"Error generating SQL with LLM: {str(e)}")
            return "", f"Error generating SQL: {str(e)}"
    
    def _build_schema_context(self) -> str:
        """Build simple schema context for the LLM - similar to notebook approach"""
        return """
patients(id, name, dob, gender, contact, address, created_at, updated_at)
lab_results(id, patient_id, timestamp, test_name, result, unit, reference_range)
vitals(id, patient_id, timestamp, type, value, unit)
medications(id, patient_id, name, dosage, frequency, start_date, end_date)
reports(id, patient_id, content, created_at)
alerts(id, patient_id, severity, created_at, resolved)
conversations(id, patient_id, title, created_at)
messages(id, conversation_id, role, content, timestamp)
"""
    
    def _format_markdown_response(self, original_query: str, sql_query: str, explanation: str, results: Optional[list] = None) -> str:
        """Format the response in markdown"""
        response = f"**Database Query Analysis**\n\n"
        response += f"**Original Question**: {original_query}\n\n"
        
        response += f"**Generated SQL Query**:\n```sql\n{sql_query}\n```\n\n"
        
        response += f"**Explanation**: {explanation}\n\n"
        
        if results is not None:
            if results:
                response += f"**Query Results**:\n"
                if len(results) == 1 and len(results[0]) == 1:
                    # Simple count result
                    value = list(results[0].values())[0]
                    response += f"- **Answer**: {value}\n\n"
                else:
                    # Multiple results - format as table
                    response += "| " + " | ".join(results[0].keys()) + " |\n"
                    response += "| " + " | ".join(['---'] * len(results[0])) + " |\n"
                    for row in results[:10]:  # Limit to first 10 rows
                        response += "| " + " | ".join(str(v) for v in row.values()) + " |\n"
                    
                    if len(results) > 10:
                        response += f"\n*Showing first 10 of {len(results)} results*\n"
            else:
                response += f"**Query Results**: No data found.\n\n"
        
        response += f"**How to use**: You can copy and paste the SQL query above into any PostgreSQL client or database management tool to get the results directly."
        
        return response