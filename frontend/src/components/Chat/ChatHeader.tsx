import React, { useState } from 'react';
import {
  Box,
  Stack,
  Typography,
  IconButton,
  Tooltip,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Badge,
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  DeleteOutline as DeleteIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  BookmarkBorder as BookmarkIcon,
  RestartAlt as RestartIcon,
  SmartToy as BotIcon,
  Psychology as PsychologyIcon,
  Code as CodeIcon,
  School as SchoolIcon,
  Calculate as CalculateIcon,
} from '@mui/icons-material';

interface ChatHeaderProps {
  conversationTitle?: string;
  activeAgent?: string;
  messageCount?: number;
  onClearChat?: () => void;
  onExportChat?: () => void;
  onShareChat?: () => void;
  onSaveChat?: () => void;
  onNewChat?: () => void;
  onAgentChange?: (agent: string) => void;
}

const agents = [
  { id: 'general', name: 'General Assistant', icon: <PsychologyIcon />, color: 'primary' },
  { id: 'code', name: 'Code Expert', icon: <CodeIcon />, color: 'secondary' },
  { id: 'study', name: 'Study Buddy', icon: <SchoolIcon />, color: 'info' },
  { id: 'math', name: 'Math Tutor', icon: <CalculateIcon />, color: 'warning' },
];

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  conversationTitle = 'New Conversation',
  activeAgent = 'general',
  messageCount = 0,
  onClearChat,
  onExportChat,
  onShareChat,
  onSaveChat,
  onNewChat,
  onAgentChange,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [agentMenuAnchor, setAgentMenuAnchor] = useState<null | HTMLElement>(null);

  const currentAgent = agents.find(a => a.id === activeAgent) || agents[0];

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAgentMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAgentMenuAnchor(event.currentTarget);
  };

  const handleAgentMenuClose = () => {
    setAgentMenuAnchor(null);
  };

  const handleAgentSelect = (agentId: string) => {
    if (onAgentChange) {
      onAgentChange(agentId);
    }
    handleAgentMenuClose();
  };

  return (
    <Box
      sx={{
        px: 3,
        py: 2,
        backgroundColor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}
    >
      <Stack direction="row" alignItems="center" justifyContent="space-between">
        {/* Left Section */}
        <Stack direction="row" spacing={2} alignItems="center">
          {/* Agent Selector */}
          <Tooltip title="Change agent">
            <Chip
              avatar={
                <Avatar sx={{ bgcolor: `${currentAgent.color}.main` }}>
                  {currentAgent.icon}
                </Avatar>
              }
              label={currentAgent.name}
              onClick={handleAgentMenuOpen}
              variant="outlined"
              sx={{
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            />
          </Tooltip>

          {/* Conversation Info */}
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              {conversationTitle}
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Badge color="success" variant="dot" sx={{ '& .MuiBadge-dot': { right: -3, top: 3 } }}>
                <BotIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              </Badge>
              <Typography variant="caption" color="text.secondary">
                {currentAgent.name} is active • {messageCount} messages
              </Typography>
            </Stack>
          </Box>
        </Stack>

        {/* Right Section */}
        <Stack direction="row" spacing={1}>
          {/* Quick Actions */}
          <Tooltip title="New chat">
            <IconButton onClick={onNewChat} size="small">
              <RestartIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Save conversation">
            <IconButton onClick={onSaveChat} size="small">
              <BookmarkIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Share">
            <IconButton onClick={onShareChat} size="small">
              <ShareIcon />
            </IconButton>
          </Tooltip>

          {/* More Options */}
          <Tooltip title="More options">
            <IconButton onClick={handleMenuOpen} size="small">
              <MoreIcon />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>

      {/* Agent Selection Menu */}
      <Menu
        anchorEl={agentMenuAnchor}
        open={Boolean(agentMenuAnchor)}
        onClose={handleAgentMenuClose}
        PaperProps={{
          sx: { width: 250 },
        }}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle2" color="text.secondary">
            Select an Agent
          </Typography>
        </Box>
        <Divider />
        {agents.map((agent) => (
          <MenuItem
            key={agent.id}
            onClick={() => handleAgentSelect(agent.id)}
            selected={agent.id === activeAgent}
          >
            <ListItemIcon>
              <Avatar
                sx={{
                  width: 28,
                  height: 28,
                  bgcolor: `${agent.color}.main`,
                }}
              >
                {agent.icon}
              </Avatar>
            </ListItemIcon>
            <ListItemText
              primary={agent.name}
              primaryTypographyProps={{ fontSize: '0.9rem' }}
            />
            {agent.id === activeAgent && (
              <Chip label="Active" size="small" color="primary" />
            )}
          </MenuItem>
        ))}
      </Menu>

      {/* Options Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: { width: 200 },
        }}
      >
        <MenuItem
          onClick={() => {
            onExportChat?.();
            handleMenuClose();
          }}
        >
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Chat</ListItemText>
        </MenuItem>

        <MenuItem
          onClick={() => {
            onShareChat?.();
            handleMenuClose();
          }}
        >
          <ListItemIcon>
            <ShareIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Share</ListItemText>
        </MenuItem>

        <MenuItem
          onClick={() => {
            onSaveChat?.();
            handleMenuClose();
          }}
        >
          <ListItemIcon>
            <BookmarkIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Save</ListItemText>
        </MenuItem>

        <Divider />

        <MenuItem
          onClick={() => {
            onClearChat?.();
            handleMenuClose();
          }}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Clear Chat</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ChatHeader;