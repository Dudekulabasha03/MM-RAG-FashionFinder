# Style Finder - Fashion Style Analyzer

A fashion style analyzer that combines computer vision, vector similarity, and local LLM models to provide detailed fashion analysis.

## 🚀 Recent Updates

**IBM Watson AI → Local Ollama Integration**
- ✅ Replaced IBM Watson AI with local Ollama LLM service
- ✅ Now uses `llama3.2:3b` model for fashion analysis
- ✅ No more API keys or external dependencies required
- ✅ Faster response times and offline capability

## 🏗️ Architecture

The application consists of several key components:

- **Image Processing**: ResNet50-based image encoding and similarity matching
- **LLM Service**: Local Ollama integration for fashion analysis
- **Web Interface**: Gradio-based user interface
- **Data Processing**: Pandas-based dataset management

## 📋 Prerequisites

- Python 3.8+
- Ollama installed and running locally
- `llama3.2:3b` model downloaded

## 🛠️ Installation & Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Ollama

#### Option A: Automated Setup (Recommended)
```bash
python setup_ollama.py
```

#### Option B: Manual Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull the required model
ollama pull llama3.2:3b
```

### 3. Verify Ollama Setup

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Should return available models including llama3.2:3b
```

## 🚀 Running the Application

### 1. Start Ollama Service
```bash
ollama serve
```

### 2. Test Ollama Integration (Optional but Recommended)
```bash
python test_ollama.py
```

### 3. Run the Style Finder App
```bash
python app.py
```

### 4. Access the Web Interface
Open your browser and navigate to: `http://127.0.0.1:7070`

## 🔧 Configuration

Edit `config.py` to customize:

- **Ollama Model**: Change `OLLAMA_MODEL_NAME` to use different models
- **Ollama URL**: Modify `OLLAMA_BASE_URL` if running on different port/host
- **Image Processing**: Adjust `IMAGE_SIZE`, normalization parameters
- **Similarity Threshold**: Modify `SIMILARITY_THRESHOLD`

## 📁 Project Structure

```
style-finder/
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── setup_ollama.py       # Ollama setup script
├── test_ollama.py        # Ollama integration test script
├── models/
│   ├── image_processor.py # Image processing and encoding
│   └── llm_service.py    # Ollama LLM service
├── utils/
│   └── helpers.py        # Utility functions
├── examples/              # Sample images for testing
└── requirements.txt       # Python dependencies
```

## 🎯 Features

- **Image Upload**: Drag & drop or click to upload fashion images
- **Style Analysis**: AI-powered fashion element detection
- **Similar Item Matching**: Find visually similar items in database
- **Detailed Descriptions**: Comprehensive fashion analysis and recommendations
- **Example Images**: Built-in examples for testing

## 🔍 How It Works

1. **Image Upload**: User uploads a fashion image
2. **Image Encoding**: Image is converted to feature vector using ResNet50
3. **Similarity Matching**: Finds closest match in pre-computed dataset
4. **LLM Analysis**: Local Ollama model generates detailed fashion analysis
5. **Response Formatting**: Results are formatted and displayed to user

## 🐛 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama service
pkill ollama
ollama serve
```

### Model Not Found
```bash
# List available models
ollama list

# Pull the required model
ollama pull llama3.2:3b
```

### Port Already in Use
```bash
# Check what's using port 11434
lsof -i :11434

# Kill the process and restart Ollama
kill -9 <PID>
ollama serve
```

## 🔄 Migration from IBM Watson AI

If you were previously using IBM Watson AI:

1. **Removed Dependencies**: `ibm-watsonx-ai` package removed
2. **Updated Service**: `LlamaVisionService` → `OllamaService`
3. **Configuration Changes**: Updated `config.py` for Ollama settings
4. **API Changes**: No more API keys or external authentication

## 📝 Notes

- **Performance**: Local Ollama provides faster response times
- **Offline Capability**: Works without internet connection once model is downloaded
- **Resource Usage**: `llama3.2:3b` requires ~2GB RAM and ~2GB disk space
- **Model Quality**: 3B parameter model provides good balance of speed and quality

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
# MM-RAG-FashionFinder
# MM-RAG-FashionFinder
# MM-RAG-FashionFinder
# MM-RAG-FashionFinder
# MM-RAG-FashionFinder
