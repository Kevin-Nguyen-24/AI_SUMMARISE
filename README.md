# AI Summarization Server

**Local GPU-powered document summarization service using Ollama and RTX 5090**

A production-grade backend API that summarizes PDF, DOCX, and TXT documents using local LLM inference on your NVIDIA GPU. All processing happens on your machine—no cloud, no external APIs.

---

## 🎯 Features

- **Local GPU Inference**: Uses Ollama with NVIDIA RTX 5090
- **Multiple File Formats**: PDF, DOCX, TXT support
- **Hierarchical Summarization**: Handles documents of any length (100+ pages)
- **Dual Output**: Bullet points + detailed paragraph summary
- **REST API**: Clean JSON responses
- **Production Ready**: Logging, error handling, validation
- **Remote Access**: Can be accessed via VPN or local network

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, WSL2, or Windows
- **GPU**: NVIDIA RTX 5090 (or compatible GPU)
- **Python**: 3.10 or higher
- **Ollama**: Installed and running locally

### Install Ollama
```bash
# Linux/WSL
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai
```

### Pull the Model
```bash
ollama pull qwen2.5:7b
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

---

## 🚀 Installation

### 1. Clone or Navigate to Project
```bash
cd "C:\projects\Summarise\AI Server"
```

### 2. Create Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/WSL
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (defaults work for standard Ollama setup)
```

**.env Configuration:**
```ini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=120
MAX_FILE_SIZE_MB=20
ALLOWED_EXTENSIONS=pdf,docx,txt
CHUNK_SIZE=3000
CHUNK_OVERLAP=300
LOG_LEVEL=INFO
```

---

## 🏃 Running the Server

### Development Mode
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Using Python Directly
```bash
python app/main.py
```

The server will start at: **http://localhost:8000**

---

## 📡 API Usage

### Endpoint: `POST /summarize`

**Request:**
```bash
curl -X POST http://localhost:8000/summarize \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "file_name": "report.pdf",
  "file_type": "pdf",
  "summary_short": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ],
  "summary_detailed": "This document discusses...",
  "model": "qwen2.5:7b",
  "processing_time_sec": 22.4
}
```

**Error Response:**
```json
{
  "error": "Unsupported file type"
}
```

### Health Check: `GET /health`
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "server": "healthy",
  "ollama": "healthy",
  "ollama_url": "http://localhost:11434",
  "model": "qwen2.5:7b"
}
```

### Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🧪 Testing

### Test with Sample Files

**1. Create a test text file:**
```bash
echo "This is a test document. It contains some sample text for testing the summarization API. The content should be long enough to generate a meaningful summary." > test.txt
```

**2. Test the API:**
```bash
curl -X POST http://localhost:8000/summarize -F "file=@test.txt"
```

### Test with Different File Types

**PDF:**
```bash
curl -X POST http://localhost:8000/summarize -F "file=@document.pdf"
```

**DOCX:**
```bash
curl -X POST http://localhost:8000/summarize -F "file=@report.docx"
```

### Test Error Handling

**Unsupported file type:**
```bash
curl -X POST http://localhost:8000/summarize -F "file=@image.jpg"
```

**File too large:** (Create a file > 20MB)
```bash
curl -X POST http://localhost:8000/summarize -F "file=@large_file.pdf"
```

---

## 🌐 Remote Access

### Option 1: Local Network Access
```bash
# Find your local IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# Access from another device on same network
curl -X POST http://192.168.1.100:8000/summarize -F "file=@doc.pdf"
```

### Option 2: VPN Access (Recommended)
Set up VPN to securely access your server remotely.

### Option 3: Port Forwarding
Configure your router to forward port 8000 to your machine.

**⚠️ Security Note:** Use firewall rules and consider adding API key authentication for external access.

---

## 📊 Performance Benchmarks

| Document Size | Processing Time | Chunks |
|--------------|-----------------|--------|
| 10 pages     | ~8s             | 1-2    |
| 30 pages     | ~15s            | 3-5    |
| 100 pages    | ~30s            | 10-15  |

*Times may vary based on GPU, model, and document complexity*

---

## 🗂️ Project Structure

```
ai-server/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── summarize.py        # Summarization endpoint
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py     # File upload/management
│   │   ├── text_extractor.py   # Extract text from files
│   │   ├── chunker.py          # Text chunking
│   │   ├── ollama_client.py    # Ollama API client
│   │   └── summarizer.py       # Hierarchical summarization
│   │
│   └── utils/
│       ├── __init__.py
│       └── validators.py       # Input validation
│
├── temp/uploads/               # Temporary file storage
├── logs/                       # Application logs
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Configuration

### Human-Like Summarization
Adjust how natural and conversational summaries are:
```ini
SUMMARY_TEMPERATURE=0.7  # 0.0-1.0 scale
```
- **0.0-0.3**: Very factual, precise (technical docs)
- **0.4-0.6**: Balanced
- **0.7-0.8**: Natural, human-like (recommended)
- **0.9-1.0**: Very creative, informal

**See `HUMAN_LIKE_SUMMARIZATION.md` for detailed guide**

### Adjusting Chunk Size
Edit `.env`:
```ini
CHUNK_SIZE=3000        # Increase for longer context
CHUNK_OVERLAP=300      # Overlap between chunks
```

### Changing Model
```bash
# Pull a different model
ollama pull llama2:13b

# Update .env
OLLAMA_MODEL=llama2:13b
```

### Increasing File Size Limit
Edit `.env`:
```ini
MAX_FILE_SIZE_MB=50
```

---

## 📝 Logging

Logs are stored in `logs/` directory:
- **File**: `logs/server_YYYYMMDD.log`
- **Console**: Real-time output
- **Format**: Timestamp, level, message

View logs:
```bash
tail -f logs/server_*.log
```

---

## 🐛 Troubleshooting

### Ollama Connection Error
```
✗ Ollama service is not available
```
**Solution:**
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Start Ollama: `ollama serve`
3. Verify model is installed: `ollama list`

### Model Not Found
```
⚠ Configured model 'qwen2.5:7b' not found
```
**Solution:**
```bash
ollama pull qwen2.5:7b
```

### GPU Not Being Used
**Check GPU usage:**
```bash
nvidia-smi
```
Ollama automatically uses GPU if available. Check Ollama logs.

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
```bash
pip install -r requirements.txt
```

### Port Already in Use
```
ERROR: [Errno 48] Address already in use
```
**Solution:**
```bash
# Use different port
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

## 🔐 Security Considerations

### For Production Deployment:
1. **API Key Authentication**: Add API key validation
2. **Rate Limiting**: Implement request rate limits
3. **HTTPS**: Use reverse proxy (nginx) with SSL
4. **Firewall**: Restrict access to specific IPs
5. **Input Sanitization**: Already implemented
6. **File Size Limits**: Already enforced

### Example nginx Configuration:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🎯 Next Steps

- [ ] Add API key authentication
- [ ] Implement request rate limiting
- [ ] Add support for more file formats (HTML, EPUB)
- [ ] Create batch processing endpoint
- [ ] Add custom summarization styles
- [ ] Build frontend UI
- [ ] Implement caching for repeated documents
- [ ] Add multi-language support

---

## 📄 License

This project is for personal/internal use. Modify as needed for your requirements.

---

## 🤝 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify Ollama is running and model is loaded
3. Test with simple text file first
4. Check GPU availability with `nvidia-smi`

---

## ✅ Acceptance Criteria

- [x] API reachable remotely
- [x] Files uploaded successfully
- [x] GPU used by Ollama
- [x] Accurate summaries
- [x] Clean JSON output
- [x] Error handling
- [x] Logging implemented
- [x] Production-ready code

---

**Built with FastAPI, Ollama, and NVIDIA RTX 5090** 🚀
