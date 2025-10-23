import React, { useState } from 'react';
import { AlertCircle, Zap, Send, RotateCcw } from 'lucide-react';
import { analyzeIncident } from './services/api';
import LoadingSpinner from './components/LoadingSpinner';
import IncidentAnalysis from './components/IncidentAnalysis';
import SearchResults from './components/SearchResults';
import ResolutionRecommendation from './components/ResolutionRecommendation';
import ConfidenceScore from './components/ConfidenceScore';

const SAMPLE_INCIDENTS = [
  {
    title: "Database Connection Pool Exhausted",
    description: "Users reporting 500 errors on checkout page. Error logs show: HikariCP - Connection is not available, request timed out after 30000ms. Connection pool size currently at 20. Peak traffic during flash sale."
  },
  {
    title: "Memory Leak in Production",
    description: "User service pods crashing every 2-3 hours with OutOfMemoryError. Heap dumps show excessive String objects. GC logs indicate heap exhaustion before crash. Need immediate resolution."
  },
  {
    title: "API Gateway Timeouts",
    description: "Users reporting API timeouts. Gateway returning 504 Gateway Timeout errors. Backend services appear healthy but response times elevated from 200ms to 8000ms. N+1 query suspected."
  }
];

function App() {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [processingSteps, setProcessingSteps] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!description.trim()) {
      setError('Please enter an incident description');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);
    setProcessingSteps([
      'Analyzing incident with Gemini 2.0...',
      'Extracting technical terms and symptoms...',
      'Formulating search strategy...',
      'Executing hybrid search across knowledge base...',
      'Synthesizing resolution recommendation...'
    ]);
    
    try {
      const response = await analyzeIncident(description);
      setResult(response);
      setProcessingSteps([]);
    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze incident. Please try again.');
      setProcessingSteps([]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDescription('');
    setResult(null);
    setError(null);
    setProcessingSteps([]);
  };

  const loadSample = (sample) => {
    setDescription(sample.description);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <Zap className="w-10 h-10 text-primary-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
              DevOps Oracle
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-Powered Incident Resolution System
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Powered by Google Cloud Vertex AI & Elastic Hybrid Search
          </p>
        </div>

        {/* Input Section */}
        <div className="card mb-8 max-w-4xl mx-auto">
          <form onSubmit={handleSubmit}>
            <label className="block text-lg font-semibold text-gray-800 mb-3">
              Describe Your Incident
            </label>
            
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Paste your incident description here... Include error messages, symptoms, affected systems, and any relevant details."
              className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              disabled={loading}
            />
            
            {/* Sample Incidents */}
            <div className="mt-4 mb-4">
              <p className="text-sm text-gray-600 mb-2">Try a sample incident:</p>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_INCIDENTS.map((sample, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => loadSample(sample)}
                    className="text-sm px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md border border-gray-300 transition-colors"
                    disabled={loading}
                  >
                    {sample.title}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading || !description.trim()}
                className="btn-primary flex items-center gap-2"
              >
                <Send className="w-5 h-5" />
                {loading ? 'Analyzing...' : 'Analyze Incident'}
              </button>
              
              {(result || description) && !loading && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  <RotateCcw className="w-5 h-5" />
                  Reset
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-danger-50 border border-danger-300 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-danger-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-danger-800 mb-1">Error</h3>
                <p className="text-danger-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="max-w-4xl mx-auto">
            <LoadingSpinner
              message="Analyzing your incident..."
              steps={processingSteps}
            />
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-6 animate-fade-in">
            {/* Processing Stats */}
            <div className="max-w-4xl mx-auto bg-gradient-to-r from-primary-50 to-primary-100 border border-primary-200 rounded-lg p-4">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <p className="text-sm text-primary-700 font-medium">Request ID</p>
                  <p className="font-mono text-primary-900">{result.request_id}</p>
                </div>
                <div>
                  <p className="text-sm text-primary-700 font-medium">Processing Time</p>
                  <p className="font-semibold text-primary-900">{result.processing_time_seconds}s</p>
                </div>
                <div>
                  <p className="text-sm text-primary-700 font-medium">Agent Steps</p>
                  <p className="font-semibold text-primary-900">{result.agent_steps.length} completed</p>
                </div>
              </div>
            </div>

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Analysis & Results */}
              <div className="lg:col-span-2 space-y-6">
                <IncidentAnalysis analysis={result.analysis} />
                <SearchResults results={result.search_results} />
              </div>
              
              {/* Right Column - Confidence */}
              <div className="lg:col-span-1">
                <div className="sticky top-6">
                  <ConfidenceScore
                    score={result.recommendation.confidence_score}
                    reasoning={result.recommendation.confidence_reasoning}
                  />
                </div>
              </div>
            </div>

            {/* Full Width - Recommendation */}
            <div className="max-w-5xl mx-auto">
              <ResolutionRecommendation recommendation={result.recommendation} />
            </div>

            {/* Agent Timeline */}
            <div className="max-w-4xl mx-auto card">
              <h3 className="font-semibold text-gray-800 mb-3">Agent Execution Timeline</h3>
              <div className="space-y-2">
                {result.agent_steps.map((step, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 text-sm text-gray-700"
                  >
                    <div className="w-2 h-2 rounded-full bg-success-500" />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-16 text-center text-sm text-gray-500">
          <p>Built with Google Cloud Vertex AI (Gemini 2.0) & Elastic Hybrid Search</p>
          <p className="mt-1">AI Accelerate Hackathon - Elastic Challenge</p>
        </div>
      </div>
    </div>
  );
}

export default App;