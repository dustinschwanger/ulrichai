import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Stack,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Description as DocumentIcon,
  VideoLibrary as VideoIcon,
  OpenInNew as OpenIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

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

interface SourceCardsProps {
  sources: Source[];
  onSourceClick?: (source: Source) => void;
}

const MotionPaper = motion(Paper);

export const SourceCards: React.FC<SourceCardsProps> = ({ sources, onSourceClick }) => {
  // Debug logging
  console.log('SourceCards component - sources prop:', sources);
  console.log('SourceCards - sources length:', sources ? sources.length : 'sources is null/undefined');

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

  const handleCopyContent = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('Source content copied!');
  };

  if (!sources || sources.length === 0) {
    console.log('SourceCards - returning null because no sources');
    return null;
  }

  return (
    <Box sx={{ mt: 2, mb: 1, overflow: 'visible' }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
        <Typography variant="subtitle2" fontWeight={600} color="text.secondary">
          📚 Sources
        </Typography>
        <Chip
          label={`${sources.length} reference${sources.length > 1 ? 's' : ''}`}
          size="small"
          variant="outlined"
        />
      </Stack>

      <Box
        sx={{
          display: 'flex',
          gap: 2,
          overflowX: 'auto',
          overflowY: 'visible',
          py: 1,    // Add vertical padding for lift effect
          px: 0.5,  // Add horizontal padding for border space
          my: -1,   // Compensate with negative margin
          mx: -0.5, // Compensate with negative margin
          '&::-webkit-scrollbar': {
            height: 8,
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'action.hover',
            borderRadius: 4,
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'action.disabled',
            borderRadius: 4,
            '&:hover': {
              backgroundColor: 'action.selected',
            },
          },
        }}
      >
        {sources.map((source, idx) => {
          const isVideo = source.content_type === 'video' ||
                         (source.start_time !== undefined && source.start_time !== null);

          return (
            <MotionPaper
              key={idx}
              elevation={0}
              whileHover={{ y: -4 }}
              whileTap={{ scale: 0.98 }}
              sx={{
                p: 2,
                minWidth: 280,
                maxWidth: 320,
                cursor: onSourceClick ? 'pointer' : 'default',
                border: '2px solid',
                borderColor: 'divider',
                borderRadius: 2,
                backgroundColor: 'background.paper',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.main',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                },
              }}
              onClick={() => onSourceClick && onSourceClick(source)}
            >
              {/* Header */}
              <Stack direction="row" spacing={1} alignItems="flex-start" sx={{ mb: 1.5 }}>
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: 1,
                    backgroundColor: isVideo ? 'error.light' : '#19A9FF20',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  {isVideo ? (
                    <VideoIcon sx={{ fontSize: 18, color: 'error.dark' }} />
                  ) : (
                    <DocumentIcon sx={{ fontSize: 18, color: 'primary.dark' }} />
                  )}
                </Box>
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography
                    variant="subtitle2"
                    fontWeight={600}
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      lineHeight: 1.3,
                    }}
                  >
                    {source.title}
                  </Typography>
                  {source.section && source.section !== "Document Summary" && (
                    <Typography variant="caption" color="text.secondary">
                      {source.section}
                    </Typography>
                  )}
                </Box>
              </Stack>

              {/* Content Preview */}
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  mb: 1.5,
                  lineHeight: 1.5,
                  fontSize: '0.875rem',
                }}
              >
                {source.content}
              </Typography>

              {/* Footer */}
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Stack direction="row" spacing={1} alignItems="center">
                  {source.page_number && (
                    <Chip
                      label={`Page ${source.page_number}`}
                      size="small"
                      variant="outlined"
                      sx={{ height: 24, fontSize: '0.75rem' }}
                    />
                  )}
                  {source.start_time !== undefined && source.start_time !== null && (
                    <Chip
                      label={formatTimestamp(source.start_time)}
                      size="small"
                      variant="outlined"
                      color="error"
                      sx={{ height: 24, fontSize: '0.75rem' }}
                    />
                  )}
                  <Chip
                    label={`${Math.round(source.score * 100)}%`}
                    size="small"
                    color="primary"
                    sx={{ height: 24, fontSize: '0.75rem' }}
                  />
                </Stack>

                <Stack direction="row" spacing={0.5}>
                  <Tooltip title="Copy content">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCopyContent(source.content);
                      }}
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  {onSourceClick && (
                    <Tooltip title="Open source">
                      <IconButton size="small">
                        <OpenIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Stack>
              </Stack>
            </MotionPaper>
          );
        })}
      </Box>
    </Box>
  );
};

export default SourceCards;