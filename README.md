# Nyayantar AI - Legal Assistant

A powerful, context-aware legal assistant chatbot built with LangChain and advanced RAG techniques. This application uses Retrieval Augmented Generation (RAG) with multi-query retrieval and reciprocal rank fusion to provide accurate legal information based on your documents while maintaining conversation history.

## 🌟 Features

- **PDF Document Processing**: Automatically processes and indexes legal PDF documents
- **Multi-Query Retrieval**: Generates multiple query variations for improved retrieval coverage
- **Reciprocal Rank Fusion (RRF)**: Advanced document ranking for better result quality
- **Intelligent Query Classification**: Determines whether document retrieval is needed
- **Conversation History Awareness**: Maintains context across multiple questions
- **Vector Database Storage**: Efficiently stores and retrieves document embeddings using Chroma DB
- **Modern Web Interface**: Beautiful, responsive UI built with Next.js and Tailwind CSS
- **Real-time Chat**: Interactive chat interface with follow-up questions and source citations
- **Responsible AI Disclaimers**: Clearly communicates that responses are not substitutes for legal advice

## 🛠️ Technical Stack

### Backend
- **Framework**: LangChain + FastAPI
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Chat Model**: OpenAI GPT-3.5-turbo
- **Vector Store**: ChromaDB
- **Document Processing**: LangChain's PyPDFLoader
- **Text Splitting**: RecursiveCharacterTextSplitter
- **Advanced Features**: Multi-query generation, Reciprocal Rank Fusion

### Frontend
- **Framework**: Next.js 15.4.6 with App Router
- **UI Library**: React 19.1.0
- **Styling**: Tailwind CSS v4
- **Language**: TypeScript
- **Design**: Perplexity-inspired chat interface

## 📋 Prerequisites

```bash
python 3.12.7
node.js 18+
npm or yarn
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Install Frontend dependencies**:
```bash
cd nyayantar-ui
npm install
cd ..
```

3. **Start the complete pipeline**:
```bash
python start_pipeline.py
```

This will automatically start both the backend API server and frontend development server.

### Option 2: Manual Startup

#### Backend Setup

1. **Navigate to the project directory**:
```bash
cd nyayantar-ai
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Edit .env with your API keys:
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Start the backend API server**:
```bash
python api_server.py
```

The backend will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to the frontend directory**:
```bash
cd nyayantar-ui
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start the development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🎯 Usage

### Web Interface

1. **Open the application**: Navigate to `http://localhost:3000`
2. **Start chatting**: 
   - Type a legal question in the input field
   - Click one of the quick start buttons
   - Use the feature tabs to access different capabilities
3. **Chat page**: You'll be redirected to a dedicated chat page with:
   - Conversation history
   - Source citations
   - Follow-up questions
   - Real-time responses

### API Endpoints

- **Health Check**: `GET /health`
- **Chat**: `POST /api/chat`
- **API Documentation**: `http://localhost:8000/docs`

## 📁 Project Structure

```
nyayantar-ai/
├── api_server.py              # FastAPI backend server
├── app.py                     # Main RAG application
├── data-ingestion.py          # Document processing pipeline
├── start_pipeline.py          # Automated startup script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── data/                      # PDF documents directory
├── data-ingestion-local/      # Vector database storage
├── prompts/                   # Prompt templates
│   ├── mainRAG-prompt.md      # Main RAG system prompt
│   └── multiQuery-prompt.md   # Multi-query generation prompt
└── nyayantar-ui/              # Frontend application
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx       # Home page
    │   │   ├── chat/          # Chat page
    │   │   └── api/           # API routes
    │   └── components/        # React components
    ├── package.json           # Frontend dependencies
    └── README.md              # Frontend documentation
```

## 🔧 Key Components

### Backend Components

- **MultiQuery Class**: Pydantic model for structured query analysis
- **createMultiQueryChain()**: Creates the multi-query generation chain
- **generateRRF()**: Implements Reciprocal Rank Fusion for document ranking
- **generateResponse()**: Main response generation function with context integration

### Frontend Components

- **Chat Page**: Dedicated chat interface with conversation history
- **Message Display**: Shows user and assistant messages with proper formatting
- **Source Citations**: Displays document sources for responses
- **Follow-up Questions**: Suggests related questions for continued conversation
- **Real-time Input**: Responsive textarea with keyboard shortcuts

## ⚙️ How It Works

### 1. Document Processing Pipeline
```
PDF Documents → PyPDFLoader → Text Chunks → Embeddings → ChromaDB
```

### 2. Query Processing Pipeline
```
User Query → Query Classification → Multi-Query Generation → Document Retrieval → RRF Ranking → Response Generation
```

### 3. Web Interface Flow
```
User Input → Frontend API → Backend RAG → Response → UI Display
```

## 🎨 UI Features

### Chat Interface
- **Perplexity-inspired design**: Clean, modern chat interface
- **Message bubbles**: Distinct styling for user and assistant messages
- **Source citations**: Visual indicators for document sources
- **Follow-up questions**: Clickable suggestions for continued conversation
- **Loading states**: Real-time feedback during processing
- **Responsive design**: Works on desktop and mobile devices

### Navigation
- **Home page**: Welcome screen with quick start options
- **Chat page**: Dedicated conversation interface
- **Feature tabs**: Access to different capabilities (Chat, Judgements PRO, etc.)

## 🔑 API Keys Required

- **OpenAI API Key**: Required for the chat model (sign up at [OpenAI](https://openai.com/))
- **Cohere API Key**: Optional, if you want to switch to Cohere models

## 🚀 Deployment

### Backend Deployment
The FastAPI backend can be deployed to:
- **Railway**: Easy deployment with automatic scaling
- **Render**: Free tier available with automatic deployments
- **Heroku**: Traditional deployment option
- **AWS/GCP**: For production workloads

### Frontend Deployment
The Next.js frontend can be deployed to:
- **Vercel**: Recommended for Next.js applications
- **Netlify**: Alternative with good performance
- **AWS Amplify**: Full-stack deployment option

## 🧪 Testing

### Manual Testing
1. Start both servers using `python start_pipeline.py`
2. Open `http://localhost:3000` in your browser
3. Try asking legal questions like:
   - "What is the Indian Penal Code?"
   - "What are the fundamental rights in Indian Constitution?"
   - "Explain property laws in India"

### API Testing
- Backend health: `curl http://localhost:8000/health`
- Chat endpoint: Use the API documentation at `http://localhost:8000/docs`

## 🔧 Troubleshooting

### Common Issues

1. **Backend not starting**:
   - Check if all dependencies are installed: `pip install -r requirements.txt`
   - Verify API keys are set in `.env` file
   - Check if port 8000 is available

2. **Frontend not starting**:
   - Ensure Node.js 18+ is installed
   - Run `npm install` in the `nyayantar-ui` directory
   - Check if port 3000 is available

3. **Chat not working**:
   - Verify both backend and frontend are running
   - Check browser console for errors
   - Ensure API keys are valid

### Logs and Debugging
- Backend logs: Check the terminal where `api_server.py` is running
- Frontend logs: Check browser developer tools console
- API errors: Check the FastAPI logs in the backend terminal

## 📄 License

© 2024 Albin Xavier. All rights reserved.

This project is not licensed under any open-source license. You may not copy, distribute, or modify this project without permission.

## 👨‍💻 Creator

Created by Albin Xavier

## 🤝 Contributing

This is a private project. No external contributions are accepted at this time.