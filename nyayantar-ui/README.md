# Nyantar AI - Legal Assistant UI

A modern, responsive web interface for the Nyantar AI legal assistant, built with Next.js and Tailwind CSS.

## Features

- **Dark Theme**: Modern dark interface optimized for legal research
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Interactive Tabs**: Feature tabs for different legal assistant capabilities
- **Real-time Input**: Live chat interface with intelligent input handling
- **Professional UI**: Clean, professional design matching legal industry standards

## Tech Stack

- **Next.js 15.4.6**: React framework with App Router
- **React 19.1.0**: Latest React version
- **TypeScript**: Type-safe development
- **Tailwind CSS v4**: Modern utility-first CSS framework
- **ESLint**: Code quality and consistency

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the UI directory:
```bash
cd nyayantar-ui
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout component
│   ├── page.tsx            # Main page component
│   └── globals.css         # Global styles
├── components/
│   ├── Header.tsx          # Header component with navigation
│   ├── FeatureTabs.tsx     # Feature tabs component
│   ├── ChatInput.tsx       # Chat input component
│   └── Footer.tsx          # Footer component
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## UI Components

### Header
- Hamburger menu for navigation
- Nyantar AI branding with hexagon icon
- User profile and theme toggle buttons

### Feature Tabs
- **Chat**: Free legal Q&A interface
- **Judgements PRO**: Premium judgements search
- **Summarize Documents PRO**: Document summarization
- **AI Drafting PRO**: Legal document drafting

### Chat Input
- Large textarea for detailed legal questions
- Prompts Library link for example questions
- Send button with validation
- Legal disclaimer

### Footer
- Links to plans, legal resources, and policies
- Responsive layout with hover effects

## Design System

### Colors
- **Primary Background**: `#1a1a1a` (Dark gray)
- **Secondary Background**: `#374151` (Input fields)
- **Accent**: `#d97706` (Orange for PRO badges and buttons)
- **Text**: `#ffffff` (White) and `#9ca3af` (Gray)

### Typography
- **Font**: Geist Sans (Google Fonts)
- **Sizes**: Responsive text sizing with Tailwind utilities

## Development

### Adding New Features
1. Create new components in `src/components/`
2. Update the main page to include new functionality
3. Add TypeScript interfaces for type safety
4. Test responsive behavior

### Styling
- Use Tailwind CSS classes for styling
- Follow the existing color scheme
- Ensure responsive design for all screen sizes

## Deployment

The application can be deployed to:
- Vercel (recommended for Next.js)
- Netlify
- Any static hosting service

Build the application:
```bash
npm run build
```

## Contributing

1. Follow the existing code structure
2. Use TypeScript for all new components
3. Maintain responsive design
4. Test on multiple screen sizes
5. Follow ESLint rules

## License

This project is part of the Nyantar AI legal assistant system.
