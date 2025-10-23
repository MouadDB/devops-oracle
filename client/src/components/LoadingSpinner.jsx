import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ message = 'Processing...', steps = [] }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
      <p className="text-lg font-medium text-gray-700">{message}</p>
      
      {steps.length > 0 && (
        <div className="w-full max-w-md space-y-2">
          {steps.map((step, index) => (
            <div
              key={index}
              className="flex items-center space-x-3 text-sm text-gray-600 animate-fade-in"
            >
              <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
              <span>{step}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;