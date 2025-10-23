export const getSeverityConfig = (severity) => {
  const configs = {
    P0: {
      label: 'P0 - Critical',
      color: 'bg-danger-100 text-danger-700 border-danger-300',
      icon: '🔥',
      description: 'System down, immediate action required'
    },
    P1: {
      label: 'P1 - High',
      color: 'bg-warning-100 text-warning-700 border-warning-300',
      icon: '⚠️',
      description: 'Major functionality impaired'
    },
    P2: {
      label: 'P2 - Medium',
      color: 'bg-primary-100 text-primary-700 border-primary-300',
      icon: '📋',
      description: 'Minor functionality affected'
    },
    P3: {
      label: 'P3 - Low',
      color: 'bg-gray-100 text-gray-700 border-gray-300',
      icon: '📝',
      description: 'Minimal impact'
    }
  };
  return configs[severity] || configs.P3;
};

export const getIncidentTypeConfig = (type) => {
  const configs = {
    database: { label: 'Database', icon: '🗄️', color: 'text-blue-600' },
    network: { label: 'Network', icon: '🌐', color: 'text-green-600' },
    application: { label: 'Application', icon: '💻', color: 'text-purple-600' },
    infrastructure: { label: 'Infrastructure', icon: '🏗️', color: 'text-orange-600' },
    security: { label: 'Security', icon: '🔒', color: 'text-red-600' }
  };
  return configs[type] || { label: type, icon: '📦', color: 'text-gray-600' };
};

export const formatTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);
  
  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60
  };
  
  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secondsInUnit);
    if (interval >= 1) {
      return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
    }
  }
  
  return 'just now';
};

export const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'text-success-600';
  if (score >= 0.6) return 'text-primary-600';
  if (score >= 0.4) return 'text-warning-600';
  return 'text-danger-600';
};

export const getConfidenceLabel = (score) => {
  if (score >= 0.8) return 'High Confidence';
  if (score >= 0.6) return 'Medium Confidence';
  if (score >= 0.4) return 'Low-Medium Confidence';
  return 'Low Confidence';
};

export const highlightText = (text, highlights) => {
  if (!text || !highlights || highlights.length === 0) return text;
  
  // highlights already contain <mark> tags from Elasticsearch
  return text;
};