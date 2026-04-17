import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    identifier: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Basic validation
    if (!formData.identifier || !formData.password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      await authAPI.login(formData);
      navigate('/dashboard');
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        err.response?.data?.message ||
        'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-mesh bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-teal-400/20 to-blue-500/20 rounded-full blur-3xl animate-float-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-br from-purple-400/20 to-pink-500/20 rounded-full blur-3xl animate-float-slow" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-conic from-teal-500/5 via-blue-500/5 to-purple-500/5 rounded-full blur-3xl"></div>
      </div>

      <div className={`max-w-md w-full space-y-8 relative z-10 transition-all duration-700 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
        <div className="text-center">
          {/* Animated Logo */}
          <div className="mx-auto relative w-20 h-20 mb-6">
            <div className="absolute inset-0 bg-gradient-to-br from-teal-400 to-blue-600 rounded-2xl rotate-6 opacity-20 animate-pulse"></div>
            <div className="relative h-20 w-20 bg-gradient-to-br from-teal-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-glow-teal transition-transform hover:scale-105 hover:rotate-3 cursor-pointer">
              <svg className="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gradient mb-2">
            Welcome Back
          </h2>
          <p className="text-gray-500">
            Sign in to your Clinical AI Assistant account
          </p>
        </div>
        
        <div className="glass-card p-8 rounded-2xl shadow-glass animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-3 animate-fade-in">
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center">
                  <svg className="h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-sm font-medium">{error}</span>
              </div>
            )}
            
            <div className="space-y-2">
              <label htmlFor="identifier" className="block text-sm font-semibold text-gray-700">
                Username or Email
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  id="identifier"
                  name="identifier"
                  type="text"
                  required
                  value={formData.identifier}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3 bg-white border-2 border-gray-100 rounded-xl text-gray-900 placeholder-gray-400 
                    focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all duration-300"
                  placeholder="Enter your username or email"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                Password
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3 bg-white border-2 border-gray-100 rounded-xl text-gray-900 placeholder-gray-400 
                    focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all duration-300"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className={`w-full flex justify-center items-center py-3.5 px-4 border border-transparent text-base font-semibold rounded-xl text-white
                  ${loading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-glow-sm hover:shadow-glow-md hover:scale-[1.02] active:scale-[0.98]'
                  } transition-all duration-300`}
              >
                {loading ? (
                  <div className="flex items-center space-x-3">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Signing in...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <span>Sign In</span>
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                )}
              </button>
            </div>
          </form>
          
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500 font-medium">New to Clinical AI?</span>
              </div>
            </div>
            
            <div className="mt-6">
              <Link
                to="/signup"
                className="w-full flex justify-center items-center py-3 px-4 border-2 border-gray-200 rounded-xl shadow-sm text-base font-semibold text-gray-700 
                  bg-white hover:bg-gradient-to-r hover:from-gray-50 hover:to-blue-50 hover:border-blue-200 hover:text-blue-700
                  focus:outline-none focus:ring-4 focus:ring-blue-500/10 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
              >
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                Create an account
              </Link>
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <p className="text-center text-sm text-gray-500 animate-fade-in" style={{ animationDelay: '400ms' }}>
          By signing in, you agree to our{' '}
          <span className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium">Terms of Service</span>
          {' '}and{' '}
          <span className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium">Privacy Policy</span>
        </p>
      </div>
    </div>
  );
};

export default Login;