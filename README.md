<!-- ---
title: Banking Dispute Resolution System
emoji: 🤖
colorFrom: green
colorTo: gray
pinned: false
sdk: docker
--- -->
# AI-Powered Dispute Resolution

[![Build Status](https://img.shields.io/github/actions/workflow/status/DebopamParam/AI-Powered_Dispute_Resolution/ci.yml?branch=main)](https://github.com/DebopamParam/AI-Powered_Dispute_Resolution/actions)
[![Version](https://img.shields.io/github/v/release/DebopamParam/AI-Powered_Dispute_Resolution?include_prereleases)](https://github.com/DebopamParam/AI-Powered_Dispute_Resolution/releases)
[![License](https://img.shields.io/github/license/DebopamParam/AI-Powered_Dispute_Resolution)](https://github.com/DebopamParam/AI-Powered_Dispute_Resolution/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.1-009688)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.22.0-FF4B4B)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.0.200-yellow)](https://langchain.com/)
[![Gemini API](https://img.shields.io/badge/Gemini%20API-1.0-blue)](https://ai.google.dev/)
[![Hugging Face Spaces](https://img.shields.io/badge/Hugging%20Face%20Spaces-Ready-yellow)](https://huggingface.co/spaces)

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact/Support](#contactsupport)
- [Disclaimer](#disclaimer)

## 🔍 Overview

The AI-Powered Dispute Resolution system is designed to streamline the process of analyzing and resolving disputes using advanced AI technologies. This application leverages large language models to analyze dispute details, identify key issues, suggest potential solutions, and provide legal references. The system is primarily designed to operate as a standalone application on Hugging Face Spaces, combining a user-friendly Streamlit frontend with a robust FastAPI backend.

## ✨ Key Features

### AI-Powered Analysis
- **Intelligent Dispute Processing**: Analyzes dispute details using Gemini API to extract key information
- **Solution Recommendation**: Suggests potential resolutions based on similar historical cases
- **Legal Reference Integration**: Provides relevant legal references and precedents
- **Continuous Learning**: System improves over time by incorporating feedback from resolved cases

### Frontend Capabilities
- **Intuitive Interface**: User-friendly Streamlit interface for submitting and tracking disputes
- **Dashboard**: Real-time visualization of dispute status and analytics
- **Document Upload**: Support for uploading relevant documents in various formats
- **Explainable AI**: Clear explanations of how the AI reached its conclusions

### Backend Robustness
- **Secure API**: FastAPI backend ensuring secure data processing
- **Efficient Data Management**: Optimized database schema for quick retrieval and analysis
- **Scalable Architecture**: Designed to handle increasing volumes of disputes
- **Comprehensive Logging**: Detailed activity logs for auditing purposes

### Deployment Strategy
- **Hugging Face Integration**: Seamless deployment on Hugging Face Spaces
- **Single Container Solution**: Entire application packaged in a single Docker container
- **Environment Variable Configuration**: Easy configuration through environment variables

## 🏗️ Architecture Overview

### High-Level System Diagram

```mermaid
graph TD
    A[User] -->|Submits Dispute| B[Streamlit Frontend]
    B -->|API Request| C[FastAPI Backend]
    C -->|Query| D[Database]
    C -->|Analysis Request| E[Gemini API]
    E -->|Analysis Results| C
    C -->|Response| B
    B -->|Display Results| A
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
    style E fill:#bff,stroke:#333,stroke-width:2px
```

The diagram above illustrates the flow of data through the system, from user input to AI analysis and result presentation.

### Component Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Streamlit Frontend
    participant Backend as FastAPI Backend
    participant DB as Database
    participant AI as Gemini API

    User->>Frontend: Submit dispute details
    Frontend->>Backend: POST /api/disputes
    Backend->>DB: Store dispute data
    Backend->>AI: Request analysis
    AI->>Backend: Return analysis results
    Backend->>DB: Update with analysis
    Backend->>Frontend: Return dispute ID & status
    Frontend->>User: Display confirmation
    User->>Frontend: View analysis results
    Frontend->>Backend: GET /api/disputes/{id}
    Backend->>DB: Retrieve dispute data
    DB->>Backend: Return dispute data
    Backend->>Frontend: Return complete dispute info
    Frontend->>User: Display analysis results
```

This sequence diagram shows the typical flow when a user submits a dispute for analysis.

### Deployment Architecture Diagram

```mermaid
graph TD
    A[Hugging Face Space] -->|Container| B[Docker Container]
    B -->|Port 8000| C[FastAPI Backend]
    B -->|Port 8501| D[Streamlit Frontend]
    C -->|Internal Communication| D
    C -->|Database| E[SQLite]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
    style E fill:#bff,stroke:#333,stroke-width:2px
```

The deployment architecture shows how the application is packaged in a single Docker container for deployment on Hugging Face Spaces.

### Database Schema Diagram

```mermaid
erDiagram
    DISPUTES {
        string id PK
        string title
        string description
        datetime created_at
        string status
        string user_id FK
    }
    ANALYSIS {
        string id PK
        string dispute_id FK
        string key_issues
        string suggested_solutions
        string legal_references
        datetime created_at
    }
    USERS {
        string id PK
        string username
        string email
        datetime created_at
    }
    FEEDBACK {
        string id PK
        string analysis_id FK
        int rating
        string comments
        datetime created_at
    }
    DISPUTES ||--o{ ANALYSIS : has
    USERS ||--o{ DISPUTES : submits
    ANALYSIS ||--o{ FEEDBACK : receives
```

This ER diagram shows the database structure used to store dispute information, analysis results, user data, and feedback.

### User Flow Diagram

```mermaid
graph TD
    A[Start] --> B[Create Account/Login]
    B --> C[Submit New Dispute]
    C --> D[Upload Supporting Documents]
    D --> E[View Initial AI Analysis]
    E --> F{Satisfied with Analysis?}
    F -->|Yes| G[Accept Recommendations]
    F -->|No| H[Request Detailed Analysis]
    H --> I[Review Detailed Analysis]
    I --> J{Accept Solution?}
    J -->|Yes| K[Implement Solution]
    J -->|No| L[Provide Feedback]
    L --> M[Receive Refined Analysis]
    M --> J
    G --> N[Provide Feedback on Process]
    K --> N
    N --> O[End]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style J fill:#bbf,stroke:#333,stroke-width:2px
    style O fill:#f9f,stroke:#333,stroke-width:2px
```

This diagram illustrates the typical user journey through the dispute resolution process.

## 🛠️ Technologies Used

- [Python 3.9+](https://www.python.org/) - Programming language
- [FastAPI](https://fastapi.tiangolo.com/) - Backend API framework
- [Streamlit](https://streamlit.io/) - Frontend framework
- [LangChain](https://langchain.com/) - AI integration framework
- [Gemini API](https://ai.google.dev/) - AI language model
- [SQLite](https://www.sqlite.org/) - Database
- [Docker](https://www.docker.com/) - Containerization
- [Hugging Face Spaces](https://huggingface.co/spaces) - Deployment platform

## 📋 Prerequisites

To run this application, you need:

- Python 3.9 or higher
- Docker and Docker Compose
- Gemini API key
- Hugging Face account (for deployment)

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DebopamParam/AI-Powered_Dispute_Resolution.git
   cd AI-Powered_Dispute_Resolution
   ```

2. Create a `.env` file in the root directory with the following variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=sqlite:///./app.db
   DEBUG=False
   ```

3. Build the Docker image:
   ```bash
   docker build -t dispute-resolution-app .
   ```

## ⚙️ Configuration

### Environment Variables

The application can be configured using the following environment variables:

- `GEMINI_API_KEY` - Your Gemini API key
- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `DEBUG` - Enable debug mode (True/False)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, ERROR)
- `MAX_UPLOAD_SIZE` - Maximum file upload size in MB

### Optional Configuration Files

You can also create the following configuration files:

- `config/app_config.json` - Application-specific settings
- `config/model_config.json` - AI model parameters

## 📝 Usage

### Running Locally

1. Start the application using Docker Compose:
   ```bash
   docker-compose up
   ```

2. Navigate to http://localhost:8501 in your web browser

### Quickstart Guide

1. Create an account or log in
2. Click on "Create New Dispute"
3. Fill in the dispute details:
   - Title
   - Description
   - Parties involved
   - Relevant dates
4. Upload any supporting documents
5. Click "Submit for Analysis"
6. Wait for the AI to analyze the dispute
7. Review the analysis results, which include:
   - Key issues identified
   - Suggested solutions
   - Legal references
8. Provide feedback on the analysis
9. Implement the recommended solutions

## 📚 API Documentation

The API documentation is automatically generated and available at `/docs` when running the application. It provides:

- Complete list of endpoints
- Request and response schemas
- Authentication requirements
- Example requests
- Interactive testing capabilities

## 🧪 Testing

To run the tests:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_api.py

# Run with coverage report
python -m pytest --cov=app tests/
```

## 🚀 Deployment

### Deploying to Hugging Face Spaces

1. Fork this repository
2. Create a new Space on Hugging Face:
   - Type: Docker
   - Repository: Your forked repository
3. Add the following secrets to your Space:
   - `GEMINI_API_KEY` - Your Gemini API key
4. The Space will automatically build and deploy the application

### Deploying Locally with Docker Compose

1. Make sure Docker and Docker Compose are installed
2. Create the `.env` file as described in the Installation section
3. Run the following command:
   ```bash
   docker-compose up -d
   ```
4. Access the application at http://localhost:8501

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure your code follows the project's coding standards and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/DebopamParam/AI-Powered_Dispute_Resolution/blob/main/LICENSE) file for details.

## 👏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the efficient API framework
- [Streamlit](https://streamlit.io/) for the intuitive frontend framework
- [LangChain](https://langchain.com/) for simplifying AI integration
- [Gemini API](https://ai.google.dev/) for the powerful language model
- [Hugging Face Spaces](https://huggingface.co/spaces) for the deployment platform

## 📞 Contact/Support

- For bug reports and feature requests, please [open an issue](https://github.com/DebopamParam/AI-Powered_Dispute_Resolution/issues)

## ⚠️ Disclaimer

This project is a prototype and should be used with caution. The AI-generated recommendations should not be considered legal advice. Always consult with a qualified legal professional for legal matters.