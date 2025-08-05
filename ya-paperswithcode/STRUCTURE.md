# YA-PapersWithCode Project Structure

## Overview
A modern rebuild of the PapersWithCode website using React, TypeScript, Vite, and Tailwind CSS. The application provides a comprehensive platform for browsing machine learning papers, datasets, methods, and state-of-the-art benchmarks.

## Technology Stack
- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v3 + Custom CSS variables
- **Routing**: React Router v6
- **UI Components**: Custom shadcn/ui-inspired components
- **Icons**: Lucide React

## Directory Structure

```
ya-paperswithcode/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── layout/         # Layout components
│   │   │   ├── Header.tsx  # Main navigation header
│   │   │   └── Layout.tsx  # App layout wrapper
│   │   ├── papers/         # Paper-related components
│   │   │   └── PaperCard.tsx
│   │   ├── datasets/       # Dataset-related components
│   │   │   ├── DatasetCard.tsx
│   │   │   └── DatasetFilters.tsx
│   │   ├── methods/        # Method-related components
│   │   │   └── MethodCard.tsx
│   │   └── ui/            # Base UI components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── select.tsx
│   │       └── tabs.tsx
│   ├── data/              # Static data files
│   │   ├── dataset-filters.json    # Dataset filter options
│   │   ├── method-categories.json  # Method categories
│   │   ├── sample-datasets.json    # Sample dataset data
│   │   ├── sample-methods.json     # Sample method data
│   │   ├── sample-papers.json      # Sample paper data
│   │   └── sample-sota.json        # Sample SOTA data
│   ├── lib/               # Utility functions
│   │   └── utils.ts       # Helper functions (cn)
│   ├── pages/             # Page components
│   │   ├── Home.tsx       # Papers page (main)
│   │   ├── Datasets.tsx   # Datasets browser
│   │   ├── Methods.tsx    # Methods browser
│   │   └── StateOfTheArt.tsx # SOTA benchmarks
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts       # Core type definitions
│   ├── App.tsx            # Main app component
│   ├── index.css          # Global styles + Tailwind
│   └── main.tsx           # App entry point
├── public/                # Static assets
├── index.html             # HTML template
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
└── postcss.config.js      # PostCSS configuration
```

## Core Features

### 1. Papers (Home Page)
- Display trending and latest papers
- Paper cards showing:
  - Title, authors, abstract
  - Stars count
  - Implementation framework badges
  - Publication date
- Load more functionality

### 2. Datasets Browser
- Comprehensive filtering system:
  - **Filter by Modality** (39 options): Texts, Images, Videos, etc.
  - **Filter by Task** (500+ options): Classification, Generation, etc.
  - **Filter by Language** (387 options): English, Chinese, etc.
- Dataset cards with paper count
- Search functionality

### 3. Methods Browser
- Categorized by domains:
  - General (191 methods)
  - Computer Vision (426 methods)
  - Natural Language Processing (251 methods)
  - Reinforcement Learning (55 methods)
  - Audio (38 methods)
- Method cards with description and paper count

### 4. State-of-the-Art
- Browse benchmarks by task
- Leaderboard display
- Model performance comparison

## Key Components

### Layout Components

#### Header.tsx
- Sticky navigation bar
- Search functionality with icon
- Navigation links to all main sections
- Sign In link

#### Layout.tsx
- Wrapper component providing consistent layout
- Integrates Header component
- Manages page content area

### UI Components

#### Button.tsx
- Multiple variants: default, primary, secondary, outline, ghost, link
- Size options: default, sm, lg, icon
- Fully accessible with keyboard navigation

#### Card.tsx
- Reusable card component for content display
- Consistent styling across the app

#### Select.tsx
- Custom select dropdown for filters
- Supports placeholder and value management

#### Tabs.tsx
- Tab navigation component
- Used in Methods page for category switching

## Styling System

### Color Scheme
- **Primary**: #007bff (HSL: 211 100% 50%)
- **Background**: White
- **Foreground**: Dark gray
- **Border**: Light gray
- CSS variables defined in HSL format for easy theming

### Tailwind Configuration
- Custom color palette matching PapersWithCode design
- Extended with CSS variables for dynamic theming
- Responsive breakpoints configured

## Data Structure

### Paper Type
```typescript
interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  date: string;
  stars: number;
  implementations: Implementation[];
  trending?: boolean;
}
```

### Dataset Type
```typescript
interface Dataset {
  id: string;
  name: string;
  description: string;
  paperCount: number;
  modality?: string;
  task?: string;
  languages?: string[];
}
```

### Method Type
```typescript
interface Method {
  id: string;
  name: string;
  fullName: string;
  description: string;
  category: string;
  paperCount: number;
  introduced: string;
}
```

## Build and Development

### Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript compiler

### Environment
- Node.js 16+
- Uses ES modules
- TypeScript with strict mode
- Vite for fast HMR and builds

## Recent Updates
1. Fixed Tailwind CSS v4 compatibility issues by reverting to v3
2. Resolved search icon overlap with proper positioning
3. Implemented comprehensive dataset filtering system
4. Added all original PapersWithCode categories and filters
5. Created responsive design for all screen sizes