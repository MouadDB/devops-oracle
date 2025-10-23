import React from 'react';
import { AlertCircle, Server, Clock, Tag } from 'lucide-react';
import SeverityBadge from './SeverityBadge';
import { getIncidentTypeConfig } from '../utils/helpers';

const IncidentAnalysis = ({ analysis }) => {
  const typeConfig = getIncidentTypeConfig(analysis.incident_type);
  
  return (
    <div className="card animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <AlertCircle className="w-6 h-6 text-primary-600" />
        <h2 className="text-xl font-bold text-gray-800">Incident Analysis</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="text-sm font-medium text-gray-600 mb-1 block">Severity</label>
          <SeverityBadge severity={analysis.severity} showDescription />
        </div>
        
        <div>
          <label className="text-sm font-medium text-gray-600 mb-1 block">Incident Type</label>
          <div className="flex items-center gap-2">
            <span className="text-2xl">{typeConfig.icon}</span>
            <span className={`text-lg font-semibold ${typeConfig.color}`}>
              {typeConfig.label}
            </span>
          </div>
        </div>
      </div>
      
      <div className="space-y-4">
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h3 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Summary
          </h3>
          <p className="text-gray-700">{analysis.summary}</p>
        </div>
        
        {analysis.key_symptoms && analysis.key_symptoms.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-700 mb-2">Key Symptoms</h3>
            <ul className="space-y-1">
              {analysis.key_symptoms.map((symptom, index) => (
                <li key={index} className="flex items-start gap-2 text-gray-700">
                  <span className="text-danger-500 mt-1">•</span>
                  <span>{symptom}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {analysis.affected_systems && analysis.affected_systems.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Server className="w-4 h-4" />
              Affected Systems
            </h3>
            <div className="flex flex-wrap gap-2">
              {analysis.affected_systems.map((system, index) => (
                <span
                  key={index}
                  className="badge bg-gray-100 text-gray-700 border border-gray-300"
                >
                  {system}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {analysis.technical_terms && analysis.technical_terms.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Tag className="w-4 h-4" />
              Technical Terms
            </h3>
            <div className="flex flex-wrap gap-2">
              {analysis.technical_terms.map((term, index) => (
                <span
                  key={index}
                  className="badge bg-primary-50 text-primary-700 border border-primary-200 font-mono text-xs"
                >
                  {term}
                </span>
              ))}
            </div>
          </div>
        )}
        
        <div className="flex items-center gap-2 text-sm">
          <span className="font-medium text-gray-600">Urgency Score:</span>
          <div className="flex items-center gap-1">
            {[...Array(10)].map((_, i) => (
              <div
                key={i}
                className={`w-2 h-6 rounded ${
                  i < analysis.urgency_score ? 'bg-danger-500' : 'bg-gray-200'
                }`}
              />
            ))}
            <span className="ml-2 font-semibold text-danger-600">
              {analysis.urgency_score}/10
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentAnalysis;