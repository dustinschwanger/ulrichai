import React from 'react';
import {
  Box,
  CircularProgress,
  LinearProgress,
  Typography,
  Skeleton,
  Stack,
} from '@mui/material';
import { motion } from 'framer-motion';

interface LoadingProps {
  variant?: 'circular' | 'linear' | 'skeleton' | 'dots' | 'pulse';
  size?: 'small' | 'medium' | 'large';
  text?: string;
  fullScreen?: boolean;
  color?: 'primary' | 'secondary' | 'inherit';
}

const MotionBox = motion(Box);

export const Loading: React.FC<LoadingProps> = ({
  variant = 'circular',
  size = 'medium',
  text,
  fullScreen = false,
  color = 'primary',
}) => {
  const getSizeValue = () => {
    switch (size) {
      case 'small':
        return 24;
      case 'large':
        return 60;
      default:
        return 40;
    }
  };

  const renderLoadingContent = () => {
    switch (variant) {
      case 'linear':
        return (
          <Box sx={{ width: '100%', maxWidth: 400 }}>
            <LinearProgress color={color} />
            {text && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
                {text}
              </Typography>
            )}
          </Box>
        );

      case 'skeleton':
        return (
          <Stack spacing={2} sx={{ width: '100%', maxWidth: 600 }}>
            <Skeleton variant="text" sx={{ fontSize: '2rem' }} />
            <Skeleton variant="rectangular" height={60} />
            <Skeleton variant="rectangular" height={200} />
          </Stack>
        );

      case 'dots':
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {[0, 1, 2].map((index) => (
              <MotionBox
                key={index}
                sx={{
                  width: getSizeValue() / 4,
                  height: getSizeValue() / 4,
                  borderRadius: '50%',
                  backgroundColor: 'primary.main',
                }}
                animate={{
                  y: [-10, 0, -10],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: index * 0.2,
                }}
              />
            ))}
            {text && (
              <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                {text}
              </Typography>
            )}
          </Box>
        );

      case 'pulse':
        return (
          <MotionBox
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <MotionBox
              sx={{
                width: getSizeValue(),
                height: getSizeValue(),
                borderRadius: '50%',
                backgroundColor: 'primary.main',
                opacity: 0.8,
              }}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.8, 0.4, 0.8],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
              }}
            />
            {text && (
              <Typography variant="body2" color="text.secondary">
                {text}
              </Typography>
            )}
          </MotionBox>
        );

      default: // circular
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={getSizeValue()} color={color} />
            {text && (
              <Typography variant="body2" color="text.secondary">
                {text}
              </Typography>
            )}
          </Box>
        );
    }
  };

  const content = renderLoadingContent();

  if (fullScreen) {
    return (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 9999,
        }}
      >
        {content}
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
      }}
    >
      {content}
    </Box>
  );
};

export default Loading;