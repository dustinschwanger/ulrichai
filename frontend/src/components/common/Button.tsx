import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';

interface ButtonProps extends MuiButtonProps {
  isLoading?: boolean;
  loadingText?: string;
  icon?: React.ReactNode;
  animate?: boolean;
}

const MotionButton = motion(MuiButton);

export const Button: React.FC<ButtonProps> = ({
  children,
  isLoading = false,
  loadingText,
  icon,
  animate = true,
  disabled,
  startIcon,
  ...props
}) => {
  const buttonVariants = animate ? {
    initial: { scale: 1 },
    hover: { scale: 1.02 },
    tap: { scale: 0.98 },
  } : {};

  return (
    <MotionButton
      {...props}
      disabled={disabled || isLoading}
      startIcon={
        isLoading ? (
          <CircularProgress size={16} color="inherit" />
        ) : (
          startIcon || icon
        )
      }
      variants={buttonVariants}
      initial="initial"
      whileHover={!disabled && !isLoading ? "hover" : undefined}
      whileTap={!disabled && !isLoading ? "tap" : undefined}
      transition={{ duration: 0.1 }}
    >
      {isLoading && loadingText ? loadingText : children}
    </MotionButton>
  );
};

export default Button;