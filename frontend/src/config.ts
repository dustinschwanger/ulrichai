// Configuration for different environments

interface Config {
  API_BASE_URL: string;
  ENVIRONMENT: string;
}

const getConfig = (): Config => {
  // Check if we're in development mode
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  // Use environment variable if provided, otherwise fallback to defaults
  const API_BASE_URL = process.env.REACT_APP_API_URL || 
    (isDevelopment ? 'http://localhost:8000' : window.location.origin.replace(':3000', ':8000'));

  return {
    API_BASE_URL,
    ENVIRONMENT: process.env.NODE_ENV || 'development'
  };
};

export const config = getConfig();
export default config;