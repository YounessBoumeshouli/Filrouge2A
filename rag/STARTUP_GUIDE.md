# RAG API Startup Guide

## Port Conflict Issue Fixed! 🔧

The error you encountered means port 8001 was already in use. Here are the solutions:

## Quick Start Options

### Option 1: Auto Port Detection (Recommended)
```bash
start_rag_simple.bat
```
- Automatically finds available port (8002, 8003, etc.)
- No port conflicts
- Clean startup

### Option 2: Direct Command (Port 8002)
```bash
start_rag_direct.bat
```
- Uses port 8002 directly
- Simple and reliable

### Option 3: Check Ports First
```bash
python check_ports.py
```
Then use any startup script.

## If Ports Are Still Busy

### Kill Running Servers
```bash
kill_servers.bat
```
This will stop any servers running on ports 8001-8003.

### Manual Port Check
```bash
netstat -ano | findstr :8001
netstat -ano | findstr :8002
```

## API Endpoints

Once running, your API will be available at:
- **Health Check**: `http://localhost:8002/health`
- **Query**: `POST http://localhost:8002/query`

## Test the API

```bash
python test_rag_api.py
```
(Update the BASE_URL to match your port)

## Integration Example

```javascript
// Update port to match your running server
const queryRAG = async (question) => {
  const response = await fetch('http://localhost:8002/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: question, k: 5 })
  });
  return await response.json();
};
```

## Troubleshooting

1. **Port in use**: Run `kill_servers.bat` or use `start_rag_simple.bat`
2. **Ollama not running**: Run `ollama serve` in another terminal
3. **Model not found**: Run `ollama pull gemma2:2b`
4. **Import errors**: The script will auto-install dependencies

## Success Indicators

✅ You should see:
```
Starting RAG API server on http://localhost:8002
INFO: Uvicorn running on http://0.0.0.0:8002
INFO: Application startup complete.
```

❌ No more:
```
ERROR: [Errno 10048] error while attempting to bind
```