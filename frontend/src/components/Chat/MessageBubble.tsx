import React, { useState } from 'react';
import {
  Box,
  Avatar,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  Chip,
  Stack,
  Fade,
  Collapse,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import toast from 'react-hot-toast';
import { SourceCards } from './SourceCards';

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
  start_time?: number;
  end_time?: number;
  duration?: number;
  timestamp_display?: string;
  content_type?: string;
}

interface MessageBubbleProps {
  message: {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: Date;
    isStreaming?: boolean;
    sources?: Source[];
  };
  onRegenerateRequest?: () => void;
  onFeedback?: (messageId: string, feedback: 'up' | 'down') => void;
  onSourceClick?: (source: Source) => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onRegenerateRequest,
  onFeedback,
  onSourceClick,
}) => {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const isUser = message.role === 'user';

  // Debug logging for sources
  if (!isUser && message.sources) {
    console.log('MessageBubble - Sources received:', message.sources);
    console.log('MessageBubble - Number of sources:', message.sources.length);
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFeedback = (type: 'up' | 'down') => {
    setFeedback(type);
    if (onFeedback) {
      onFeedback(message.id, type);
    }
    toast.success(`Thanks for your feedback!`);
  };

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: 'numeric',
      hour12: true,
    }).format(date);
  };

  return (
    <Fade in timeout={300}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 3,
          px: { xs: 1, sm: 2 },
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: isUser ? 'row-reverse' : 'row',
            gap: 1.5,
            maxWidth: '85%',
            width: { xs: '100%', md: 'auto' },
          }}
        >
          {/* Avatar */}
          <Avatar
            sx={{
              bgcolor: isUser ? 'primary.main' : 'secondary.main',
              width: 36,
              height: 36,
              flexShrink: 0,
            }}
          >
            {isUser ? <PersonIcon /> : <BotIcon />}
          </Avatar>

          {/* Message Content */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            {/* Header */}
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{ mb: 0.5 }}
            >
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  color: 'text.primary',
                }}
              >
                {isUser ? 'You' : 'RBL AI'}
              </Typography>
              <Typography
                variant="caption"
                sx={{ color: 'text.secondary' }}
              >
                {formatTime(message.timestamp)}
              </Typography>
              {message.isStreaming && (
                <Chip
                  label="Typing..."
                  size="small"
                  color="primary"
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              )}
            </Stack>

            {/* Message Box */}
            <Paper
              elevation={isUser ? 2 : 1}
              sx={{
                p: 2,
                borderRadius: 2,
                backgroundColor: isUser
                  ? 'primary.main'
                  : 'background.paper',
                color: isUser ? 'primary.contrastText' : 'text.primary',
                border: !isUser ? '1px solid' : 'none',
                borderColor: 'divider',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Message Content with Markdown */}
              <Box
                sx={{
                  '& p': { margin: 0, mb: 1.5 },
                  '& p:last-child': { mb: 0 },
                  '& ul, & ol': { mt: 1, mb: 1, pl: 3 },
                  '& li': { mb: 0.5 },
                  '& code': {
                    backgroundColor: isUser
                      ? 'rgba(255,255,255,0.2)'
                      : 'rgba(0,0,0,0.05)',
                    padding: '2px 6px',
                    borderRadius: 1,
                    fontSize: '0.875rem',
                    fontFamily: 'monospace',
                  },
                  '& pre': {
                    margin: 0,
                    borderRadius: 1,
                    overflow: 'auto',
                    maxWidth: '100%',
                  },
                  '& blockquote': {
                    borderLeft: '4px solid',
                    borderColor: isUser ? 'rgba(255,255,255,0.3)' : 'primary.main',
                    pl: 2,
                    ml: 0,
                    my: 1,
                  },
                }}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, inline, className, children, ...props }: any) {
                      const match = /language-(\w+)/.exec(className || '');
                      if (!inline && match) {
                        return (
                          <Box sx={{ position: 'relative', my: 1 }}>
                            <Box
                              sx={{
                                position: 'absolute',
                                right: 8,
                                top: 8,
                                zIndex: 1,
                              }}
                            >
                              <Tooltip title="Copy code">
                                <IconButton
                                  size="small"
                                  onClick={() => {
                                    navigator.clipboard.writeText(String(children));
                                    toast.success('Code copied!');
                                  }}
                                  sx={{
                                    color: 'white',
                                    backgroundColor: 'rgba(0,0,0,0.3)',
                                    '&:hover': {
                                      backgroundColor: 'rgba(0,0,0,0.5)',
                                    },
                                  }}
                                >
                                  <CopyIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                            <SyntaxHighlighter
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                              customStyle={{
                                margin: 0,
                                borderRadius: 8,
                                fontSize: '0.875rem',
                              }}
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          </Box>
                        );
                      }
                      return (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </Box>

              {/* Streaming indicator */}
              {message.isStreaming && (
                <Box
                  sx={{
                    display: 'flex',
                    gap: 0.5,
                    mt: 1,
                  }}
                >
                  {[0, 1, 2].map((i) => (
                    <Box
                      key={i}
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: isUser
                          ? 'rgba(255,255,255,0.5)'
                          : 'primary.main',
                        animation: 'pulse 1.4s infinite',
                        animationDelay: `${i * 0.2}s`,
                        '@keyframes pulse': {
                          '0%, 60%, 100%': {
                            opacity: 0.3,
                          },
                          '30%': {
                            opacity: 1,
                          },
                        },
                      }}
                    />
                  ))}
                </Box>
              )}
            </Paper>

            {/* Source Cards */}
            {(() => {
              console.log('MessageBubble - Checking source display conditions:');
              console.log('  - isUser:', isUser);
              console.log('  - message.sources:', message.sources);
              console.log('  - message.sources.length:', message.sources ? message.sources.length : 0);
              console.log('  - Will show sources:', !isUser && message.sources && message.sources.length > 0);

              return !isUser && message.sources && message.sources.length > 0 && (
                <SourceCards
                  sources={message.sources}
                  onSourceClick={onSourceClick}
                />
              );
            })()}

            {/* Action Buttons */}
            {!isUser && !message.isStreaming && (
              <Stack
                direction="row"
                spacing={0.5}
                sx={{ mt: 1 }}
              >
                <Tooltip title="Copy message">
                  <IconButton
                    size="small"
                    onClick={handleCopy}
                    sx={{ color: 'text.secondary' }}
                  >
                    {copied ? (
                      <CheckIcon fontSize="small" color="success" />
                    ) : (
                      <CopyIcon fontSize="small" />
                    )}
                  </IconButton>
                </Tooltip>

                <Tooltip title="Good response">
                  <IconButton
                    size="small"
                    onClick={() => handleFeedback('up')}
                    sx={{
                      color: feedback === 'up' ? 'success.main' : 'text.secondary',
                    }}
                  >
                    <ThumbUpIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Bad response">
                  <IconButton
                    size="small"
                    onClick={() => handleFeedback('down')}
                    sx={{
                      color: feedback === 'down' ? 'error.main' : 'text.secondary',
                    }}
                  >
                    <ThumbDownIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

                {onRegenerateRequest && (
                  <Tooltip title="Regenerate response">
                    <IconButton
                      size="small"
                      onClick={onRegenerateRequest}
                      sx={{ color: 'text.secondary' }}
                    >
                      <RefreshIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Stack>
            )}
          </Box>
        </Box>
      </Box>
    </Fade>
  );
};

export default MessageBubble;