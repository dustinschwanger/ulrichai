import React, { useState, useRef, KeyboardEvent } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Stack,
  Tooltip,
  CircularProgress,
  Typography,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Fade,
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachIcon,
  Mic as MicIcon,
  Stop as StopIcon,
  Add as AddIcon,
  Code as CodeIcon,
  School as SchoolIcon,
  Psychology as PsychologyIcon,
  Calculate as CalculateIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onFileUpload?: (file: File) => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

const MotionBox = motion(Box);

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onFileUpload,
  isLoading = false,
  disabled = false,
  placeholder = "Ask anything... Type '@' for agents or '/' for commands",
}) => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [showAgentHint, setShowAgentHint] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textFieldRef = useRef<HTMLInputElement>(null);

  const agentSuggestions = [
    { icon: <PsychologyIcon />, name: 'General Assistant', trigger: '@general' },
    { icon: <CodeIcon />, name: 'Code Expert', trigger: '@code' },
    { icon: <SchoolIcon />, name: 'Study Buddy', trigger: '@study' },
    { icon: <CalculateIcon />, name: 'Math Tutor', trigger: '@math' },
  ];

  const handleSend = () => {
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message);
      setMessage('');
      setShowAgentHint(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setMessage(value);

    // Show agent hint when @ is typed
    setShowAgentHint(value.includes('@') && !value.includes(' '));
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAgentSelect = (trigger: string) => {
    setMessage(trigger + ' ');
    setShowAgentHint(false);
    handleMenuClose();
    textFieldRef.current?.focus();
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Voice recording logic would go here
  };

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Agent Hint */}
      <Fade in={showAgentHint}>
        <Paper
          sx={{
            position: 'absolute',
            bottom: '100%',
            left: 0,
            right: 0,
            mb: 1,
            p: 1.5,
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography variant="caption" color="text.secondary" gutterBottom>
            Available Agents:
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
            {agentSuggestions.map((agent) => (
              <Chip
                key={agent.trigger}
                icon={agent.icon}
                label={agent.name}
                size="small"
                onClick={() => handleAgentSelect(agent.trigger)}
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Stack>
        </Paper>
      </Fade>

      <Paper
        elevation={0}
        sx={{
          p: 2.5,
          borderRadius: 3,
          backgroundColor: 'background.paper',
          border: '2px solid',
          borderColor: 'divider',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:focus-within': {
            borderColor: 'primary.main',
            boxShadow: '0 8px 24px rgba(0, 134, 214, 0.15)',
          },
        }}
      >
        <Stack spacing={2}>
          {/* Main Input Area */}
          <Stack direction="row" spacing={1} alignItems="flex-end">
            {/* Plus Menu */}
            <Tooltip title="More options">
              <IconButton
                size="small"
                onClick={handleMenuOpen}
                disabled={disabled}
                sx={{ color: 'text.secondary' }}
              >
                <AddIcon />
              </IconButton>
            </Tooltip>

            {/* Text Input */}
            <TextField
              ref={textFieldRef}
              fullWidth
              multiline
              maxRows={4}
              value={message}
              onChange={handleMessageChange}
              onKeyPress={handleKeyPress}
              placeholder={placeholder}
              disabled={disabled || isLoading}
              variant="standard"
              InputProps={{
                disableUnderline: true,
                sx: {
                  fontSize: '0.95rem',
                  px: 1,
                },
              }}
              sx={{
                '& .MuiInput-root': {
                  backgroundColor: 'action.hover',
                  borderRadius: 2,
                  px: 1.5,
                  py: 1,
                  transition: 'background-color 0.2s',
                  '&:hover': {
                    backgroundColor: 'action.selected',
                  },
                  '&.Mui-focused': {
                    backgroundColor: 'action.selected',
                  },
                },
              }}
            />

            {/* Action Buttons */}
            <Stack direction="row" spacing={0.5}>
              {/* File Upload */}
              <input
                ref={fileInputRef}
                type="file"
                hidden
                onChange={handleFileSelect}
              />
              <Tooltip title="Attach file">
                <IconButton
                  size="small"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={disabled || isLoading}
                  sx={{ color: 'text.secondary' }}
                >
                  <AttachIcon />
                </IconButton>
              </Tooltip>

              {/* Voice Input */}
              <Tooltip title={isRecording ? "Stop recording" : "Voice input"}>
                <IconButton
                  size="small"
                  onClick={toggleRecording}
                  disabled={disabled || isLoading}
                  sx={{
                    color: isRecording ? 'error.main' : 'text.secondary',
                  }}
                >
                  {isRecording ? <StopIcon /> : <MicIcon />}
                </IconButton>
              </Tooltip>

              {/* Send Button */}
              <MotionBox
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <IconButton
                  onClick={handleSend}
                  disabled={!message.trim() || isLoading || disabled}
                  sx={{
                    background: 'linear-gradient(135deg, #0086D6 0%, #19A9FF 100%)',
                    color: 'white',
                    width: 44,
                    height: 44,
                    boxShadow: '0 4px 14px rgba(0, 134, 214, 0.3)',
                    transition: 'all 0.3s',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #071D49 0%, #0086D6 100%)',
                      boxShadow: '0 8px 20px rgba(0, 134, 214, 0.4)',
                    },
                    '&.Mui-disabled': {
                      backgroundColor: 'action.disabledBackground',
                      boxShadow: 'none',
                    },
                  }}
                >
                  {isLoading ? (
                    <CircularProgress size={20} sx={{ color: 'white' }} />
                  ) : (
                    <SendIcon sx={{ fontSize: 20 }} />
                  )}
                </IconButton>
              </MotionBox>
            </Stack>
          </Stack>

          {/* Character Count & Shortcuts */}
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Stack direction="row" spacing={2}>
              <Typography variant="caption" color="text.secondary">
                {message.length}/4000
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Press Enter to send • Shift+Enter for new line
              </Typography>
            </Stack>
            {isRecording && (
              <Chip
                label="Recording..."
                size="small"
                color="error"
                sx={{
                  animation: 'pulse 1.5s infinite',
                  '@keyframes pulse': {
                    '0%': { opacity: 1 },
                    '50%': { opacity: 0.5 },
                    '100%': { opacity: 1 },
                  },
                }}
              />
            )}
          </Stack>
        </Stack>

        {/* Options Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'left',
          }}
          transformOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
        >
          {agentSuggestions.map((agent) => (
            <MenuItem
              key={agent.trigger}
              onClick={() => handleAgentSelect(agent.trigger)}
            >
              <ListItemIcon>{agent.icon}</ListItemIcon>
              <ListItemText
                primary={agent.name}
                secondary={agent.trigger}
              />
            </MenuItem>
          ))}
        </Menu>
      </Paper>
    </Box>
  );
};

export default ChatInput;