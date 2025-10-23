import React from 'react';
import { getSeverityConfig } from '../utils/helpers';

const SeverityBadge = ({ severity, showDescription = false }) => {
  const config = getSeverityConfig(severity);
  
  return (
    <div className="inline-flex flex-col">
      <span className={`badge border ${config.color} inline-flex items-center gap-1`}>
        <span>{config.icon}</span>
        <span>{config.label}</span>
      </span>
      {showDescription && (
        <span className="text-xs text-gray-500 mt-1">{config.description}</span>
      )}
    </div>
  );
};

export default SeverityBadge;