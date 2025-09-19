import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Stack,
  Paper,
  Typography,
  Button,
  TextField,
  IconButton,
  Divider,
  Chip,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Psychology,
  Quiz,
  Code,
  Lightbulb,
  School,
  AutoAwesome,
  Business,
} from '@mui/icons-material';
import { config } from '../../../config';
import toast from 'react-hot-toast';

interface LessonChatProps {
  courseTitle: string;
  lessonTitle: string;
  lessonType?: string;
  moduleTitle?: string;
  learningObjectives?: string[];
  currentContent?: string;
}

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isStreaming?: boolean;
}

const LessonChat: React.FC<LessonChatProps> = ({
  courseTitle,
  lessonTitle,
  lessonType = 'lesson',
  moduleTitle,
  learningObjectives = [],
  currentContent = '',
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [hasInitialized, setHasInitialized] = useState(false);

  // Format markdown content to HTML
  const formatMessageContent = (content: string): string => {
    let formatted = content;

    // Convert headers (###, ##, #)
    formatted = formatted.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Convert bold text
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert italic text
    formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Convert bullet points (lines starting with - or *)
    formatted = formatted.replace(/^[\*\-] (.+)$/gm, '<li>$1</li>');

    // Wrap consecutive <li> elements in <ul>
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
      return '<ul>' + match + '</ul>';
    });

    // Convert numbered lists
    formatted = formatted.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

    // Convert code blocks
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Convert line breaks to paragraphs (but not within lists)
    const lines = formatted.split('\n');
    const formattedLines = [];
    let inList = false;

    for (let line of lines) {
      if (line.includes('<ul>') || line.includes('<ol>')) {
        inList = true;
      }
      if (line.includes('</ul>') || line.includes('</ol>')) {
        inList = false;
      }

      if (!inList && line.trim() && !line.includes('<h') && !line.includes('</h') && !line.includes('<ul') && !line.includes('<ol') && !line.includes('<li')) {
        formattedLines.push(`<p>${line}</p>`);
      } else {
        formattedLines.push(line);
      }
    }

    formatted = formattedLines.join('\n');

    return formatted;
  };

  // Generate context-aware suggested questions based on lesson
  const getSuggestedQuestions = () => {
    const baseQuestions = [
      `Can you explain the key concepts in "${lessonTitle}"?`,
      `What are real-world applications of what I'm learning?`,
      `Can you give me a practice problem to test my understanding?`,
    ];

    // Add lesson-type specific questions
    if (lessonType === 'video') {
      baseQuestions.push('Can you summarize the main points from this video?');
    } else if (lessonType === 'quiz') {
      baseQuestions.push('Can you help me understand why my answer might be wrong?');
    } else if (lessonType === 'code') {
      baseQuestions.push('Can you walk me through this code example step by step?');
    }

    return baseQuestions;
  };

  const scrollToBottom = () => {
    // Only scroll within the chat container, not the entire page
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  useEffect(() => {
    // Only auto-scroll for new user messages or when a bot message completes
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && (lastMessage.role === 'user' || !lastMessage.isStreaming)) {
      scrollToBottom();
    }
  }, [messages]);

  // Initialize with a context-aware greeting
  useEffect(() => {
    if (!hasInitialized) {
      const welcomeMessage: Message = {
        id: `msg-welcome-${Date.now()}`,
        content: `Hi! I'm Ulrich AI, your personal tutor for **${lessonTitle}** in the ${courseTitle} course.

I'm here to help you understand the concepts, answer questions, and provide examples. I have context about what you're learning, so feel free to ask me anything about this lesson!

${learningObjectives.length > 0 ? `**Learning Objectives for this lesson:**\n${learningObjectives.map(obj => `• ${obj}`).join('\n')}` : ''}

What would you like to know?`,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
      setHasInitialized(true);
    }
  }, [hasInitialized, courseTitle, lessonTitle, learningObjectives]);

  const buildContextPrompt = (userQuery: string) => {
    // Build a context-rich prompt that includes lesson information
    let contextPrompt = `You are an AI tutor helping a student with a specific lesson. Here's the context:

**Course:** ${courseTitle}
**Current Lesson:** ${lessonTitle}
**Module:** ${moduleTitle || 'N/A'}
**Lesson Type:** ${lessonType}

${learningObjectives.length > 0 ? `**Learning Objectives:**\n${learningObjectives.map(obj => `- ${obj}`).join('\n')}` : ''}

${currentContent ? `**Current Content Summary:** ${currentContent.substring(0, 500)}...` : ''}

**Student's Question:** ${userQuery}

Please provide a helpful, educational response that:
1. Directly addresses the student's question
2. Relates to the current lesson context
3. Uses examples when helpful
4. Encourages deeper understanding
5. Stays focused on the learning objectives

Remember you are a tutor for this specific lesson, so keep your responses relevant to the course material.`;

    return contextPrompt;
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: `msg-${Date.now()}-user`,
      content: message,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Add assistant message with streaming indicator
    const assistantMessageId = `msg-${Date.now()}-assistant`;
    const streamingMessage: Message = {
      id: assistantMessageId,
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, streamingMessage]);

    try {
      // Build context-aware prompt
      const contextualQuery = buildContextPrompt(message);

      const response = await fetch(`${config.API_BASE_URL}/api/chat/query/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: contextualQuery,
          session_id: `lesson-${lessonTitle.replace(/\s+/g, '-')}-${Date.now()}`,
          context: {
            type: 'lesson',
            course: courseTitle,
            lesson: lessonTitle,
            module: moduleTitle,
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Read the stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body reader available');
      }

      let accumulatedContent = '';
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === 'content') {
                accumulatedContent += data.content;
                // Update message with accumulated content
                setMessages(prev => prev.map(msg =>
                  msg.id === assistantMessageId
                    ? {
                        ...msg,
                        content: accumulatedContent,
                        isStreaming: true,
                      }
                    : msg
                ));
              } else if (data.type === 'done') {
                // Mark streaming as complete
                setMessages(prev => prev.map(msg =>
                  msg.id === assistantMessageId
                    ? {
                        ...msg,
                        isStreaming: false,
                      }
                    : msg
                ));
              } else if (data.type === 'error') {
                throw new Error(data.error);
              }
            } catch (e) {
              if (line.trim()) {
                console.debug('Skipping unparseable line:', line);
              }
            }
          }
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get response. Please try again.');

      // Remove the streaming message on error
      setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    const quickActions: Record<string, string> = {
      explain: `Can you explain the main concept of "${lessonTitle}" in simple terms?`,
      example: `Can you give me a practical example of how "${lessonTitle}" is used in real life?`,
      quiz: `Can you quiz me on the key points from "${lessonTitle}"?`,
      apply: `How can I apply the concepts from "${lessonTitle}" to my specific role or company? Please ask me about my role/company first if needed, then provide tailored suggestions.`,
      difficult: `What's the most challenging part of "${lessonTitle}" and how can I master it?`,
    };

    const message = quickActions[action];
    if (message) {
      handleSendMessage(message);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    handleSendMessage(question);
  };

  return (
    <Box sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <SmartToy color="primary" />
          <Typography variant="h6">Ulrich AI</Typography>
          <Chip
            label={`${courseTitle}`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
        <Typography variant="caption" color="text.secondary">
          Context-aware help for: {lessonTitle}
        </Typography>
      </Box>

      {/* Quick Actions */}
      <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
        <Stack direction="row" spacing={1} sx={{ overflowX: 'auto', pb: 1 }}>
          <Button
            size="small"
            startIcon={<Lightbulb />}
            onClick={() => handleQuickAction('explain')}
            variant="outlined"
          >
            Explain
          </Button>
          <Button
            size="small"
            startIcon={<Psychology />}
            onClick={() => handleQuickAction('example')}
            variant="outlined"
          >
            Example
          </Button>
          <Button
            size="small"
            startIcon={<Quiz />}
            onClick={() => handleQuickAction('quiz')}
            variant="outlined"
          >
            Quiz Me
          </Button>
          <Button
            size="small"
            startIcon={<Business />}
            onClick={() => handleQuickAction('apply')}
            variant="outlined"
          >
            Apply
          </Button>
          <Button
            size="small"
            startIcon={<School />}
            onClick={() => handleQuickAction('difficult')}
            variant="outlined"
          >
            Challenges
          </Button>
        </Stack>
      </Box>

      {/* Messages Area */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
        <Stack spacing={2}>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
              }}
            >
              <Paper
                sx={{
                  p: 2,
                  bgcolor: message.role === 'user'
                    ? 'primary.light'
                    : 'background.paper',
                  color: message.role === 'user'
                    ? 'primary.contrastText'
                    : 'text.primary',
                }}
              >
                {message.isStreaming && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CircularProgress size={12} />
                    <Typography variant="caption">Thinking...</Typography>
                  </Box>
                )}
                <Typography
                  component="div"
                  variant="body2"
                  sx={{
                    '& h1': { fontSize: '1.5rem', fontWeight: 600, mt: 2, mb: 1 },
                    '& h2': { fontSize: '1.25rem', fontWeight: 600, mt: 2, mb: 1 },
                    '& h3': { fontSize: '1.1rem', fontWeight: 600, mt: 1.5, mb: 1 },
                    '& h4': { fontSize: '1rem', fontWeight: 600, mt: 1, mb: 0.5 },
                    '& p': { mb: 1 },
                    '& ul': { pl: 3, mb: 1 },
                    '& ol': { pl: 3, mb: 1 },
                    '& li': { mb: 0.5 },
                    '& strong': { fontWeight: 600 },
                    '& em': { fontStyle: 'italic' },
                    '& code': {
                      backgroundColor: 'action.hover',
                      padding: '2px 4px',
                      borderRadius: 1,
                      fontFamily: 'monospace',
                    },
                    '& pre': {
                      backgroundColor: 'action.hover',
                      padding: 2,
                      borderRadius: 1,
                      overflowX: 'auto',
                    },
                    '& blockquote': {
                      borderLeft: '4px solid',
                      borderColor: 'primary.main',
                      pl: 2,
                      ml: 0,
                      color: 'text.secondary',
                    }
                  }}
                  dangerouslySetInnerHTML={{
                    __html: formatMessageContent(message.content)
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 1,
                    opacity: 0.7
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Paper>
            </Box>
          ))}

          {/* Suggested Questions - Show when no messages or after welcome */}
          {messages.length <= 1 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1 }}>
                Suggested questions:
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                {getSuggestedQuestions().slice(0, 3).map((question, index) => (
                  <Button
                    key={index}
                    variant="outlined"
                    size="small"
                    onClick={() => handleSuggestedQuestion(question)}
                    sx={{
                      justifyContent: 'flex-start',
                      textAlign: 'left',
                      textTransform: 'none',
                    }}
                  >
                    {question}
                  </Button>
                ))}
              </Stack>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Stack>
      </Box>

      {/* Input Area */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder={`Ask about ${lessonTitle}...`}
            variant="outlined"
            size="small"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(input);
              }
            }}
            multiline
            maxRows={3}
            disabled={isLoading}
          />
          <IconButton
            color="primary"
            onClick={() => handleSendMessage(input)}
            disabled={!input.trim() || isLoading}
          >
            <Send />
          </IconButton>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Ulrich AI has context about this lesson and can help explain concepts
        </Typography>
      </Box>
    </Box>
  );
};

export default LessonChat;