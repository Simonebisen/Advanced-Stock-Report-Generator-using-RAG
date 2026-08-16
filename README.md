# 📊 Stock Report Generator (RAG + Financial Analysis)

An advanced financial analysis platform combining RAG-based SEC filing analysis, technical indicators, web intelligence, and modern visualizations to generate comprehensive stock reports.

👉 Users can input a stock symbol, and the system will automatically retrieve relevant SEC filings, market trends, price history, and financial indicators — then compile all findings into a well-structured PDF report for investment analysis.

---
# 📊 Stock Report Generator

An advanced financial analysis platform combining RAG-based SEC filing analysis, technical indicators, web intelligence, and modern visualizations to generate comprehensive stock reports.

## 🚀 Key Features

| Feature | Description |
| ------- | ----------- |
| 📄 **RAG-based SEC Analysis** | Leverages Gemini AI and Pinecone vector database to analyze SEC 10-K filings and extract key insights |
| 📈 **Technical Analysis** | Calculates key technical indicators including Moving Averages, MACD, RSI, and Bollinger Bands |
| 💰 **Financial Valuation** | Performs valuation analysis using PE, PB, PS ratios and builds earnings forecasts |
| 🔍 **Industry Chain Analysis** | Analyzes company's position in industry, supply chain relationships, and competitive advantages |
| 📰 **Web Intelligence** | Gathers and processes recent news, market outlook, and company developments |
| 📊 **Interactive Visualizations** | Generates candlestick charts with technical indicators and volume analysis |
| 📝 **PDF Report Generation** | Creates professional PDF reports with all analyses combined into a single document |

## 📋 Use Cases

- **Investment Research**: Generate comprehensive stock analysis reports for informed investment decisions
- **Competitor Analysis**: Understand a company's competitive position within its industry
- **Risk Assessment**: Identify and evaluate key risk factors mentioned in SEC filings and market analysis
- **Market Intelligence**: Track recent developments and news impacting stock performance
- **Technical Trading**: Analyze price trends and technical indicators for short-term trading

## 🏗️ Architecture

The system uses a modular architecture with specialized agents and services:

```plaintext
┌─────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  RAG Agent      │     │  Web Search Agent │     │  Stock Data Agent │
│  (SEC Analysis) │     │  (News & Trends)  │     │  (Technical Data) │
└────────┬────────┘     └──────────┬────────┘     └─────────┬─────────┘
         │                         │                        │
         ▼                         ▼                        ▼
┌────────▼─────────┐    ┌──────────▼─────────┐    ┌─────────▼──────────┐
│ Edgar Service    │    │ Web Search Service │    │ Alpha Vantage Svc  │
│ (SEC Filings)    │    │ (Search API)       │    │ (Price History)    │
└────────┬─────────┘    └──────────┬─────────┘    └─────────┬──────────┘
         │                         │                        │
         └─────────────┬───────────┴────────────┬───────────┘
                       ▼                        ▼
             ┌──────────────────┐     ┌─────────────────┐
             │ MCP Coordinator  │     │ Data Processor  │
             │ (Orchestration)  │     │ (Calculations)  │
             └────────┬─────────┘     └────────┬────────┘
                      │                        │
                      └───────────┬────────────┘
                                  ▼
                         ┌─────────────────┐
                         │  PDF Generator  │
                         │  (Final Report) │
                         └─────────────────┘

```

---

## 📁 Project Structure

```plaintext
HACKATHON/
├── agents/                        # Intelligent agents for analysis, querying, and content generation
│   ├── __init__.py
│   ├── rag_agent.py              # Uses Gemini + Pinecone to perform RAG-based SEC report analysis
│   ├── stock_data_agent.py       # Uses Alpha Vantage for technical and valuation analysis
│   ├── utils.py                  # Utilities for handling XBRL, HTML, and number formatting
│   └── web_search_agent.py       # Uses SERPAPI to fetch news and industry chain data
│
├── services/                     # Service layer for external APIs
│   ├── __init__.py
│   ├── alpha_vantage_service.py  # Retrieves fundamentals, price history, and financial statements
│   ├── edgar_service.py          # Downloads and parses SEC EDGAR filings into plain text
│   ├── pinecone_service.py       # Interfaces with Pinecone vector database
│   └── web_search_service.py     # Performs Google web search via SERPAPI
│
├── data/
│   └── data_processor.py         # Computes technical indicators, financial ratios, and generates charts
│
├── prompt/
│   └── report_templates.py       # Stores prompt templates used for LLM report generation
│
├── .env                          # Environment variables (e.g., API keys)
├── .gitignore                    # Files and directories to exclude from version control
├── mcp_server.py                 # Main program (can be CLI entry point or backend server)
```

---

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8+
- Pinecone account
- API keys for: Alpha Vantage, Google Gemini, SERPAPI

### 1. Create virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup .env file
Create a .env file in the root directory with the following content:
```bash
# Alpha Vantage
ALPHA_VANTAGE_API_KEY=your_alpha_key

# Google Gemini
GEMINI_API_KEY=your_gemini_key

# SERPAPI (Web Search)
SERPAPI_API_KEY=your_serpapi_key

# SEC EDGAR
EDGAR_USER_NAME=YourName
EDGAR_USER_EMAIL=youremail@example.com

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env

```
### 3. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```
---

## 🚀 Usage
### Running the application
```bash
python mcp_server.py
```

### Generating a stock report
Once the application is running, you can generate a stock report using the FastMCP interface:
1. Select the generate_stock_report tool
2. Enter a stock symbol (e.g., AAPL, MSFT, NVDA)
3. Wait for the report to be generated
4. Download the PDF report when complete
---

## **👨‍💻 Authors**
* Simone Bisen

---
