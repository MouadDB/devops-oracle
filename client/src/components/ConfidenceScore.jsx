import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { getConfidenceColor, getConfidenceLabel } from '../utils/helpers';

const ConfidenceScore = ({ score, reasoning }) => {
  const percentage = Math.round(score * 100);
  const color = getConfidenceColor(score);
  const label = getConfidenceLabel(score);
  
  const Icon = score >= 0.7 ? TrendingUp : score >= 0.4 ? Minus : TrendingDown;
  
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Icon className={`w-5 h-5 ${color}`} />
          <h3 className="text-lg font-semibold text-gray-800">Confidence Score</h3>
        </div>
        <span className={`text-2xl font-bold ${color}`}>
          {percentage}%
        </span>
      </div>
      
      <div className="mb-3">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600">{label}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ${
              score >= 0.8 ? 'bg-success-500' :
              score >= 0.6 ? 'bg-primary-500' :
              score >= 0.4 ? 'bg-warning-500' :
              'bg-danger-500'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
      
      {reasoning && (
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Reasoning:</span> {reasoning}
          </p>
        </div>
      )}
    </div>
  );
};

export default ConfidenceScore;