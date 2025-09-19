import { createTheme } from '@mui/material/styles';

// Create a professional theme with RBL Group branding
export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0086D6', // RBL Blue
      light: '#19A9FF', // Bright Blue
      dark: '#071D49', // Navy Blue
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#008884', // Green
      light: '#5EC4B6', // Bright Green
      dark: '#006660',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#ED1B34', // RBL Red
      light: '#F44958',
      dark: '#C41229',
    },
    warning: {
      main: '#E8B70B', // RBL Yellow
      light: '#F0C83B',
      dark: '#C49A09',
    },
    info: {
      main: '#0086D6', // RBL Blue
      light: '#19A9FF',
      dark: '#071D49',
    },
    success: {
      main: '#008884', // Green
      light: '#5EC4B6',
      dark: '#006660',
    },
    background: {
      default: '#F9FAFB',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#071D49', // Navy Blue for primary text
      secondary: '#6B7280',
    },
    divider: '#E5E7EB',
  },
  typography: {
    fontFamily: '"Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    subtitle1: {
      fontSize: '1rem',
      lineHeight: 1.75,
      fontWeight: 500,
    },
    subtitle2: {
      fontSize: '0.875rem',
      lineHeight: 1.57,
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.75,
      fontWeight: 400,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.57,
      fontWeight: 400,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
      letterSpacing: '0.01em',
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.66,
      fontWeight: 400,
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 1px 3px 0px rgba(0,0,0,0.03), 0px 1px 2px 0px rgba(0,0,0,0.02)',
    '0px 2px 6px 0px rgba(0,0,0,0.04), 0px 1px 2px 0px rgba(0,0,0,0.02)',
    '0px 3px 8px 0px rgba(0,0,0,0.05), 0px 1px 3px 0px rgba(0,0,0,0.03)',
    '0px 4px 10px 0px rgba(0,0,0,0.06), 0px 1px 3px 0px rgba(0,0,0,0.03)',
    '0px 5px 12px 0px rgba(0,0,0,0.07), 0px 2px 4px 0px rgba(0,0,0,0.03)',
    '0px 6px 14px 0px rgba(0,0,0,0.08), 0px 2px 4px 0px rgba(0,0,0,0.03)',
    '0px 7px 16px 0px rgba(0,0,0,0.09), 0px 2px 5px 0px rgba(0,0,0,0.03)',
    '0px 8px 18px 0px rgba(0,0,0,0.10), 0px 3px 5px 0px rgba(0,0,0,0.04)',
    '0px 9px 20px 0px rgba(0,0,0,0.11), 0px 3px 6px 0px rgba(0,0,0,0.04)',
    '0px 10px 22px 0px rgba(0,0,0,0.12), 0px 3px 6px 0px rgba(0,0,0,0.04)',
    '0px 11px 24px 0px rgba(0,0,0,0.13), 0px 4px 7px 0px rgba(0,0,0,0.04)',
    '0px 12px 26px 0px rgba(0,0,0,0.14), 0px 4px 7px 0px rgba(0,0,0,0.04)',
    '0px 13px 28px 0px rgba(0,0,0,0.15), 0px 4px 8px 0px rgba(0,0,0,0.04)',
    '0px 14px 30px 0px rgba(0,0,0,0.16), 0px 5px 8px 0px rgba(0,0,0,0.04)',
    '0px 15px 32px 0px rgba(0,0,0,0.17), 0px 5px 9px 0px rgba(0,0,0,0.04)',
    '0px 16px 34px 0px rgba(0,0,0,0.18), 0px 5px 9px 0px rgba(0,0,0,0.04)',
    '0px 17px 36px 0px rgba(0,0,0,0.19), 0px 6px 10px 0px rgba(0,0,0,0.04)',
    '0px 18px 38px 0px rgba(0,0,0,0.20), 0px 6px 10px 0px rgba(0,0,0,0.04)',
    '0px 19px 40px 0px rgba(0,0,0,0.21), 0px 6px 11px 0px rgba(0,0,0,0.04)',
    '0px 20px 42px 0px rgba(0,0,0,0.22), 0px 7px 11px 0px rgba(0,0,0,0.04)',
    '0px 21px 44px 0px rgba(0,0,0,0.23), 0px 7px 12px 0px rgba(0,0,0,0.04)',
    '0px 22px 46px 0px rgba(0,0,0,0.24), 0px 7px 12px 0px rgba(0,0,0,0.04)',
    '0px 23px 48px 0px rgba(0,0,0,0.25), 0px 8px 13px 0px rgba(0,0,0,0.04)',
    '0px 24px 50px 0px rgba(0,0,0,0.26), 0px 8px 13px 0px rgba(0,0,0,0.04)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 20px',
          fontSize: '0.875rem',
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 2px 6px 0px rgba(0,0,0,0.08)',
          },
        },
        sizeLarge: {
          padding: '12px 24px',
          fontSize: '1rem',
        },
        sizeSmall: {
          padding: '6px 12px',
          fontSize: '0.75rem',
        },
        contained: {
          '&:hover': {
            boxShadow: '0px 4px 10px 0px rgba(0,0,0,0.12)',
          },
        },
        outlined: {
          borderWidth: '1.5px',
          '&:hover': {
            borderWidth: '1.5px',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 10px 0px rgba(0,0,0,0.06), 0px 1px 3px 0px rgba(0,0,0,0.03)',
          '&:hover': {
            boxShadow: '0px 10px 22px 0px rgba(0,0,0,0.12), 0px 3px 6px 0px rgba(0,0,0,0.04)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
        elevation1: {
          boxShadow: '0px 2px 6px 0px rgba(0,0,0,0.04), 0px 1px 2px 0px rgba(0,0,0,0.02)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '& fieldset': {
              borderColor: '#E5E7EB',
              borderWidth: '1.5px',
            },
            '&:hover fieldset': {
              borderColor: '#D1D5DB',
            },
            '&.Mui-focused fieldset': {
              borderWidth: '2px',
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 500,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0px 1px 3px 0px rgba(0,0,0,0.03), 0px 1px 2px 0px rgba(0,0,0,0.02)',
          borderBottom: '1px solid #E5E7EB',
          backgroundColor: '#FFFFFF',
          color: '#111827',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid #E5E7EB',
          boxShadow: 'none',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 8px',
          '&:hover': {
            backgroundColor: 'rgba(0, 134, 214, 0.04)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(0, 134, 214, 0.08)',
            '&:hover': {
              backgroundColor: 'rgba(0, 134, 214, 0.12)',
            },
          },
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          borderRadius: 6,
          fontSize: '0.75rem',
          padding: '4px 8px',
        },
      },
    },
  },
});

// Dark theme configuration with RBL branding
export const darkTheme = createTheme({
  ...theme,
  palette: {
    mode: 'dark',
    primary: {
      main: '#19A9FF', // Bright Blue for dark mode
      light: '#4DB8FF',
      dark: '#0086D6',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#5EC4B6', // Bright Green for dark mode
      light: '#7FD4C8',
      dark: '#008884',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#0F172A',
      paper: '#1E293B',
    },
    text: {
      primary: '#F9FAFB',
      secondary: '#CBD5E1',
    },
    divider: '#334155',
  },
  components: {
    ...theme.components,
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1E293B',
          color: '#F9FAFB',
          borderBottom: '1px solid #334155',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1E293B',
          borderRight: '1px solid #334155',
        },
      },
    },
  },
});

export default theme;