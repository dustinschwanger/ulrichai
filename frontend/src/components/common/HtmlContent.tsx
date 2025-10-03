import React from 'react';
import { Box, BoxProps } from '@mui/material';

interface HtmlContentProps extends BoxProps {
  content: string;
}

/**
 * Component to safely render HTML content from the rich text editor
 */
const HtmlContent: React.FC<HtmlContentProps> = ({ content, sx, ...props }) => {
  // Return null if no content
  if (!content || content.trim() === '' || content === '<p></p>') {
    return null;
  }

  return (
    <Box
      {...props}
      sx={{
        '& p': {
          margin: '0.5em 0',
        },
        '& h1, & h2, & h3, & h4, & h5, & h6': {
          marginTop: '1em',
          marginBottom: '0.5em',
        },
        '& ul, & ol': {
          paddingLeft: '1.5em',
          margin: '0.5em 0',
        },
        '& img': {
          maxWidth: '100%',
          height: 'auto',
        },
        '& pre': {
          backgroundColor: '#f5f5f5',
          padding: '1em',
          borderRadius: '4px',
          overflow: 'auto',
          fontFamily: 'monospace',
        },
        '& code': {
          backgroundColor: '#f5f5f5',
          padding: '0.2em 0.4em',
          borderRadius: '3px',
          fontFamily: 'monospace',
        },
        '& pre code': {
          backgroundColor: 'transparent',
          padding: 0,
        },
        '& hr': {
          margin: '1em 0',
          border: 'none',
          borderTop: '2px solid #ddd',
        },
        '& blockquote': {
          borderLeft: '4px solid #ddd',
          paddingLeft: '1em',
          margin: '1em 0',
          fontStyle: 'italic',
        },
        '& a': {
          color: '#1976d2',
          textDecoration: 'underline',
        },
        ...sx,
      }}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  );
};

export default HtmlContent;
