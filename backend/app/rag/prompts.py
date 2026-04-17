from typing import List, Dict, Any

def build_rag_context(query: str, docs: List[Dict[str, Any]]) -> str:
    """
    CRITICAL: Format RAG context exactly as specified to reduce hallucinations.
    
    Args:
        query: User query
        docs: Retrieved documents with 'text', 'title', 'pubmed_id' keys
        
    Returns:
        Formatted context string with proper citations, or empty string if no docs
    """
    if not docs:
        return ""
    
    # Build the context sections
    context_parts = []
    
    # Header with paper titles and PubMed IDs
    context_parts.append("Based on your query and recent research:")
    context_parts.append("")
    
    for i, doc in enumerate(docs, 1):
        title = doc.get('title', 'Unknown Title')
        pubmed_id = doc.get('pubmed_id', 'Unknown ID')
        context_parts.append(f"* \"{title}\" (PubMed ID: {pubmed_id})")
    
    context_parts.append("")
    context_parts.append("Instructions:")
    context_parts.append("* Use the above research to answer the query.")
    context_parts.append("* When using information, cite references like [1], [2].")
    context_parts.append("* Do NOT make up references.")
    context_parts.append("")
    
    # Add the research content
    for i, doc in enumerate(docs, 1):
        text = doc.get('text', '')
        if text:
            context_parts.append(f"[{i}] {text}")
            context_parts.append("")
    
    # References section
    context_parts.append("References:")
    for i, doc in enumerate(docs, 1):
        title = doc.get('title', 'Unknown Title')
        pubmed_id = doc.get('pubmed_id', 'Unknown ID')
        context_parts.append(f"{i}. {title}. PubMed: {pubmed_id}")
    
    return "\n".join(context_parts)

def diagnosis_prompt(patient, vitals, labs):
    """Legacy function for backward compatibility"""
    return f"""
    Patient: {patient.name}, DOB: {patient.dob}, Gender: {patient.gender}
    Vitals: {[(v.type, v.value, v.unit) for v in vitals]}
    Labs: {[(l.test_name, l.result, l.unit) for l in labs]}
    What are the possible conditions? List with uncertainty and always include a disclaimer.
    """

def treatment_prompt(context):
    """Legacy function for backward compatibility"""
    return f"""
    Context: {context}
    Suggest possible treatment options with uncertainty and always include a disclaimer.
    """
