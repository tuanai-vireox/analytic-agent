# LibreChat Frontend

This directory contains the LibreChat frontend configuration for the Analytic Agent project.

## Overview

LibreChat is an open-source chat interface that provides a modern, feature-rich chat experience. It's configured to integrate with the Analytic Agent backend API for AI-powered analysis and chat functionality.

## Features

- 💬 Modern chat interface
- 🤖 AI model integration
- 📱 Responsive design
- 🔐 Authentication support
- 🌐 Multi-language support
- 📊 File upload and analysis
- 🔄 Real-time updates

## Quick Start

### Using Docker Compose (Recommended)

```bash
# From the project root
docker-compose up frontend

# Or from this directory
docker-compose up -d
```

### Manual Setup

1. Clone LibreChat repository:
```bash
git clone https://github.com/danny-avila/LibreChat.git
cd LibreChat
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Configure environment variables (see Configuration section)

4. Start the application:
```bash
docker-compose up -d
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# LibreChat Configuration
HOST=0.0.0.0
PORT=3000
JWT_SECRET=your_jwt_secret_here

# Database
MONGODB_URI=mongodb://localhost:27017/librechat

# API Configuration
API_BASE_URL=http://localhost:8000
API_KEY=your_api_key_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Security
ALLOW_REGISTRATION=true
ALLOW_SOCIAL_LOGIN=false
JWT_REFRESH_SECRET=your_refresh_secret_here

# Features
ENABLE_ANALYTICS=true
ENABLE_FILE_UPLOAD=true
MAX_FILE_SIZE=10485760
```

### Backend Integration

The frontend is configured to communicate with the Analytic Agent backend through:

- **API Base URL**: `http://localhost:8000`
- **Chat Endpoints**: `/api/v1/chat/`
- **Analysis Endpoints**: `/api/v1/analysis/`
- **User Management**: `/api/v1/users/`

## Development

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Docker Development

```bash
# Development with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f frontend
```

## API Integration

### Custom Endpoints

The frontend is configured to use custom endpoints for the Analytic Agent:

```javascript
// Chat endpoint
POST /api/v1/chat/
{
  "message": "Analyze this data",
  "context": "analysis_request"
}

// Analysis endpoint
POST /api/v1/analysis/
{
  "query": "Sales analysis for Q4",
  "analysis_type": "trend_analysis",
  "data_source": "sales_data.csv"
}
```

### WebSocket Support

Real-time communication is supported through WebSocket connections for:
- Live chat updates
- Analysis progress updates
- File upload progress
- System notifications

## Customization

### Themes

LibreChat supports custom themes. Create a custom theme by:

1. Adding CSS variables to the theme configuration
2. Customizing the chat interface styling
3. Modifying the color scheme

### Plugins

Extend functionality with LibreChat plugins:
- Custom analysis tools
- Data visualization components
- Export functionality
- Integration with external services

## Troubleshooting

### Common Issues

1. **Connection refused**: Check if the backend is running on port 8000
2. **Authentication errors**: Verify JWT_SECRET configuration
3. **File upload fails**: Check MAX_FILE_SIZE and file permissions
4. **API errors**: Verify API_BASE_URL and API_KEY configuration

### Logs

View application logs:
```bash
# Docker logs
docker-compose logs -f frontend

# Application logs
tail -f logs/librechat.log
```

## Contributing

1. Fork the LibreChat repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Resources

- [LibreChat Documentation](https://docs.librechat.ai/)
- [LibreChat GitHub](https://github.com/danny-avila/LibreChat)
- [Analytic Agent Backend](../backend/README.md) 