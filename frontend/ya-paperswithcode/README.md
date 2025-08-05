# Papers With Code Clone

A modern recreation of the Papers With Code website built with React, TypeScript, and Tailwind CSS. This project serves as a static frontend for browsing historical machine learning papers, datasets, and methods.

## 🚀 Live Demo

Access the application at: `http://localhost:5173/` (after running the development server)

## ✨ Features

- 📄 **Papers Page** - Browse trending and latest machine learning papers with code implementations
- 📊 **Datasets** - Explore ML datasets with comprehensive filtering:
  - 39 Modalities (Texts, Images, Videos, Audio, Medical, 3D, etc.)
  - 500+ Tasks (Question Answering, Object Detection, etc.)
  - 387 Languages
- 🔧 **Methods** - Discover ML methods organized by categories:
  - General (Optimization, Regularization, Activation Functions)
  - Computer Vision (CNNs, Object Detection, Vision Transformers)
  - Natural Language Processing (Transformers, Language Models)
  - Reinforcement Learning (Policy Gradient, Q-Learning, Actor-Critic)
  - Audio (Speech Recognition, Speech Synthesis)
- 🏆 **State-of-the-Art** - Browse benchmark leaderboards across different domains
- 🔍 **Search** - Global search functionality across papers, datasets, and methods
- 📱 **Responsive Design** - Mobile-friendly interface optimized for all devices

## Tech Stack

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Custom components inspired by shadcn/ui
- **Routing**: React Router v6
- **Icons**: Lucide React

## Project Structure

```
src/
├── components/
│   ├── layout/          # Header, Footer, Layout wrapper
│   ├── papers/          # Paper-related components
│   ├── datasets/        # Dataset cards and filters
│   ├── methods/         # Method category cards
│   └── ui/              # Reusable UI components
├── pages/               # Page components
├── data/                # Static data files (categories, filters, samples)
├── types/               # TypeScript type definitions
└── lib/                 # Utility functions
```

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

## Data Sources

The project uses static JSON files for demonstration purposes:
- `sample-papers.json` - Example papers with metadata
- `sample-datasets.json` - Example datasets
- `dataset-filters.json` - Filter options for datasets
- `method-categories.json` - Method categorization

In a production environment, these would be replaced with API calls to fetch data from:
- [PapersWithCode Data Repository](https://github.com/paperswithcode/paperswithcode-data)

## Key Features Implementation

### Dataset Filtering
- Multi-select filters for modality, task, and language
- Real-time filtering with result count
- Collapsible filter sections
- Clear all filters option

### Method Categories
- Hierarchical organization of ML methods
- Expandable subcategories
- Links to related papers and implementations

### Responsive Design
- Mobile-first approach
- Adaptive grid layouts
- Touch-friendly interactions
- Optimized for various screen sizes

## Color Scheme

The design uses a blue-based color scheme matching the original PapersWithCode:
- Primary: `#007bff`
- Secondary: `#6c757d`
- Background: `#ffffff`
- Text: `#212529`

## Screenshots

### Papers Page (Home)
- Trending papers section with badges
- Paper cards showing title, authors, abstract, tags
- GitHub repository links with star counts
- Load more functionality

### Datasets Page
- Advanced filtering sidebar
- Grid layout with dataset cards
- Real-time filter results
- Multi-select filter options

### Methods Page
- Category cards with descriptions
- Hierarchical subcategory navigation
- Methods grouped by domain

## Development

### Prerequisites
- Node.js 20.x or higher
- npm 11.x or higher

### Environment Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/ya-paperswithcode.git
cd frontend/ya-paperswithcode

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Project Commands
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Data Integration

### Current Implementation
The project uses static JSON files in the `/src/data` directory:
- `sample-papers.json` - Example papers with metadata
- `sample-datasets.json` - Dataset examples  
- `dataset-filters.json` - Complete filter options (modalities, tasks, languages)
- `method-categories.json` - Full method categorization

### Production Data Source
For production use, integrate with the official PapersWithCode data:
1. Download data files from [paperswithcode-data](https://github.com/paperswithcode/paperswithcode-data)
2. Process JSON files: `papers-with-abstracts.json.gz`, `datasets.json.gz`, etc.
3. Implement API endpoints or static generation
4. Update data fetching hooks to use real endpoints

## Deployment

### Static Hosting (Recommended)
```bash
# Build the project
npm run build

# Deploy the 'dist' folder to:
# - Vercel
# - Netlify  
# - GitHub Pages
# - AWS S3 + CloudFront
```

### Docker Deployment
```dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Backend API integration with real-time data
- [ ] User authentication and personalization
- [ ] Paper submission and review system
- [ ] Advanced search with semantic matching
- [ ] Interactive benchmark visualization charts
- [ ] Paper recommendation engine
- [ ] BibTeX export functionality
- [ ] Dark mode theme support
- [ ] Mobile app (React Native)
- [ ] Browser extension for paper discovery

## Acknowledgments

- Original [Papers With Code](https://paperswithcode.com) for inspiration
- [PapersWithCode Data Repository](https://github.com/paperswithcode/paperswithcode-data) for datasets
- [shadcn/ui](https://ui.shadcn.com/) for UI component patterns
- [Tailwind CSS](https://tailwindcss.com/) for styling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The data from PapersWithCode is available under the Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0).
