import React from 'react';
import {
  Card as MuiCard,
  CardProps as MuiCardProps,
  CardContent,
  CardActions,
  CardHeader,
  Typography,
  Box,
} from '@mui/material';
import { motion } from 'framer-motion';

interface CardProps extends Omit<MuiCardProps, 'title'> {
  title?: string | React.ReactNode;
  subtitle?: string;
  actions?: React.ReactNode;
  headerAction?: React.ReactNode;
  hoverable?: boolean;
  clickable?: boolean;
  selected?: boolean;
}

const MotionCard = motion(MuiCard);

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  actions,
  headerAction,
  hoverable = false,
  clickable = false,
  selected = false,
  sx,
  ...props
}) => {
  const cardVariants = hoverable || clickable ? {
    initial: {
      scale: 1,
      boxShadow: '0px 4px 10px 0px rgba(0,0,0,0.06), 0px 1px 3px 0px rgba(0,0,0,0.03)',
    },
    hover: {
      scale: 1.02,
      boxShadow: '0px 10px 22px 0px rgba(0,0,0,0.12), 0px 3px 6px 0px rgba(0,0,0,0.04)',
    },
  } : {};

  const cardSx = {
    ...sx,
    cursor: clickable ? 'pointer' : 'default',
    border: selected ? '2px solid' : '1px solid transparent',
    borderColor: selected ? 'primary.main' : 'transparent',
    transition: 'all 0.2s ease',
  };

  const content = (
    <>
      {(title || headerAction) && (
        <CardHeader
          title={
            typeof title === 'string' ? (
              <Typography variant="h6" component="h3">
                {title}
              </Typography>
            ) : (
              title
            )
          }
          subheader={subtitle}
          action={headerAction}
          sx={{ pb: 0 }}
        />
      )}
      <CardContent>
        {children}
      </CardContent>
      {actions && (
        <CardActions sx={{ px: 2, pb: 2 }}>
          {actions}
        </CardActions>
      )}
    </>
  );

  if (hoverable || clickable) {
    return (
      <MotionCard
        {...props}
        sx={cardSx}
        variants={cardVariants}
        initial="initial"
        whileHover="hover"
        transition={{ duration: 0.2 }}
      >
        {content}
      </MotionCard>
    );
  }

  return (
    <MuiCard {...props} sx={cardSx}>
      {content}
    </MuiCard>
  );
};

export default Card;