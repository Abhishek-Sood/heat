import { useState, useRef, useEffect } from 'react';
import { llmAPI, ragAPI, fileAPI } from '../services/api';

const ChatPanel = ({ patient }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('unknown'); // 'connected', 'disconnected', 'unknown'
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message when patient changes
    if (patient) {
      console.log('👤 Patient selected in ChatPanel:', {
        id: patient.id,
        name: patient.name,
        dob: patient.dob,
        timestamp: new Date().toISOString()
      });
      
      setMessages([{
        id: Date.now(),
        role: 'assistant',
        content: `I'm ready to assist with ${patient.name}'s clinical information. You can ask me about their medical history, lab results, vitals, medications, or any clinical queries.

**Patient Info:**
- ID: ${patient.id}
- Name: ${patient.name}
- DOB: ${patient.dob}
- Gender: ${patient.gender}

Try asking: "What are this patient's glucose levels?" or "Show me lab results for this patient"`,
        timestamp: new Date()
      }]);
    } else {
      console.log('ℹ️ No patient selected in ChatPanel');
      setMessages([{
        id: Date.now(),
        role: 'assistant',
        content: 'Welcome to the Clinical AI Assistant. Please select a patient to get started, or ask me general medical questions.',
        timestamp: new Date()
      }]);
    }
  }, [patient?.id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    console.log('🗣️ User submitted message:', {
      content: userMessage.content,
      patient: patient ? { id: patient.id, name: patient.name } : null,
      timestamp: new Date().toISOString()
    });

    setMessages(prev => [...prev, userMessage]);
    const queryText = input.trim();
    setInput('');
    setLoading(true);
    setIsTyping(true);

    try {
      console.log('🔄 Starting LLM query...', {
        query: queryText,
        patientId: patient?.id || null
      });

      // Use the new LLM API function
      const response = await llmAPI.queryLLM(queryText, patient?.id || null);

      console.log('✅ LLM Response received:', {
        response: response.response?.substring(0, 100) + '...',
        agents_used: response.agents_used,
        has_research_context: response.has_research_context,
        source: response.source,
        timestamp: new Date().toISOString()
      });

      // Update connection status on successful response
      setConnectionStatus('connected');

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        metadata: {
          agents_used: response.agents_used,
          has_research_context: response.has_research_context,
          source: response.source
        }
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('❌ Chat error details:', {
        error: err.message,
        response: err.response?.data,
        status: err.response?.status,
        timestamp: new Date().toISOString()
      });
      
      // Update connection status on error
      if (err.message.includes('No backend server found') || err.response?.status === 0) {
        setConnectionStatus('disconnected');
      } else {
        setConnectionStatus('connected'); // Server is responding but there might be other issues
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `I apologize, but I encountered an error processing your request: ${err.response?.data?.detail || err.message}. Please try again or rephrase your question.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!patient) {
      alert('Please select a patient first before uploading files.');
      return;
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Only PDF files are supported for lab results.');
      return;
    }

    setUploadingFile(true);

    try {
      const response = await fileAPI.uploadLabResults(patient.id, file);
      
      const successMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `Successfully uploaded and processed lab results from "${file.name}" for ${patient.name}. ${response.lab_results_added} lab results have been added to the patient's records.`,
        timestamp: new Date(),
        metadata: {
          type: 'file_upload',
          filename: file.name
        }
      };

      setMessages(prev => [...prev, successMessage]);
    } catch (err) {
      console.error('File upload error:', err);
      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `Failed to upload "${file.name}". Please ensure it's a valid PDF file with lab results. Error: ${err.response?.data?.detail || err.message}`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setUploadingFile(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRAGSearch = async (query) => {
    setLoading(true);
    try {
      const response = await ragAPI.searchMedical(query);
      
      const ragMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `**Medical Research Results:**\n\n${JSON.stringify(response, null, 2)}`,
        timestamp: new Date(),
        metadata: {
          type: 'rag_search',
          source: 'medical_literature'
        }
      };

      setMessages(prev => [...prev, ragMessage]);
    } catch (err) {
      console.error('RAG search error:', err);
      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `Failed to search medical literature. Error: ${err.response?.data?.detail || err.message}`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const suggestedQueries = patient ? [
    `What are ${patient.name}'s latest vital signs?`,
    `Summarize recent lab results`,
    `What medications is this patient on?`,
    `Any clinical alerts or concerns?`
  ] : [
    'What can you help me with?',
    'How do I interpret lab results?',
    'General clinical guidelines'
  ];

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-white to-gray-50/50">
      {/* Header */}
      <div className="p-4 border-b border-white/20 bg-gradient-to-r from-blue-600 via-blue-700 to-teal-600 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="h-12 w-12 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center shadow-inner">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              {connectionStatus === 'connected' && (
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-blue-600 shadow-sm"></div>
              )}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Clinical AI Assistant</h2>
              <p className="text-sm text-blue-100 flex items-center">
                {patient ? (
                  <>
                    <span className="w-1.5 h-1.5 rounded-full bg-green-300 mr-2 animate-pulse"></span>
                    Analyzing {patient.name}'s records
                  </>
                ) : (
                  'General medical assistant'
                )}
              </p>
            </div>
          </div>
          
          {/* Connection Status Indicator */}
          <div className={`
            flex items-center space-x-2 px-3 py-1.5 rounded-lg transition-all duration-300
            ${connectionStatus === 'connected' 
              ? 'bg-green-500/20 text-green-100' 
              : connectionStatus === 'disconnected' 
                ? 'bg-red-500/20 text-red-100' 
                : 'bg-yellow-500/20 text-yellow-100'
            }
          `}>
            <div className={`h-2 w-2 rounded-full animate-pulse ${
              connectionStatus === 'connected' ? 'bg-green-400' :
              connectionStatus === 'disconnected' ? 'bg-red-400' :
              'bg-yellow-400'
            }`}></div>
            <span className="text-xs font-medium">
              {connectionStatus === 'connected' ? 'Connected' :
               connectionStatus === 'disconnected' ? 'Offline' :
               'Checking...'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide bg-gradient-mesh">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} message-appear`}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {/* Assistant Avatar */}
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 mr-3">
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center shadow-sm ${
                  message.isError 
                    ? 'bg-gradient-to-br from-red-400 to-rose-500' 
                    : 'bg-gradient-to-br from-blue-500 to-teal-500'
                }`}>
                  {message.isError ? (
                    <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  ) : (
                    <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  )}
                </div>
              </div>
            )}
            
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm ${
                message.role === 'user'
                  ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-br-md shadow-glow-sm'
                  : message.isError
                  ? 'bg-gradient-to-br from-red-50 to-rose-50 text-red-800 border border-red-200 rounded-bl-md'
                  : 'glass-card text-gray-800 rounded-bl-md'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
              
              {/* Enhanced metadata display */}
              {message.metadata && (
                <div className="mt-3 pt-3 border-t border-gray-100/50 text-xs space-y-1.5">
                  {message.metadata.agents_used?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {message.metadata.agents_used.map((agent, i) => (
                        <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 rounded-md font-medium">
                          {agent}
                        </span>
                      ))}
                    </div>
                  )}
                  {message.metadata.has_research_context && (
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 rounded-md">
                      <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Research Enhanced
                    </span>
                  )}
                  {message.metadata.source && (
                    <div className="text-gray-400">
                      Source: <span className="text-gray-600">{message.metadata.source}</span>
                    </div>
                  )}
                </div>
              )}
              
              <div className={`flex items-center justify-between mt-2 text-xs ${
                message.role === 'user' ? 'text-blue-200' : 'text-gray-400'
              }`}>
                <span>{formatTime(message.timestamp)}</span>
                {message.metadata?.agents_used?.length > 0 && (
                  <span className="ml-2 px-2 py-0.5 bg-blue-500/20 text-blue-100 rounded-md text-xs font-medium">
                    ✨ AI Enhanced
                  </span>
                )}
              </div>
            </div>

            {/* User Avatar */}
            {message.role === 'user' && (
              <div className="flex-shrink-0 ml-3">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center shadow-sm">
                  <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Typing Indicator */}
        {loading && (
          <div className="flex justify-start message-appear">
            <div className="flex-shrink-0 mr-3">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-teal-500 flex items-center justify-center shadow-sm">
                <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <div className="glass-card rounded-2xl rounded-bl-md px-5 py-4 shadow-sm">
              <div className="flex items-center space-x-3">
                <div className="flex space-x-1.5">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span className="text-sm text-gray-500 font-medium">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Queries */}
      {messages.length <= 1 && (
        <div className="px-4 py-3 border-t border-gray-100 bg-white/80 backdrop-blur-sm">
          <p className="text-xs text-gray-500 mb-2 font-medium">💡 Suggested questions:</p>
          <div className="flex overflow-x-auto gap-2 pb-1 scrollbar-hide">
            {suggestedQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => setInput(query)}
                className="flex-shrink-0 text-xs px-4 py-2 bg-gradient-to-r from-gray-50 to-gray-100 
                  hover:from-blue-50 hover:to-indigo-50 text-gray-700 hover:text-blue-700
                  rounded-xl transition-all duration-300 border border-gray-200 hover:border-blue-200
                  hover:shadow-sm hover:scale-105 active:scale-95 whitespace-nowrap"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-100 bg-white/90 backdrop-blur-sm">
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf"
          className="hidden"
        />
        
        {/* Action buttons */}
        <div className="flex items-center space-x-2 mb-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={!patient || uploadingFile}
            className="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 
              hover:from-green-600 hover:to-emerald-700 disabled:from-gray-300 disabled:to-gray-400 
              text-white text-xs font-medium rounded-xl transition-all duration-300 shadow-sm 
              hover:shadow-md hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {uploadingFile ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            )}
            <span>{uploadingFile ? 'Uploading...' : 'Upload Lab Results'}</span>
          </button>
          
          <button
            type="button"
            onClick={() => handleRAGSearch(input.trim() || 'latest medical research')}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-purple-500 to-indigo-600 
              hover:from-purple-600 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-400 
              text-white text-xs font-medium rounded-xl transition-all duration-300 shadow-sm 
              hover:shadow-md hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Search Research</span>
          </button>
        </div>

        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder={patient ? `Ask about ${patient.name}...` : 'Ask a medical question...'}
              className="w-full px-4 py-3 bg-white border-2 border-gray-100 rounded-xl resize-none 
                focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 
                text-sm transition-all duration-300 placeholder-gray-400"
              rows="1"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="h-12 w-12 flex items-center justify-center 
              bg-gradient-to-br from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700
              disabled:from-gray-300 disabled:to-gray-400 
              text-white rounded-xl transition-all duration-300 shadow-sm
              hover:shadow-glow-sm hover:scale-105 active:scale-95
              disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-3 text-center flex items-center justify-center space-x-4">
          <span className="flex items-center space-x-1">
            <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">Enter</kbd>
            <span>to send</span>
          </span>
          <span className="text-gray-300">•</span>
          <span className="flex items-center space-x-1">
            <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">Shift+Enter</kbd>
            <span>for new line</span>
          </span>
        </p>
      </form>
    </div>
  );
};

export default ChatPanel;
