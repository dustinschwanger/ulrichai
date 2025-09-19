import React, { useState, useRef, useEffect } from 'react';
import { Send, GripVertical } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import Sidebar from './Sidebar';
import DocumentViewer from './DocumentViewer';
import VideoViewer from './VideoViewer';
import { config } from '../config';
import './Chat.css';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  sources?: Source[];
}

interface Source {
  title: string;
  filename: string;
  content: string;
  score: number;
  chunk_id?: string;
  page_number?: number;
  section?: string;
  document_id?: string;
  type?: string;
  fileUrl?: string;
  // Video-specific fields
  start_time?: number;
  end_time?: number;
  duration?: number;
  timestamp_display?: string;
  content_type?: string;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  timestamp: Date;
}

interface ActiveDocument {
  filename: string;
  title: string;
  url?: string;
  pageNumber?: number;
  allowDownload?: boolean;
  // Video-specific fields
  contentType?: string;
  startTime?: number;
}

const Chat: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeDocument, setActiveDocument] = useState<ActiveDocument | null>(null);

  // Helper function to format seconds into readable timestamp
  const formatTimestamp = (seconds: number | undefined): string => {
    if (typeof seconds !== 'number') return '';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
  };
  const [splitPosition, setSplitPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const currentSession = sessions.find(s => s.id === currentSessionId);
  const messages = React.useMemo(() => {
    return currentSession?.messages || [];
  }, [currentSession]);

  useEffect(() => {
    if (sessions.length === 0) {
      createNewChat();
    }
  }, [sessions.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;
      
      const containerRect = containerRef.current.getBoundingClientRect();
      const containerWidth = containerRect.width - 260;
      const mouseX = e.clientX - 260;
      const percentage = (mouseX / containerWidth) * 100;
      
      const newPosition = Math.min(Math.max(percentage, 30), 70);
      setSplitPosition(newPosition);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };

    if (isDragging) {
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const createNewChat = () => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: 'New chat',
      messages: [],
      timestamp: new Date(),
    };
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
    setActiveDocument(null);
  };

  const selectChat = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setActiveDocument(null);
  };

  const updateSessionTitle = (sessionId: string, firstMessage: string) => {
    setSessions(prev => prev.map(session => 
      session.id === sessionId 
        ? { ...session, title: firstMessage.slice(0, 50) + (firstMessage.length > 50 ? '...' : '') }
        : session
    ));
  };

  const handleSourceClick = async (source: Source) => {
    console.log('Source clicked:', {
      filename: source.filename,
      page_number: source.page_number,
      fullSource: source
    });

    try {
      // First check permissions
      const permResponse = await fetch(`${config.API_BASE_URL}/api/ingestion/documents/${encodeURIComponent(source.filename)}/permissions`);
      const permissions = await permResponse.json();
      
      if (!permissions.showInViewer) {
        alert('This document is not available for viewing');
        return;
      }
      
      // Get the document URL from Supabase
      let documentUrl = source.fileUrl;
      
      if (!documentUrl) {
        // If no fileUrl in source, fetch it from backend
        try {
          const urlResponse = await fetch(`${config.API_BASE_URL}/api/ingestion/documents/${encodeURIComponent(source.filename)}/download`);
          if (urlResponse.ok) {
            const urlData = await urlResponse.json();
            documentUrl = urlData.url;
          }
        } catch (error) {
          console.error('Error getting document URL:', error);
        }
      }
      
      if (!documentUrl) {
        // Final fallback - query the documents endpoint to get the fileUrl
        try {
          const docsResponse = await fetch(`${config.API_BASE_URL}/api/ingestion/documents?limit=100`);
          const docsData = await docsResponse.json();
          const doc = docsData.documents.find((d: any) => d.filename === source.filename);
          if (doc && doc.fileUrl) {
            documentUrl = doc.fileUrl;
          }
        } catch (error) {
          console.error('Error fetching documents list:', error);
        }
      }
      
      if (!documentUrl) {
        alert('Unable to load document URL');
        return;
      }
      
      // Determine content type (video vs document)
      const isVideo = source.content_type === 'video' || 
                     (source.start_time !== undefined && source.start_time !== null) ||
                     /\.(mp4|webm|mov|avi|mkv)$/i.test(source.filename);
      
      if (isVideo) {
        console.log('Setting active video with start time:', source.start_time);
        
        setActiveDocument({
          filename: source.filename,
          title: source.title,
          url: documentUrl,
          allowDownload: permissions.allowDownload,
          contentType: 'video',
          startTime: source.start_time || 0
        });
      } else {
        const pageToNavigate = source.page_number || 1;
        console.log('Setting active document with page:', pageToNavigate);
        
        setActiveDocument({
          filename: source.filename,
          title: source.title,
          url: documentUrl,
          pageNumber: pageToNavigate,
          allowDownload: permissions.allowDownload,
          contentType: 'document'
        });
      }
      setSplitPosition(50);
    } catch (error) {
      console.error('Error checking permissions:', error);
      alert('Unable to open document');
    }
  };

  const handleCloseDocument = () => {
    setActiveDocument(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      content: input,
      role: 'user',
      timestamp: new Date(),
    };

    setSessions(prev => prev.map(session => 
      session.id === currentSessionId
        ? { ...session, messages: [...session.messages, userMessage] }
        : session
    ));

    if (messages.length === 0) {
      updateSessionTitle(currentSessionId, input);
    }

    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          session_id: currentSessionId,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant-${Math.random().toString(36).substr(2, 9)}`,
        content: data.answer,
        role: 'assistant',
        timestamp: new Date(),
        sources: data.sources,
      };

      setSessions(prev => prev.map(session => 
        session.id === currentSessionId
          ? { ...session, messages: [...session.messages, assistantMessage] }
          : session
      ));
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error-${Math.random().toString(36).substr(2, 9)}`,
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setSessions(prev => prev.map(session => 
        session.id === currentSessionId
          ? { ...session, messages: [...session.messages, errorMessage] }
          : session
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className={`chat-container ${activeDocument ? 'document-open' : ''}`} ref={containerRef}>
      <Sidebar
        currentChatId={currentSessionId}
        chats={sessions}
        onNewChat={createNewChat}
        onSelectChat={selectChat}
      />
      
      <div 
        className="chat-main" 
        style={activeDocument ? { width: `${splitPosition}%` } : {}}
      >
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-hero">
                <h2>Welcome to Ulrich AI</h2>
              </div>
              <p className="welcome-subtitle">
                Your intelligent partner for HR and organizational development insights
              </p>
              <div className="suggested-questions">
                <button onClick={() => setInput('What are the key organizational trends shaping the future of work?')}>
                  What are the key organizational trends shaping the future of work?
                </button>
                <button onClick={() => setInput('How do you build a customer-focused culture in an organization?')}>
                  How do you build a customer-focused culture in an organization?
                </button>
                <button onClick={() => setInput('What is the strategic role of HR in organizational development?')}>
                  What is the strategic role of HR in organizational development?
                </button>
                <button onClick={() => setInput('How can leaders drive meaningful organizational change?')}>
                  How can leaders drive meaningful organizational change?
                </button>
              </div>
            </div>
          ) : (
            <div className="messages-list">
              {messages.map((message) => (
                <div key={message.id} className={`message message-${message.role}`}>
                  <div className="message-wrapper">
                    <div className="message-content">
                      {message.role === 'assistant' ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        message.content
                      )}
                    </div>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="source-cards">
                        <div className="source-cards-title">
                          📚 Sources
                        </div>
                        <div className="source-cards-container">
                          <div className="source-cards-scroll">
                            {message.sources.map((source, idx) => (
                              <div 
                                key={idx} 
                                className="source-card"
                                onClick={() => handleSourceClick(source)}
                                title={`Click to view ${source.title}`}
                              >
                                <div className="source-title">{source.title}</div>
                                {source.section && source.section !== "Document Summary" && (
                                  <div className="source-section">{source.section}</div>
                                )}
                                <div className="source-preview">{source.content}</div>
                                <div className="source-metadata">
                                  {source.page_number && (
                                    <span className="source-page">Page {source.page_number}</span>
                                  )}
                                  {source.start_time !== undefined && (
                                    <span className="source-page">{formatTimestamp(source.start_time)}</span>
                                  )}
                                  <div className="source-score">
                                    Relevance: {(source.score * 100).toFixed(0)}%
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="message message-assistant">
                  <div className="loading-indicator">
                    <div className="loading-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span>Thinking...</span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about HR, leadership, or organizational development..."
              className="chat-input"
              disabled={isLoading}
              rows={1}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!input.trim() || isLoading}
            >
              <Send size={20} />
            </button>
          </div>
          <div className="input-hint">
            Press Enter to send, Shift+Enter for new line
          </div>
        </form>
      </div>
      
      {activeDocument && (
        <>
          <div 
            className="resize-handle"
            onMouseDown={() => setIsDragging(true)}
            title="Drag to resize"
          >
            <GripVertical size={20} />
          </div>
          <div 
            className="document-panel"
            style={{ width: `${100 - splitPosition}%` }}
          >
            {activeDocument.contentType === 'video' ? (
              <VideoViewer
                filename={activeDocument.filename}
                title={activeDocument.title}
                url={activeDocument.url}
                startTime={activeDocument.startTime}
                allowDownload={activeDocument.allowDownload}
                onClose={handleCloseDocument}
              />
            ) : (
              <DocumentViewer
                filename={activeDocument.filename}
                title={activeDocument.title}
                url={activeDocument.url}
                pageNumber={activeDocument.pageNumber}
                allowDownload={activeDocument.allowDownload}
                onClose={handleCloseDocument}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Chat;