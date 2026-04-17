import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import PatientList from '../components/PatientList';
import LabResults from '../components/LabResults';
import ChatPanel from '../components/ChatPanel';

const Dashboard = () => {
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    setIsLoaded(true);
  }, []);

  const handleLogout = () => {
    authAPI.logout();
    window.location.href = '/login';
  };

  return (
    <div className={`h-screen flex flex-col bg-gradient-mesh bg-gray-50 transition-opacity duration-700 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}>
      {/* Top Navigation Bar - Modern Glass Effect */}
      <header className="glass-card border-b border-white/20 z-20 animate-fade-in-down">
        <div className="px-4 py-3 flex items-center justify-between">
          {/* Left: Logo & Title */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-xl hover:bg-white/50 lg:hidden transition-all duration-300 hover:scale-105 active:scale-95"
            >
              <svg className="h-6 w-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="flex items-center space-x-3">
              {/* Animated Logo */}
              <div className="relative">
                <div className="h-11 w-11 bg-gradient-to-br from-teal-500 to-blue-600 rounded-xl flex items-center justify-center shadow-glow-sm transition-all duration-300 hover:shadow-glow-md hover:scale-105">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                {/* Pulse ring effect */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-teal-500 to-blue-600 animate-pulse-ring opacity-0"></div>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gradient">Clinical AI Assistant</h1>
                <p className="text-xs text-gray-500 hidden sm:block">Intelligent Healthcare Dashboard</p>
              </div>
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center space-x-3">
            {selectedPatient && (
              <div className="hidden md:flex items-center px-4 py-2 bg-gradient-to-r from-teal-50 to-blue-50 rounded-xl border border-teal-100/50 animate-fade-in">
                <div className="w-2 h-2 rounded-full bg-teal-500 mr-2 animate-pulse"></div>
                <span className="text-sm text-gray-700">
                  Active: <span className="font-semibold text-gradient">{selectedPatient.name}</span>
                </span>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:text-red-600 bg-white/50 hover:bg-red-50 rounded-xl border border-gray-200/50 hover:border-red-200 transition-all duration-300 hover:scale-105 active:scale-95"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="hidden sm:inline font-medium">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Patient List */}
        <aside
          className={`${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } fixed lg:relative lg:translate-x-0 z-20 w-80 h-full glass-card border-r border-white/20 transition-all duration-500 ease-out animate-slide-in-left`}
        >
          <PatientList
            onSelectPatient={(patient) => {
              setSelectedPatient(patient);
              // Close sidebar on mobile after selection
              if (window.innerWidth < 1024) {
                setSidebarOpen(false);
              }
            }}
            selectedPatientId={selectedPatient?.id}
          />
        </aside>

        {/* Overlay for mobile sidebar */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-10 lg:hidden modal-backdrop"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Center Panel - Lab Results */}
        <main className="flex-1 flex flex-col min-w-0 glass border-r border-white/20 animate-fade-in">
          <LabResults patient={selectedPatient} />
        </main>

        {/* Right Panel - Chat */}
        <aside className="hidden xl:flex w-96 flex-col glass-card animate-slide-in-right">
          <ChatPanel patient={selectedPatient} />
        </aside>
      </div>

      {/* Mobile Chat Button - Enhanced Floating Button */}
      <div className="xl:hidden fixed bottom-6 right-6 z-30">
        <EnhancedFloatingChatButton patient={selectedPatient} />
      </div>
    </div>
  );
};

// Enhanced Floating Chat Button Component
const EnhancedFloatingChatButton = ({ patient }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  // Show tooltip after a delay when mounted
  useEffect(() => {
    const timer = setTimeout(() => setShowTooltip(true), 2000);
    const hideTimer = setTimeout(() => setShowTooltip(false), 6000);
    return () => {
      clearTimeout(timer);
      clearTimeout(hideTimer);
    };
  }, []);

  return (
    <>
      {/* Floating Button Container */}
      <div 
        className="fab-container relative"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Multiple Pulse Rings */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500 to-teal-500 fab-pulse-ring"></div>
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500 to-teal-500 fab-pulse-ring" style={{ animationDelay: '0.5s' }}></div>
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500 to-teal-500 fab-pulse-ring" style={{ animationDelay: '1s' }}></div>
        
        {/* Main Button */}
        <button
          onClick={() => setIsOpen(true)}
          className={`
            relative h-16 w-16 
            bg-gradient-to-br from-blue-500 via-blue-600 to-teal-500 
            text-white rounded-full 
            shadow-lg fab-glow
            flex items-center justify-center 
            transition-all duration-500 ease-out
            ${isHovered ? 'scale-110 rotate-12' : 'scale-100 rotate-0'}
            hover:from-blue-600 hover:via-blue-700 hover:to-teal-600
            active:scale-95 active:rotate-0
            overflow-hidden
          `}
        >
          {/* Shimmer Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-shimmer"></div>
          
          {/* Icon with animation */}
          <div className={`transition-all duration-300 ${isHovered ? 'scale-110' : 'scale-100'}`}>
            <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>

          {/* Notification Badge */}
          <div className="absolute -top-1 -right-1 h-5 w-5 bg-gradient-to-br from-red-500 to-pink-500 rounded-full flex items-center justify-center text-xs font-bold shadow-lg animate-bounce-gentle">
            <span className="text-white">AI</span>
          </div>
        </button>

        {/* Tooltip */}
        {showTooltip && !isOpen && (
          <div className="absolute bottom-full right-0 mb-4 animate-fade-in-up">
            <div className="bg-gray-900 text-white text-sm px-4 py-2 rounded-xl shadow-xl whitespace-nowrap">
              <div className="flex items-center space-x-2">
                <span className="text-lg">💬</span>
                <span>Ask AI about your patients!</span>
              </div>
              <div className="absolute bottom-0 right-6 transform translate-y-1/2 rotate-45 w-3 h-3 bg-gray-900"></div>
            </div>
          </div>
        )}

        {/* Hover Label */}
        <div className={`
          absolute right-full mr-4 top-1/2 -translate-y-1/2
          bg-white rounded-xl px-4 py-2 shadow-card
          border border-gray-100
          transition-all duration-300
          ${isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4 pointer-events-none'}
        `}>
          <span className="text-sm font-medium text-gradient whitespace-nowrap">Clinical AI Chat</span>
        </div>
      </div>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 modal-backdrop bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-lg h-[85vh] glass-card rounded-t-3xl sm:rounded-3xl overflow-hidden shadow-2xl flex flex-col modal-content border border-white/20">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-gradient-to-r from-blue-600 via-blue-700 to-teal-600">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
                  <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Clinical AI Chat</h3>
                  <p className="text-xs text-blue-100">
                    {patient ? `Assisting with ${patient.name}` : 'General medical assistant'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/20 rounded-xl transition-all duration-300 hover:scale-110 active:scale-95 group"
              >
                <svg className="h-6 w-6 text-white group-hover:rotate-90 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {/* Chat Content */}
            <div className="flex-1 overflow-hidden">
              <ChatPanel patient={patient} />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Dashboard;
