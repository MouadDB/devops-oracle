import React from 'react';
import { Lightbulb, CheckCircle2, Shield, Clock, AlertTriangle } from 'lucide-react';

const ResolutionRecommendation = ({ recommendation }) => {
  const riskConfig = {
    low: { color: 'text-success-600', bg: 'bg-success-50', icon: '✓' },
    medium: { color: 'text-warning-600', bg: 'bg-warning-50', icon: '⚠️' },
    high: { color: 'text-danger-600', bg: 'bg-danger-50', icon: '⚠️' }
  };
  
  const risk = riskConfig[recommendation.risk_assessment] || riskConfig.medium;
  
  return (
    <div className="card animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-6 h-6 text-primary-600" />
        <h2 className="text-xl font-bold text-gray-800">Resolution Strategy</h2>
      </div>
      
      {/* Immediate Actions */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-danger-500" />
          Immediate Actions
        </h3>
        <ol className="space-y-2">
          {recommendation.immediate_actions.map((action, index) => (
            <li
              key={index}
              className="flex items-start gap-3 p-3 bg-danger-50 border border-danger-200 rounded-lg"
            >
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-danger-500 text-white text-sm font-bold flex items-center justify-center">
                {index + 1}
              </span>
              <span className="text-gray-800 pt-0.5">{action}</span>
            </li>
          ))}
        </ol>
      </div>
      
      {/* Root Cause Hypothesis */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-800 mb-3">Root Cause Hypothesis</h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-gray-700">{recommendation.root_cause_hypothesis}</p>
        </div>
      </div>
      
      {/* Resolution Steps */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-success-500" />
          Detailed Resolution Steps
        </h3>
        <ol className="space-y-3">
          {recommendation.resolution_steps.map((step, index) => (
            <li
              key={index}
              className="flex items-start gap-3 p-4 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow"
            >
              <span className="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500 text-white text-sm font-bold flex items-center justify-center">
                {index + 1}
              </span>
              <div className="flex-1">
                <p className="text-gray-800 whitespace-pre-wrap">{step}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
      
      {/* Preventive Measures */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary-500" />
          Preventive Measures
        </h3>
        <ul className="space-y-2">
          {recommendation.preventive_measures.map((measure, index) => (
            <li
              key={index}
              className="flex items-start gap-2 p-3 bg-gray-50 border border-gray-200 rounded-lg"
            >
              <CheckCircle2 className="w-5 h-5 text-success-500 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700">{measure}</span>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-400" />
          <div>
            <p className="text-sm text-gray-600">Estimated Resolution Time</p>
            <p className="font-semibold text-gray-800">
              {recommendation.estimated_resolution_time_minutes} minutes
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-gray-400" />
          <div>
            <p className="text-sm text-gray-600">Risk Assessment</p>
            <p className={`font-semibold ${risk.color} flex items-center gap-1`}>
              <span>{risk.icon}</span>
              <span className="capitalize">{recommendation.risk_assessment} Risk</span>
            </p>
          </div>
        </div>
      </div>
      
      {recommendation.similar_incident_references.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-2">Based on similar incidents:</p>
          <div className="flex flex-wrap gap-2">
            {recommendation.similar_incident_references.map((ref, index) => (
              <span
                key={index}
                className="badge bg-primary-100 text-primary-700 border border-primary-300 font-mono"
              >
                {ref}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResolutionRecommendation;