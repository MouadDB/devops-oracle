import React from 'react';
import { Search, ExternalLink, Clock, TrendingUp } from 'lucide-react';
import { formatTimeAgo, getSeverityConfig, getIncidentTypeConfig } from '../utils/helpers';

const SearchResults = ({ results }) => {
  if (!results || results.length === 0) {
    return (
      <div className="card text-center py-8">
        <Search className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-500">No similar incidents found</p>
      </div>
    );
  }
  
  return (
    <div className="card animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <Search className="w-6 h-6 text-primary-600" />
        <h2 className="text-xl font-bold text-gray-800">Similar Past Incidents</h2>
        <span className="badge bg-primary-100 text-primary-700">
          {results.length} found
        </span>
      </div>
      
      <div className="space-y-4">
        {results.map((result, index) => {
          const severityConfig = getSeverityConfig(result.severity);
          const typeConfig = getIncidentTypeConfig(result.incident_type);
          const similarityPercentage = Math.round(result.similarity_score * 10);
          
          return (
            <div
              key={result.incident_id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-white"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-gray-500 text-sm font-mono">
                      {result.incident_id}
                    </span>
                    <span className={`badge border ${severityConfig.color}`}>
                      {result.severity}
                    </span>
                    <span className="text-sm text-gray-500 flex items-center gap-1">
                      {typeConfig.icon} {typeConfig.label}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    {result.title}
                  </h3>
                </div>
                
                <div className="text-right ml-4">
                  <div className="flex items-center gap-1 text-sm font-semibold text-primary-600 mb-1">
                    <TrendingUp className="w-4 h-4" />
                    {similarityPercentage}% match
                  </div>
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatTimeAgo(result.created_at)}
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {result.description}
              </p>
              
              {result.highlights && Object.keys(result.highlights).length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
                  <p className="text-xs font-medium text-yellow-800 mb-1">Matched content:</p>
                  <div className="text-xs text-gray-700 space-y-1">
                    {Object.entries(result.highlights).map(([field, snippets]) => (
                      <div key={field}>
                        {snippets.map((snippet, i) => (
                          <div
                            key={i}
                            dangerouslySetInnerHTML={{ __html: snippet }}
                            className="[&_mark]:bg-yellow-300 [&_mark]:px-1"
                          />
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    Resolved in {result.resolution_time_minutes} min
                  </span>
                </div>
                
                <button className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1">
                  View Details
                  <ExternalLink className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SearchResults;