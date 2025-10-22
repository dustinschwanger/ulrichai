import React, { useState, useEffect, useRef, useCallback } from 'react';
import { X, ZoomIn, ZoomOut, Download, ChevronUp, ChevronDown, Minimize2, Maximize2 } from 'lucide-react';
import { Document, Page } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import './DocumentViewer.css';
import { config } from '../config';

// Configure PDF.js worker using require for better compatibility
const pdfjs = require('pdfjs-dist');
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';


interface DocumentViewerProps {
  filename: string;
  pageNumber?: number;
  title: string;
  url?: string;
  allowDownload?: boolean;
  onClose: () => void;
  bucket?: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  filename,
  pageNumber = 1,
  title,
  url,
  allowDownload = false,
  onClose,
  bucket = 'documents'
}) => {
  const [zoom, setZoom] = useState(100);
  const [numPages, setNumPages] = useState<number>(0);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string>('');
  const [containerWidth, setContainerWidth] = useState<number>(800);
  const [isMinimized, setIsMinimized] = useState(false);
  const [currentVisiblePage, setCurrentVisiblePage] = useState(pageNumber || 1);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const pageRefs = useRef<{ [key: number]: HTMLDivElement }>({});

  // Debug logging
  console.log('DocumentViewer received:', { 
    filename, 
    pageNumber, 
    currentVisiblePage,
    url 
  });

  useEffect(() => {
    // Calculate container width for responsive sizing
    const updateWidth = () => {
      const container = document.querySelector('.document-content');
      if (container) {
        setContainerWidth(container.clientWidth - 40); // Subtract padding
      }
    };
    
    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  useEffect(() => {
    // Set the PDF URL
    if (url) {
      // If URL is relative, prepend the API base URL
      const fullUrl = url.startsWith('http') ? url : `${config.API_BASE_URL}${url}`;
      setPdfUrl(fullUrl);
    } else {
      fetchDocumentUrl();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, filename]);

  useEffect(() => {
    // Scroll to target page when pageNumber prop changes
    if (pageNumber && pageNumber > 0 && numPages > 0) {
      console.log('Scrolling to page:', pageNumber);
      scrollToPage(pageNumber);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageNumber, numPages]);

  // Intersection Observer to track visible pages
  useEffect(() => {
    if (!numPages || numPages === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const pageNum = parseInt(entry.target.getAttribute('data-page') || '1');
          if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
            setCurrentVisiblePage(pageNum);
          }
        });
      },
      { threshold: 0.5, rootMargin: '-50px 0px -50px 0px' }
    );

    Object.values(pageRefs.current).forEach((ref) => {
      if (ref) observer.observe(ref);
    });

    return () => observer.disconnect();
  }, [numPages]);

  const fetchDocumentUrl = async () => {
    try {
      // Use direct PDF serving endpoint instead of Supabase signed URL
      const directUrl = `${config.API_BASE_URL}/api/documents/${encodeURIComponent(filename)}`;
      setPdfUrl(directUrl);
    } catch (error) {
      console.error('Error setting document URL:', error);
      setError('Error loading document');
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 25, 50));
  };

  const handleDownload = async () => {
    if (!allowDownload) {
      alert('Download is not permitted for this document');
      return;
    }

    try {
      // Use the Supabase signed URL for downloads
      const response = await fetch(`${config.API_BASE_URL}/api/ingestion/documents/${encodeURIComponent(filename)}/download?bucket=${bucket}`);
      if (response.ok) {
        const data = await response.json();
        window.open(data.url, '_blank');
      } else {
        // Fallback to direct PDF endpoint
        window.open(`${config.API_BASE_URL}/api/documents/${encodeURIComponent(filename)}?bucket=${bucket}`, '_blank');
      }
    } catch (error) {
      console.error('Download error:', error);
      window.open(`${config.API_BASE_URL}/api/documents/${encodeURIComponent(filename)}?bucket=${bucket}`, '_blank');
    }
  };

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    console.log('PDF loaded successfully. Pages:', numPages, 'Target page:', pageNumber);
    setNumPages(numPages);
    setLoading(false);
    setError(null);
    // Scroll to target page after a short delay to ensure pages are rendered
    setTimeout(() => {
      if (pageNumber && pageNumber > 0) {
        scrollToPage(pageNumber);
      }
    }, 100);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('PDF load error:', error);
    setError('Failed to load PDF document');
    setLoading(false);
  };

  const scrollToPage = useCallback((targetPage: number) => {
    const pageElement = pageRefs.current[targetPage];
    if (pageElement && scrollContainerRef.current) {
      pageElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start',
        inline: 'nearest'
      });
    }
  }, []);

  const goToPreviousPage = () => {
    const newPage = Math.max(1, currentVisiblePage - 1);
    scrollToPage(newPage);
  };

  const goToNextPage = () => {
    const newPage = Math.min(numPages, currentVisiblePage + 1);
    scrollToPage(newPage);
  };

  const handlePageInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const page = parseInt(e.target.value);
    if (!isNaN(page) && page >= 1 && page <= numPages) {
      scrollToPage(page);
    }
  };


  return (
    <div className={`document-viewer ${isMinimized ? 'minimized' : ''}`}>
      <div className="document-header">
        <div className="document-title">
          <h3>{title}</h3>
        </div>
        <div className="document-controls">
          {/* Page Navigation */}
          {numPages > 0 && (
            <>
              <input
                type="number"
                min="1"
                max={numPages}
                value={currentVisiblePage}
                onChange={handlePageInputChange}
                className="page-input compact"
                title={`Page ${currentVisiblePage} of ${numPages}`}
              />
              <button
                className="control-button"
                onClick={goToPreviousPage}
                disabled={currentVisiblePage <= 1}
                title="Previous Page"
              >
                <ChevronUp size={14} />
              </button>
              <button
                className="control-button"
                onClick={goToNextPage}
                disabled={currentVisiblePage >= numPages}
                title="Next Page"
              >
                <ChevronDown size={14} />
              </button>
            </>
          )}
          
          {/* Zoom Controls */}
          <button
            className="control-button"
            onClick={handleZoomOut}
            title="Zoom Out"
            disabled={zoom <= 50}
          >
            <ZoomOut size={14} />
          </button>
          <button
            className="control-button"
            onClick={handleZoomIn}
            title="Zoom In"
            disabled={zoom >= 200}
          >
            <ZoomIn size={14} />
          </button>
          
          {/* Panel & Download Controls */}
          <button
            className="control-button"
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? "Expand Panel" : "Minimize Panel"}
          >
            {isMinimized ? <Maximize2 size={14} /> : <Minimize2 size={14} />}
          </button>
          
          {allowDownload && (
            <button
              className="control-button download-button"
              onClick={handleDownload}
              title="Download Document"
            >
              <Download size={14} />
            </button>
          )}
          <button
            className="control-button close-button"
            onClick={onClose}
            title="Close Document"
          >
            <X size={16} />
          </button>
        </div>
      </div>
      
      {!isMinimized && (
        <div className="document-content" ref={scrollContainerRef}>
          {error && (
            <div className="document-error">
              <p>{error}</p>
              <button onClick={() => window.location.reload()}>Retry</button>
            </div>
          )}
          
          {pdfUrl && !error && (
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="document-loading">
                  <div className="loading-spinner"></div>
                  <p>Loading document{pageNumber && pageNumber > 1 ? ` (Target: Page ${pageNumber})` : ''}...</p>
                </div>
              }
              className="pdf-document"
            >
              {/* Render all pages for scrollable view */}
              {Array.from({ length: numPages }, (_, index) => {
                const pageNum = index + 1;
                return (
                  <div
                    key={`page_container_${pageNum}`}
                    ref={(el) => {
                      if (el) pageRefs.current[pageNum] = el;
                    }}
                    data-page={pageNum}
                    className={`page-container ${pageNum === currentVisiblePage ? 'visible' : ''}`}
                  >
                    <div className="page-number-label">
                      Page {pageNum}
                    </div>
                    <Page
                      key={`page_${pageNum}`}
                      pageNumber={pageNum}
                      width={containerWidth * (zoom / 100)}
                      renderTextLayer={true}
                      renderAnnotationLayer={true}
                      loading={
                        <div className="page-loading">
                          <div className="loading-spinner"></div>
                          <p>Loading page {pageNum}...</p>
                        </div>
                      }
                    />
                  </div>
                );
              })}
            </Document>
          )}
        </div>
      )}
      
      {isMinimized && (
        <div className="minimized-content">
          <p>📄 {title}</p>
          <small>Click expand to view document</small>
        </div>
      )}
    </div>
  );
};

export default DocumentViewer;