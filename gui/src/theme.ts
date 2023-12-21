// theme.ts
import { extendTheme } from "@chakra-ui/react";


const fonts = {
  heading: 'Georgia, serif',
  body: 'Arial, sans-serif',
  mono: 'Menlo, monospace',
};

const colors = {
  brand: {
    50: '#eef2ff', // Lightest
    100: '#d0d6e6',
    200: '#b1bbcc',
    300: '#929fb3',
    400: '#737e99',
    500: '#556080', // Default or "base" color
    600: '#444e64',
    700: '#333c48',
    800: '#22292d',
    900: '#111317', // Darkest
  },
};

const fontSizes = {
  xs: '0.75rem',
  sm: '0.875rem',
  md: '1rem', // base font size
  lg: '1.125rem',
  xl: '1.25rem',
  '2xl': '1.5rem',
  '3xl': '1.75rem',
  '4xl': '2rem',
  '5xl': '2.25rem',
  '6xl': '2.5rem',
};

const fontWeights = {
  normal: 400,
  medium: 500,
  bold: 700,
};

const breakpoints = {
  sm: '320px',
  md: '768px',
  lg: '960px',
  xl: '1200px',
  '2xl': '1536px',
};

const components = {
  Button: {
    baseStyle: {
      fontWeight: 'bold',
    },
    sizes: {
      sm: {
        fontSize: 'sm',
        px: 4,
        py: 3,
      },
      md: {
        fontSize: 'md',
        px: 6,
        py: 4,
      },
    },
    variants: {
      solid: {
        bg: 'brand.500',
        color: 'white',
        _hover: {
          bg: 'brand.600',
        },
      },
    },
  },
};

const customTheme = extendTheme({
  colors,
  fonts,
  fontSizes,
  fontWeights,
  breakpoints,
  components,
});

export default customTheme;
