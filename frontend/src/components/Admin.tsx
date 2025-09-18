import React, { useState, useEffect, useCallback } from 'react';
import { Upload, FileText, X, Search, Download, Eye } from 'lucide-react';
import { config } from '../config';
import './Admin.css';

interface DocumentMetadata {
  displayName: string;
  documentType: string;
  documentSource: string;
  humanCapabilityDomain: string;
  author: string;
  publicationDate: string;
  description: string;
  allowDownload: boolean;
  showInViewer: boolean;
}

interface ChunkingConfig {
  chunkSize: number;
  chunkOverlap: number;
  sectionHeaders: string[];
  keepTablesIntact: boolean;
  keepListsIntact: boolean;
}

interface Document {
  id: string;
  filename: string;
  displayName: string;
  documentType: string;
  documentSource: string;
  humanCapabilityDomain: string;
  author: string;
  publicationDate: string;
  description: string;
  allowDownload: boolean;
  showInViewer: boolean;
  uploadDate: string;
  fileUrl?: string;
}

const Admin: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [metadata, setMetadata] = useState<DocumentMetadata>({
    displayName: '',
    documentType: 'article',
    documentSource: 'institute',
    humanCapabilityDomain: 'hr',
    author: '',
    publicationDate: '',
    description: '',
    allowDownload: true,
    showInViewer: true
  });
  const [chunkingConfig, setChunkingConfig] = useState<ChunkingConfig>({
    chunkSize: 3000,  // Larger chunks for better RAG performance
    chunkOverlap: 200,
    sectionHeaders: ['Chapter', 'Section', 'Part'],
    keepTablesIntact: true,
    keepListsIntact: true
  });
  const [isUploading, setIsUploading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSource, setFilterSource] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        page: '1',
        limit: '50'
      });
      
      if (searchTerm) {
        params.append('search', searchTerm);
      }
      if (filterSource !== 'all') {
        params.append('source', filterSource);
      }
      if (filterType !== 'all') {
        params.append('doc_type', filterType);
      }
      
      console.log('Fetching documents from:', `${config.API_BASE_URL}/api/ingestion/documents?${params}`);
      
      const response = await fetch(`${config.API_BASE_URL}/api/ingestion/documents?${params}`);
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.error) {
        setError(data.error);
        console.error('API returned error:', data.error);
      }
      
      setDocuments(data.documents || []);
      
      if (data.documents && data.documents.length > 0) {
        console.log(`Loaded ${data.documents.length} documents`);
      } else {
        console.log('No documents found');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError(`Failed to fetch documents: ${error}`);
      setDocuments([]);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, filterSource, filterType]);

  // Initial load and refetch when filters change
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchDocuments();
    }, 500); // Debounce search

    return () => clearTimeout(timer);
  }, [fetchDocuments]);

  const handleViewDocument = async (doc: Document) => {
    if (doc.fileUrl) {
      // Open document in new tab
      window.open(doc.fileUrl, '_blank');
    } else if (doc.filename) {
      // Fallback: try to get a signed URL
      try {
        const response = await fetch(`${config.API_BASE_URL}/api/ingestion/documents/${encodeURIComponent(doc.filename)}/download`);
        if (response.ok) {
          const data = await response.json();
          window.open(data.url, '_blank');
        }
      } catch (error) {
        console.error('Error getting document URL:', error);
        alert('Failed to open document');
      }
    }
  };

  const handleDownloadDocument = async (doc: Document) => {
    if (!doc.allowDownload) {
      alert('Download is not permitted for this document');
      return;
    }

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/ingestion/documents/${encodeURIComponent(doc.filename)}/download`);
      if (response.ok) {
        const data = await response.json();
        // Create a temporary link to trigger download
        const link = document.createElement('a');
        link.href = data.url;
        link.download = doc.displayName + '.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        alert('Failed to download document');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download document');
    }
  };

  const handleDeleteDocument = async (filename: string, displayName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${displayName}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/ingestion/documents/${encodeURIComponent(filename)}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        alert('Document deleted successfully');
        fetchDocuments();
      } else {
        const error = await response.text();
        alert(`Failed to delete document: ${error}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert(`Failed to delete document: ${error}`);
    }
  };

  const isVideoFile = (filename: string): boolean => {
    return /\.(mp4|webm|mov|avi|mkv)$/i.test(filename);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Check file size (1.5 GB limit)
      const MAX_FILE_SIZE = 1610612736; // 1.5 GB in bytes
      if (file.size > MAX_FILE_SIZE) {
        const sizeMB = Math.round(file.size / (1024 * 1024));
        const limitGB = MAX_FILE_SIZE / (1024 * 1024 * 1024);
        alert(`File is too large (${sizeMB} MB). Maximum allowed size is ${limitGB} GB.`);
        e.target.value = ''; // Clear the input
        return;
      }
      
      setSelectedFile(file);
      if (!metadata.displayName) {
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
        setMetadata(prev => ({
          ...prev,
          displayName: nameWithoutExt.replace(/[_-]/g, ' '),
          documentType: isVideoFile(file.name) ? 'video' : 'article'
        }));
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !metadata.displayName) {
      alert('Please select a file and provide a display name');
      return;
    }

    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('metadata', JSON.stringify(metadata));
    formData.append('chunking_config', JSON.stringify(chunkingConfig));

    try {
      console.log('Uploading document with metadata:', metadata);
      
      const response = await fetch(`${config.API_BASE_URL}/api/ingestion/upload-with-config`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Upload successful:', result);
        alert('Document uploaded successfully!');
        
        // Reset form
        setSelectedFile(null);
        setMetadata({
          displayName: '',
          documentType: 'article',
          documentSource: 'institute',
          humanCapabilityDomain: 'hr',
          author: '',
          publicationDate: '',
          description: '',
          allowDownload: true,
          showInViewer: true
        });
        
        // Refresh document list
        fetchDocuments();
      } else {
        const error = await response.text();
        console.error('Upload failed:', error);
        
        // Provide specific feedback for file size errors
        if (response.status === 413) {
          alert('File is too large. Please select a file smaller than 1.5 GB.');
        } else {
          alert(`Upload failed: ${error}`);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error}`);
    } finally {
      setIsUploading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Content Admin</h1>
        <p>Upload and configure documents and videos for the knowledge base</p>
      </div>

      <div className="admin-content">
        <div className="upload-section">
          <h2>Upload Content</h2>
          <div className="upload-area">
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx,.pptx,.mp4,.webm,.mov,.avi,.mkv"
              onChange={handleFileSelect}
              hidden
            />
            <label htmlFor="file-upload" className="upload-label">
              <Upload size={48} />
              <p>Click to select a file</p>
              <span>Documents: PDF, DOCX, PPTX | Videos: MP4, WEBM, MOV, AVI, MKV (Max: 1.5 GB)</span>
            </label>
            {selectedFile && (
              <div className="selected-file">
                <FileText size={20} />
                <span>{selectedFile.name}</span>
                <span className="file-size">({formatFileSize(selectedFile.size)})</span>
                <button 
                  onClick={() => setSelectedFile(null)}
                  className="remove-file"
                >
                  <X size={16} />
                </button>
              </div>
            )}
          </div>
        </div>

        {selectedFile && (
          <>
            <div className="metadata-section">
              <h2>Content Information</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="displayName">Display Name *</label>
                  <input
                    type="text"
                    id="displayName"
                    value={metadata.displayName}
                    onChange={(e) => setMetadata(prev => ({
                      ...prev,
                      displayName: e.target.value
                    }))}
                    placeholder="e.g., HR Effectiveness Guide or Leadership Workshop Video"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="documentSource">Document Source *</label>
                  <select
                    id="documentSource"
                    value={metadata.documentSource}
                    onChange={(e) => setMetadata(prev => ({
                      ...prev,
                      documentSource: e.target.value
                    }))}
                  >
                    <option value="institute">Institute</option>
                    <option value="dave-ulrich-hr-academy">Dave Ulrich HR Academy</option>
                    <option value="hr-development">HR Development</option>
                    <option value="hr-excellence">Leading for HR Excellence</option>
                    <option value="leadership-code-academy">Leadership Code Academy</option>
                    <option value="leadership-development">Leadership Development</option>
                    <option value="reinventing-organization">Reinventing the Organization</option>
                    <option value="talent-academy">Talent Academy</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="documentType">Document Type *</label>
                  <select
                    id="documentType"
                    value={metadata.documentType}
                    onChange={(e) => setMetadata(prev => ({
                      ...prev,
                      documentType: e.target.value
                    }))}
                  >
                    <option value="article">Article</option>
                    <option value="case-study">Case Study</option>
                    <option value="playbook">Playbook</option>
                    <option value="powerpoint">PowerPoint Deck</option>
                    <option value="tool">Tool</option>
                    <option value="toolkit">Toolkit</option>
                    <option value="video">Video</option>
                    <option value="whitepaper">Whitepaper</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="humanCapabilityDomain">Human Capability Domain *</label>
                  <select
                    id="humanCapabilityDomain"
                    value={metadata.humanCapabilityDomain}
                    onChange={(e) => setMetadata(prev => ({
                      ...prev,
                      humanCapabilityDomain: e.target.value
                    }))}
                  >
                    <option value="hr">HR</option>
                    <option value="talent">Talent</option>
                    <option value="leadership">Leadership</option>
                    <option value="organization">Organization</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="author">Author</label>
                  <input
                    type="text"
                    id="author"
                    value={metadata.author}
                    onChange={(e) => setMetadata(prev => ({
                      ...prev,
                      author: e.target.value
                    }))}
                    placeholder="e.g., Dave Ulrich"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="publicationDate">Publication Date</label>
                  <input
                    type="date"
                    id="publicationDate"
                    value={metadata.publicationDate}
                    onChange={(e) => setMetadata(prev => ({
                      ...prev,
                      publicationDate: e.target.value
                    }))}
                  />
                </div>

                <div className="form-group full-width">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    value={metadata.description}
                    onChange={(e) => setMetadata(prev => ({
                      ...prev,
                      description: e.target.value
                    }))}
                    placeholder="Brief description of the document content..."
                    rows={3}
                  />
                </div>

                <div className="form-group full-width">
                  <label>Access Permissions</label>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={metadata.allowDownload}
                        onChange={(e) => setMetadata(prev => ({
                          ...prev,
                          allowDownload: e.target.checked
                        }))}
                      />
                      <span>Allow users to download this document</span>
                    </label>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={metadata.showInViewer}
                        onChange={(e) => setMetadata(prev => ({
                          ...prev,
                          showInViewer: e.target.checked
                        }))}
                      />
                      <span>Show document in viewer (uncheck for AI training only)</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {selectedFile && !isVideoFile(selectedFile.name) && (
            <div className="chunking-section">
              <h2>Chunking Configuration</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="chunkSize">Chunk Size (characters)</label>
                  <input
                    type="number"
                    id="chunkSize"
                    value={chunkingConfig.chunkSize}
                    onChange={(e) => setChunkingConfig(prev => ({
                      ...prev,
                      chunkSize: parseInt(e.target.value) || 3000
                    }))}
                    min="500"
                    max="4000"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="chunkOverlap">Chunk Overlap (characters)</label>
                  <input
                    type="number"
                    id="chunkOverlap"
                    value={chunkingConfig.chunkOverlap}
                    onChange={(e) => setChunkingConfig(prev => ({
                      ...prev,
                      chunkOverlap: parseInt(e.target.value) || 200
                    }))}
                    min="0"
                    max="500"
                  />
                </div>

                <div className="form-group full-width">
                  <label>Preserve Structure</label>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={chunkingConfig.keepTablesIntact}
                        onChange={(e) => setChunkingConfig(prev => ({
                          ...prev,
                          keepTablesIntact: e.target.checked
                        }))}
                      />
                      <span>Keep tables intact</span>
                    </label>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={chunkingConfig.keepListsIntact}
                        onChange={(e) => setChunkingConfig(prev => ({
                          ...prev,
                          keepListsIntact: e.target.checked
                        }))}
                      />
                      <span>Keep lists intact</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            )}

            {selectedFile && isVideoFile(selectedFile.name) && (
              <div className="video-info-section" style={{ 
                background: '#f0f8ff', 
                padding: '16px', 
                borderRadius: '8px', 
                border: '1px solid #e0e8f0',
                margin: '16px 0' 
              }}>
                <h3 style={{ margin: '0 0 8px 0', color: '#0066cc' }}>Video Processing Information</h3>
                <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                  Videos will be automatically transcribed using OpenAI Whisper and chunked with timestamps. 
                  The chunking configuration above does not apply to videos. Processing may take several minutes 
                  depending on video length.
                </p>
              </div>
            )}

            <div className="action-section">
              <button
                className="upload-button"
                onClick={handleUpload}
                disabled={!metadata.displayName || isUploading}
              >
                {isUploading ? 'Processing...' : 'Upload & Process Content'}
              </button>
            </div>
          </>
        )}
      </div>

      <div className="documents-list-section">
        <div className="documents-header">
          <h2>Content Library</h2>
          <div className="documents-controls">
            <div className="search-box">
              <Search size={18} />
              <input
                type="text"
                placeholder="Search content..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select
              value={filterSource}
              onChange={(e) => setFilterSource(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Sources</option>
              <option value="institute">Institute</option>
              <option value="dave-ulrich-hr-academy">Dave Ulrich HR Academy</option>
              <option value="hr-development">HR Development</option>
              <option value="hr-excellence">Leading for HR Excellence</option>
              <option value="leadership-code-academy">Leadership Code Academy</option>
              <option value="leadership-development">Leadership Development</option>
              <option value="reinventing-organization">Reinventing the Organization</option>
              <option value="talent-academy">Talent Academy</option>
            </select>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Types</option>
              <option value="article">Article</option>
              <option value="case-study">Case Study</option>
              <option value="playbook">Playbook</option>
              <option value="powerpoint">PowerPoint Deck</option>
              <option value="tool">Tool</option>
              <option value="toolkit">Toolkit</option>
              <option value="video">Video</option>
              <option value="whitepaper">Whitepaper</option>
            </select>
          </div>
        </div>
        
        {error && (
          <div style={{
            padding: '10px',
            background: '#fee',
            color: '#c00',
            margin: '10px 0',
            borderRadius: '4px'
          }}>
            Error: {error}
          </div>
        )}
        
        <div className="documents-table">
          <table>
            <thead>
              <tr>
                <th>Display Name</th>
                <th>Source</th>
                <th>Type</th>
                <th>Domain</th>
                <th>Author</th>
                <th>Date</th>
                <th>Permissions</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="no-documents">
                    Loading content...
                  </td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan={8} className="no-documents">
                    No content found
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>{doc.displayName}</td>
                    <td>{doc.documentSource}</td>
                    <td>{doc.documentType}</td>
                    <td>{doc.humanCapabilityDomain}</td>
                    <td>{doc.author || '-'}</td>
                    <td>{formatDate(doc.publicationDate)}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '5px', fontSize: '12px' }}>
                        {doc.showInViewer && <span title="Visible in viewer">👁️</span>}
                        {doc.allowDownload && <span title="Downloadable">⬇️</span>}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button 
                          className="action-button"
                          onClick={() => handleViewDocument(doc)}
                          title="View document"
                        >
                          <Eye size={14} />
                        </button>
                        {doc.allowDownload && (
                          <button 
                            className="action-button"
                            onClick={() => handleDownloadDocument(doc)}
                            title="Download document"
                          >
                            <Download size={14} />
                          </button>
                        )}
                        <button 
                          className="action-button delete-button"
                          onClick={() => handleDeleteDocument(doc.filename, doc.displayName)}
                          title="Delete document"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Admin;