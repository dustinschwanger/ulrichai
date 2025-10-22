/// <reference types="react-scripts" />

// Google Analytics global types
interface Window {
  gtag?: (
    command: string,
    targetId: string | Date,
    config?: Record<string, any>
  ) => void;
  dataLayer?: any[];
}
