import React from 'react';
import {
  Box,
  Chip,
  Stack,
  Typography,
  Fade,
  Paper,
} from '@mui/material';
import {
  AutoAwesome as SparkleIcon,
  Business as BusinessIcon,
  Groups as TeamsIcon,
  Psychology as LeadershipIcon,
  TrendingUp as PerformanceIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface SuggestedQuestionsProps {
  questions?: string[];
  onQuestionClick: (question: string) => void;
  visible?: boolean;
}

const MotionChip = motion(Chip);

const defaultQuestions = [
  {
    icon: <LeadershipIcon />,
    text: "What are the key dimensions of effective leadership?",
    category: "leadership",
  },
  {
    icon: <BusinessIcon />,
    text: "How can HR create more value for the business?",
    category: "hr",
  },
  {
    icon: <TeamsIcon />,
    text: "What builds high-performing organizational cultures?",
    category: "culture",
  },
  {
    icon: <PerformanceIcon />,
    text: "How do we measure organizational capability?",
    category: "performance",
  },
];

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  questions,
  onQuestionClick,
  visible = true,
}) => {
  const displayQuestions = questions || defaultQuestions.map(q => q.text);

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
      },
    },
  };

  if (!visible) return null;

  return (
    <Fade in={visible} timeout={500}>
      <Box sx={{ px: 2, py: 3 }}>
        <Paper
          elevation={0}
          sx={{
            p: 3,
            backgroundColor: 'background.default',
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          {/* Header */}
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
            <SparkleIcon sx={{ color: 'primary.main', fontSize: 20 }} />
            <Typography variant="subtitle2" color="text.primary" fontWeight={600}>
              Suggested Questions
            </Typography>
          </Stack>

          {/* Questions Grid */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <Stack direction="row" flexWrap="wrap" gap={1.5}>
              {displayQuestions.map((question, index) => {
                const defaultQ = defaultQuestions[index];
                const icon = defaultQ?.icon || <SparkleIcon />;
                const category = defaultQ?.category || 'general';

                return (
                  <motion.div key={index} variants={itemVariants}>
                    <MotionChip
                      icon={icon}
                      label={question}
                      onClick={() => onQuestionClick(question)}
                      variant="outlined"
                      sx={{
                        py: 2.5,
                        px: 1,
                        height: 'auto',
                        maxWidth: { xs: '100%', sm: 350 },
                        '& .MuiChip-label': {
                          whiteSpace: 'normal',
                          display: 'block',
                          lineHeight: 1.4,
                          py: 0.5,
                        },
                        borderColor: 'divider',
                        backgroundColor: 'background.paper',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        '&:hover': {
                          borderColor: 'primary.main',
                          backgroundColor: 'action.hover',
                          transform: 'translateY(-2px)',
                          boxShadow: 2,
                        },
                      }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    />
                  </motion.div>
                );
              })}
            </Stack>
          </motion.div>

          {/* Quick Tips */}
          <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Stack direction="row" spacing={3} flexWrap="wrap">
              <Typography variant="caption" color="text.secondary">
                💡 Tip: Type <strong>@</strong> to select an agent
              </Typography>
              <Typography variant="caption" color="text.secondary">
                📎 Drag & drop files to upload
              </Typography>
              <Typography variant="caption" color="text.secondary">
                ⌨️ Press <strong>Tab</strong> to autocomplete
              </Typography>
            </Stack>
          </Box>
        </Paper>
      </Box>
    </Fade>
  );
};

export default SuggestedQuestions;