# AstroBuddy - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Start Kundali API Server

```bash
# In the main project directory
python kundali_api.py
```

API will run on `http://localhost:8000`

### Step 2: Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will open at `http://localhost:3000`

### Step 3: Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the API key

### Step 4: Use the Application

1. **Enter Birth Details:**
   - Fill in name, date, time, location
   - Click "Generate Kundali"
   - Wait for chart generation

2. **Enter API Key:**
   - Paste your Gemini API key
   - Click "Validate & Save Key"
   - Key is validated automatically

3. **Start Chatting:**
   - Ask questions about your Kundali
   - Get AI-powered astrological insights
   - Conversation history maintained (last 3 exchanges)

## 📋 Example Questions

- "What is my current Dasha period and what does it mean?"
- "Tell me about my planetary positions in different houses"
- "What are the key aspects in my birth chart?"
- "How will my current transit affect my career?"
- "Explain the significance of my Ascendant sign"

## 🔧 Configuration

### Change Kundali API URL

Create `.env` file in `frontend/` directory:

```env
VITE_KUNDALI_API_URL=http://your-api-url:8000
```

### Production Build

```bash
npm run build
npm run preview
```

## ⚠️ Troubleshooting

### API Connection Error
- Ensure Kundali API is running: `python kundali_api.py`
- Check if port 8000 is available
- Verify `.env` file has correct URL

### Invalid API Key
- Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check for extra spaces in key
- Ensure key has Gemini Pro access

### Build Errors
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Documentation

- **Full Implementation Roadmap:** See `IMPLEMENTATION_ROADMAP.md`
- **API Documentation:** See `API_README.md`
- **Frontend README:** See `frontend/README.md`

## 🎯 Key Features

✅ **Client-Side AI** - All Gemini calls from browser  
✅ **Secure Storage** - API key in sessionStorage only  
✅ **Complete Context** - Kundali + History + System Prompt  
✅ **Modern UI** - Beautiful, responsive design  
✅ **Error Handling** - Comprehensive validation  

## 🔒 Security Notes

- API key stored only in browser session
- Cleared when browser closes
- Never sent to any server except Google's API
- All data cleared on page refresh

---

**Ready to start?** Run the commands above and open `http://localhost:3000`!

