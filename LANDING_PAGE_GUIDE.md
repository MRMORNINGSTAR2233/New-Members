# Landing Page Guide

This guide explains the new Spline-powered landing page that serves as the entry point to ZenBox AI.

## 🎨 Overview

The landing page features:
- **3D Spline Scene**: Interactive 3D background using your provided Spline scene
- **Modern Hero Section**: Compelling copy and call-to-action
- **Feature Highlights**: Key capabilities showcased with icons
- **Smooth Animations**: Fade-in effects and loading states
- **Responsive Design**: Works on desktop and mobile

## 🔄 Navigation Flow

```
Landing Page (/) → Global Search Page (/search)
```

- **Landing Page**: `http://localhost:5173/` - Entry point with Spline 3D scene
- **Global Search**: `http://localhost:5173/search` - Main application interface
- **Keyboard Shortcut**: `Cmd/Ctrl + K` → Navigates to Global Search

## 🎯 Key Features

### 3D Spline Integration
- Uses your provided Spline scene: `https://prod.spline.design/5wxq-b4n3f5kLLV0/scene.splinecode`
- Loading state with spinner while scene loads
- Dark overlay for better text readability
- Responsive 3D background

### Hero Section
- **Compelling Headline**: "Your AI-Powered Productivity Hub"
- **Descriptive Subtext**: Explains the value proposition
- **Feature Pills**: Gmail, Calendar, Meet, AI Automation
- **Call-to-Action**: "Start Searching" button leads to Global Search

### Visual Design
- **Dark Theme**: Gradient background from slate to purple
- **ZenBox Branding**: Logo with "ZB" initials
- **Beta Badge**: Indicates current development status
- **Stats Section**: 50+ tools, 10x faster workflows, AI powered

### Interactive Elements
- **Primary CTA**: "Start Searching" → Navigates to `/search`
- **Secondary CTA**: "View Demo" → Opens external demo link
- **Smooth Animations**: Content fades in after Spline loads
- **Hover Effects**: Button animations and transitions

## 🛠️ Technical Implementation

### Components Used
- **Spline**: 3D scene rendering
- **React Router**: Navigation to Global Search
- **Lucide Icons**: Feature icons and UI elements
- **Tailwind CSS**: Styling and animations
- **Custom UI Components**: Buttons, badges from design system

### File Structure
```
src/pages/LandingPage.tsx - Main landing page component
src/App.tsx - Updated routing configuration
```

### Dependencies
- `@splinetool/react-spline` - Spline 3D integration
- `react-router-dom` - Navigation
- `lucide-react` - Icons

## 🎨 Design Elements

### Color Scheme
- **Background**: Dark gradient (slate-900 → purple-900 → slate-900)
- **Text**: White primary, gray-300 secondary
- **Accents**: Purple-to-blue gradients
- **Feature Pills**: Semi-transparent white backgrounds

### Typography
- **Headline**: 5xl/7xl responsive, bold weight
- **Subtext**: xl/2xl responsive, gray-300
- **Features**: Small, medium weight
- **Stats**: 3xl bold for numbers

### Layout
- **Header**: Logo + Beta badge
- **Main**: Centered hero content
- **Footer**: Scroll indicator and instructions

## 🚀 Getting Started

### 1. Start the Application
```bash
npm run dev
```

### 2. Visit Landing Page
Navigate to `http://localhost:5173/` to see the landing page

### 3. Test Navigation
- Click "Start Searching" to go to Global Search
- Use `Cmd/Ctrl + K` keyboard shortcut
- Test responsive design on different screen sizes

### 4. Customize Content
Edit `src/pages/LandingPage.tsx` to modify:
- Hero text and messaging
- Feature highlights
- Call-to-action buttons
- Stats and numbers

## 🎯 User Journey

1. **Land on Homepage**: User sees impressive 3D Spline scene
2. **Read Value Proposition**: Understands ZenBox AI capabilities
3. **See Feature Pills**: Gmail, Calendar, Meet, AI integration
4. **Click "Start Searching"**: Navigates to main application
5. **Begin Using App**: Starts with Global Search interface

## 🔧 Customization Options

### Spline Scene
- Replace the scene URL in the Spline component
- Adjust loading states and error handling
- Modify overlay opacity for text readability

### Content
- Update hero headline and description
- Modify feature pills and descriptions
- Change stats and numbers
- Customize call-to-action text

### Styling
- Adjust gradient colors and effects
- Modify animation timings and effects
- Update responsive breakpoints
- Change button styles and hover states

## 📱 Responsive Design

### Desktop (1024px+)
- Full hero layout with large text
- Side-by-side CTA buttons
- 3-column stats grid

### Tablet (768px-1023px)
- Adjusted text sizes
- Stacked CTA buttons
- 3-column stats maintained

### Mobile (< 768px)
- Smaller text sizes
- Vertical button layout
- Single column stats

## 🐛 Troubleshooting

### Spline Scene Not Loading
- Check network connection
- Verify Spline scene URL is accessible
- Check browser console for errors
- Ensure @splinetool/react-spline is installed

### Navigation Issues
- Verify React Router setup in App.tsx
- Check route paths match navigation calls
- Test keyboard shortcut functionality

### Styling Problems
- Ensure Tailwind CSS is properly configured
- Check for conflicting styles
- Verify responsive classes are working

## 🔮 Future Enhancements

Planned improvements:
- **Interactive Spline Elements**: Clickable 3D objects
- **Animated Counters**: Numbers that count up on scroll
- **Video Background**: Alternative to Spline scene
- **A/B Testing**: Different hero messages
- **Analytics Integration**: Track conversion rates
- **SEO Optimization**: Meta tags and structured data

The landing page provides a compelling first impression that effectively communicates ZenBox AI's value proposition and guides users to the main application interface.
