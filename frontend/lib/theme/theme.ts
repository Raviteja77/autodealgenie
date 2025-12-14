'use client';

import { createTheme } from '@mui/material/styles';

// 1. AESTHETICS: Define the modern, minimalist, and professional theme.
export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#0d253f", // Deep Blue
    },
    secondary: {
      main: "#6c757d", // Gray
    },
    success: {
      main: "#66bb6a", // Light Green for positive states/actions
      contrastText: "#ffffff",
    },
    background: {
      default: "#f8f9fa", // Light gray background for ample white space
    },
    text: {
      primary: "#212529",
      secondary: "#6c757d",
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    // Clear hierarchy for scannable text
    h4: { fontWeight: 700, color: "#0d253f" }, // Large section titles
    h5: { fontWeight: 600, color: "#0d253f" }, // Medium subtitles
    h6: { fontWeight: 600, fontSize: "1rem", color: "#47535E" }, // Compact labels
  },
  components: {
    // Card-based components with subtle shadows and rounded corners
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "rgba(149, 157, 165, 0.1) 0px 8px 24px",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "rgba(149, 157, 165, 0.1) 0px 8px 24px",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: "none",
          fontWeight: 600,
          padding: "10px 20px",
        },
      },
    },
    MuiToggleButton: {
      styleOverrides: {
        root: {
          borderRadius: "8px !important",
          textTransform: "none",
          fontWeight: 500,
        },
      },
    },
  },
});