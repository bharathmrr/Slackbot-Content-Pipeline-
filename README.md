# Slackbot Content Pipeline

A comprehensive Slackbot that helps content teams streamline keyword-based content creation through automated keyword processing, content analysis, and report generation.

## 🚀 Features

- **Keyword Management**: Upload CSV files or paste keyword lists directly in Slack
- **Smart Grouping**: Semantic clustering of keywords using AI embeddings
- **Content Analysis**: Fetch and analyze top-ranking web content for each keyword group
- **Outline Generation**: Create structured content outlines based on competitor analysis
- **Post Ideas**: Generate creative post ideas for each keyword cluster
- **PDF Reports**: Comprehensive downloadable reports with all results
- **Email Integration**: Automatic report delivery via SendGrid
- **Real-time Processing**: Live updates and notifications in Slack

## 🏗️ Architecture

### System Overview

```mermaid
graph TB
    A[Slack User] -->|Commands/Files| B[Slack Bot]
    B --> C[Flask/FastAPI Backend]
    C --> D[Keyword Processor]
    C --> E[Web Searcher]
    C --> F[Content Extractor]
    C --> G[Outline Generator]
    C --> H[Post Idea Generator]
    C --> I[PDF Generator]
    
    D --> J[Keyword Grouper]
    J --> K[Sentence Transformers]
    
    E --> L[SerpAPI/Brave Search]
    F --> M[BeautifulSoup]
    
    C --> N[(Supabase DB)]
    C --> O[(Redis Cache)]
    
    I --> P[Email Service]
    P --> Q[SendGrid]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style N fill:#fff3e0
    style O fill:#fce4ec
```

### Project Structure

```
slackbot-content-pipeline/
│
├── Dockerfile                       # Docker container configuration
├── README.md                        # Project documentation
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── run_flask.py                     # Flask application runner
│
├── app/                             # Main application package
│   ├── __init__.py
│   ├── main.py                      # FastAPI entry point
│   ├── main_flask.py               # Flask entry point
│   ├── config.py                   # Configuration management
│   │
│   ├── slack/                      # Slack integration
│   │   ├── __init__.py
│   │   ├── bot.py                  # AsyncApp Slack bot
│   │   ├── flask_bot.py            # Flask Slack bot
│   │   ├── commands.py             # Command handlers
│   │   └── formatter.py            # Message formatting
│   │
│   ├── keyword/                    # Keyword processing
│   │   ├── __init__.py
│   │   ├── processor.py            # CSV/text parsing & cleaning
│   │   ├── grouper.py              # Semantic clustering
│   │   └── utils.py                # Keyword utilities
│   │
│   ├── outline/                    # Content outline generation
│   │   ├── __init__.py
│   │   ├── websearch.py            # Search API integration
│   │   ├── extractor.py            # Web content extraction
│   │   └── generator.py            # Outline generation logic
│   │
│   ├── post_ideas/                 # Post idea generation
│   │   ├── __init__.py
│   │   └── idea_generator.py       # AI-powered idea generation
│   │
│   ├── reports/                    # Report generation
│   │   ├── __init__.py
│   │   ├── pdf_generator.py        # PDF creation
│   │   └── emailer.py              # Email delivery
│   │
│   └── storage/                    # Data persistence
│       ├── __init__.py
│       ├── database.py             # Supabase integration
│       └── cache.py                # Redis caching
│
├── scripts/                        # Utility scripts
│   └── seed_db.py                  # Database initialization
│
├── tests/                          # Test suite
│   └── ...
│
├── .github/                        # CI/CD workflows
│   └── workflows/
│       └── ci-cd.yml
│
└── docs/                           # Documentation
    └── assignment_documentation.pdf
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask/FastAPI (Python 3.8+)
- **Async Processing**: asyncio, threading
- **Configuration**: Pydantic Settings

### Slack Integration
- **SDK**: Slack Bolt for Python
- **Communication**: Real-time events, slash commands, interactive components

### AI & ML
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Clustering**: scikit-learn K-means
- **Text Processing**: NLTK, BeautifulSoup

### Data & Storage
- **Database**: Supabase (PostgreSQL)
- **Caching**: Upstash Redis
- **File Storage**: Local/Cloud storage for PDFs

### External APIs
- **Search**: SerpAPI / Brave Search API
- **Email**: SendGrid
- **Web Scraping**: aiohttp, BeautifulSoup

### DevOps
- **Containerization**: Docker
- **Deployment**: Render.com
- **CI/CD**: GitHub Actions
- **Monitoring**: Loguru logging

## 🚦 Getting Started

### Prerequisites

- Python 3.8+
- Slack App with Bot Token
- Supabase Project
- OpenAI API Key (optional)
- Redis instance (Upstash)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/slackbot-content-pipeline.git
   cd slackbot-content-pipeline
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Run the application**
   
   **Flask version:**
   ```bash
   python run_flask.py
   ```
   
   **FastAPI version:**
   ```bash
   python -m app.main
   ```

### Environment Variables

```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# AI Services
OPENAI_API_KEY=sk-your-openai-key

# Search APIs
SERP_API_KEY=your-serp-api-key
BRAVE_SEARCH_API_KEY=your-brave-api-key

# Cache
REDIS_URL=redis://your-redis-url

# Email
SENDGRID_API_KEY=SG.your-sendgrid-key
FROM_EMAIL=noreply@yourdomain.com
```

## 📱 Slack Commands

### Available Commands

- `/keywords upload` - Upload CSV file with keywords
- `/keywords paste` - Paste keywords directly in chat
- `/process <batch_id>` - Start processing a keyword batch
- `/history` - View your processing history
- `/regenerate <batch_id>` - Regenerate outlines for a batch

### Usage Examples

1. **Upload keywords via CSV:**
   ```
   /keywords upload
   [Upload your CSV file]
   ```

2. **Paste keywords directly:**
   ```
   /keywords paste
   seo optimization, content marketing, digital strategy
   ```

3. **Process keywords:**
   ```
   /process batch_123
   ```

## 🔄 Processing Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Slack Bot
    participant K as Keyword Processor
    participant G as Grouper
    participant O as Outline Generator
    participant P as PDF Generator
    participant E as Email Service

    U->>S: Upload keywords
    S->>K: Parse & clean keywords
    K->>S: Return cleaned keywords
    S->>U: Confirm upload

    U->>S: /process batch_id
    S->>G: Group keywords semantically
    G->>S: Return keyword groups
    
    S->>O: Generate outlines for each group
    O->>S: Return structured outlines
    
    S->>P: Generate PDF report
    P->>S: Return download URL
    
    S->>E: Send email (optional)
    S->>U: Processing complete + download link
```

## 🗃️ Database Schema

### Tables

```sql
-- Keyword Batches
CREATE TABLE keyword_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    keywords JSONB NOT NULL,
    keyword_count INTEGER NOT NULL,
    status TEXT DEFAULT 'uploaded',
    source TEXT DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Keyword Groups
CREATE TABLE keyword_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
    keywords JSONB NOT NULL,
    cluster_name TEXT NOT NULL,
    similarity_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Outlines
CREATE TABLE outlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES keyword_groups(id) ON DELETE CASCADE,
    outline_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY,
    batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🚀 Deployment

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t slackbot-content-pipeline .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 --env-file .env slackbot-content-pipeline
   ```

### Render.com Deployment

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy as a Web Service
4. Configure health check endpoint: `/health`

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_keyword_processor.py
```

## 📊 Monitoring & Logging

- **Logging**: Structured logging with Loguru
- **Health Checks**: `/health` endpoint for monitoring
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Rate Limiting**: Built-in rate limiting for API protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Contact the development team
- Check the documentation in the `docs/` folder

## 🔮 Roadmap

- [ ] Integration with Google Sheets
- [ ] Notion database sync
- [ ] Advanced AI content generation
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Webhook integrations

---

**Built with ❤️ for content teams everywhere**
