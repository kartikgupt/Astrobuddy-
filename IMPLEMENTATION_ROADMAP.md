# AstroBuddy Web Application - Implementation Roadmap

## Project Overview

This document provides a comprehensive, step-by-step roadmap for implementing a single-page, conversational Vedic Astrology Web Application that combines Kundali API data with Google Gemini AI for personalized astrological guidance.

---

## I. Technical Stack & Architecture

### Frontend Framework
- **React 18** with Vite (modern, fast build tool)
- **No Backend Required** for AI functionality (all Gemini calls are client-side)
- **State Management:** React Context API

### Key Dependencies
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "@google/generative-ai": "^0.2.1"
}
```

### Architecture Pattern
```
┌─────────────────────────────────────────┐
│         Browser (Client-Side)           │
│  ┌───────────────────────────────────┐  │
│  │      React Application            │  │
│  │  ┌──────────┐  ┌──────────────┐ │  │
│  │  │  Forms   │  │  Chat UI     │ │  │
│  │  └──────────┘  └──────────────┘ │  │
│  │  ┌──────────────────────────────┐ │  │
│  │  │   State Management (Context)  │  │
│  │  └──────────────────────────────┘ │  │
│  │  ┌──────────┐  ┌──────────────┐ │  │
│  │  │ Kundali  │  │   Gemini     │ │  │
│  │  │   API    │  │     API      │ │  │
│  │  │ Service  │  │   Service    │ │  │
│  │  └──────────┘  └──────────────┘ │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌──────────────────┐
│  Kundali API    │  │  Google Gemini  │
│  (Backend)      │  │  API (External)  │
│  localhost:8000 │  │  (Client-side)   │
└─────────────────┘  └──────────────────┘
```

---

## II. Data & API Flow (Three Phases)

### Phase 1: Initial Data Collection & Kundali Generation

#### Form 1: Birth Details Collection
**Component:** `BirthDetailsForm.jsx`

**Inputs Collected:**
- Name (text)
- Date of Birth: Year, Month, Day (numbers)
- Time of Birth: Hour, Minute, Second (numbers)
- Place of Birth:
  - Option A: City, State, Country (for geocoding)
  - Option B: Latitude, Longitude (direct coordinates)
- Timezone Offset (optional, auto-detected from country)

**Validation:**
```javascript
- Name: Required, non-empty
- Year: 1900-2100
- Month: 1-12
- Day: 1-31 (with month validation)
- Hour: 0-23
- Minute: 0-59
- Coordinates: -90 to 90 (lat), -180 to 180 (long)
```

**API Call:**
```javascript
POST http://localhost:8000/generate
Body: {
  name, birth_year, birth_month, birth_day,
  birth_hour, birth_minute, birth_second,
  latitude, longitude, city, state, country,
  timezone_offset, include_transits: true
}
```

**State Storage:**
- `birthDetails`: User input data
- `kundaliData`: Complete JSON response from API
- `kundaliLoading`: Loading state
- `kundaliError`: Error messages

---

### Phase 2: API Key Collection & Validation

#### Form 2: Gemini API Key Input
**Component:** `APIKeyForm.jsx`

**Input:**
- Gemini API Key (password field)

**Validation Process:**
1. User enters API key
2. On blur/submit, validate with Gemini API
3. Make test call: `generateContent("Say 'API key is valid'")`
4. If successful, save to `sessionStorage`
5. Mark as valid and proceed

**Security:**
- Stored in `sessionStorage` (cleared on browser close)
- Never sent to any server except Google's Gemini API
- Validated before saving

**State Storage:**
- `geminiApiKey`: Validated API key string
- Stored in: `sessionStorage.getItem('gemini_api_key')`

---

### Phase 3: Conversational Interface & Context Management

#### Chat Interface
**Component:** `ChatInterface.jsx`

**UI Elements:**
- Message history area (scrollable)
- Input textarea
- Send button
- Loading indicators

**Conversation History Management:**
```javascript
// Maintain only last 3 Q&A pairs (6 messages total)
conversationHistory = [
  { question: "Q1", answer: "A1", timestamp: Date },
  { question: "Q2", answer: "A2", timestamp: Date },
  { question: "Q3", answer: "A3", timestamp: Date }
]
// When new Q&A added, remove oldest if > 3 pairs
```

**State Storage:**
- `conversationHistory`: Array of {question, answer, timestamp}
- `messages`: Display array (includes loading states)
- `isProcessing`: Boolean for loading state

---

## III. Gemini Analysis Call - Prompt Construction

### The Four-Part Prompt Structure

When user asks a question, the application constructs a single comprehensive prompt by combining:

#### 1. System Prompt (Master Instruction)
```javascript
const systemPrompt = `You are an Expert Vedic Astrologer with deep knowledge 
of Jyotish (Indian Astrology). Your role is to provide accurate, insightful, 
and personalized astrological guidance based strictly on the provided Kundali 
(birth chart) data.

CRITICAL RULES:
1. Base ALL answers STRICTLY on the provided Kundali data.
2. Reference specific planetary positions, houses, signs, and aspects.
3. Explain astrological concepts clearly but maintain authenticity.
4. If data doesn't contain needed information, clearly state that.
5. Be respectful, ethical, and avoid absolute predictions.
6. Focus on guidance, tendencies, and potential influences.

You will receive:
- Complete Kundali data (D1, D9, aspects, Dasha, transits)
- Previous conversation context (last 3 Q&A pairs)
- Current user question

Analyze the data carefully and provide a comprehensive, data-driven response.`
```

#### 2. Kundali JSON Data
```javascript
const kundaliSection = `
=== KUNDALI DATA (Birth Chart) ===
${JSON.stringify(kundaliData, null, 2)}
`
```

#### 3. Conversation Context (Last 3 Q&A pairs)
```javascript
let contextSection = `
=== PREVIOUS CONVERSATION CONTEXT (Last ${conversationHistory.length} exchanges) ===
`
conversationHistory.forEach((item, index) => {
  contextSection += `
[Exchange ${index + 1}]
User: ${item.question}
You: ${item.answer}
`
})
```

#### 4. Current User Question
```javascript
const questionSection = `
=== CURRENT USER QUESTION ===
${currentQuestion}

Please provide a detailed, data-driven astrological analysis based on the Kundali data above.
`
```

### Final Combined Prompt
```javascript
const fullPrompt = 
  systemPrompt + 
  kundaliSection + 
  contextSection + 
  questionSection
```

### Gemini API Call
```javascript
import { GoogleGenerativeAI } from '@google/generative-ai'

const genAI = new GoogleGenerativeAI(apiKey)
const model = genAI.getGenerativeModel({ model: 'gemini-pro' })
const result = await model.generateContent(fullPrompt)
const response = await result.response
const text = response.text()
```

---

## IV. UI Component Breakdown

### 1. BirthDetailsForm Component

**Location:** `src/components/BirthDetailsForm.jsx`

**Features:**
- Multi-step form with validation
- Toggle between coordinates/place name
- Real-time error display
- Loading state during API call
- Success callback to move to next step

**Key Functions:**
- `handleChange()`: Update form state
- `validate()`: Client-side validation
- `handleSubmit()`: Call Kundali API, store results

---

### 2. APIKeyForm Component

**Location:** `src/components/APIKeyForm.jsx`

**Features:**
- Password input field
- Real-time validation on blur
- Visual feedback (valid/invalid states)
- Security information display
- Link to Google AI Studio

**Key Functions:**
- `validateKey()`: Test API key with Gemini
- `handleBlur()`: Auto-validate on field exit
- `saveApiKey()`: Store in sessionStorage

---

### 3. ChatInterface Component

**Location:** `src/components/ChatInterface.jsx`

**Features:**
- Scrollable message history
- User/AI message differentiation
- Loading indicators
- Error handling
- Auto-scroll to latest message
- Keyboard shortcuts (Enter to send)

**Key Functions:**
- `handleSubmit()`: Process user question
- `getAIResponse()`: Call Gemini with combined prompt
- `addToHistory()`: Maintain last 3 Q&A pairs
- `formatTime()`: Display message timestamps

---

### 4. App Component (Main)

**Location:** `src/App.jsx`

**Features:**
- Step indicator (1, 2, 3)
- Conditional rendering based on state
- Progress tracking
- Reset functionality

**State Flow:**
```
Step 1 → Birth Details → Step 2 → API Key → Step 3 → Chat
```

---

## V. State Management Strategy

### React Context API

**Location:** `src/context/AppContext.jsx`

**Global State:**
```javascript
{
  // Phase 1: Birth & Kundali
  birthDetails: Object | null,
  kundaliData: Object | null,
  kundaliLoading: Boolean,
  kundaliError: String | null,
  
  // Phase 2: API Key
  geminiApiKey: String | null,
  
  // Phase 3: Conversation
  conversationHistory: Array,  // Last 3 Q&A pairs
  isProcessing: Boolean,
  
  // Actions
  setBirthDetails,
  setKundaliData,
  saveApiKey,
  addToHistory,
  clearHistory,
  resetAll
}
```

### State Persistence

- **API Key:** `sessionStorage` (cleared on browser close)
- **Other Data:** React state only (cleared on refresh)
- **No Persistent Storage:** For privacy, data not saved to localStorage

---

## VI. Error Handling

### Network Errors
```javascript
try {
  const response = await fetch(apiUrl)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
} catch (error) {
  if (error.message.includes('fetch')) {
    // Network connection error
    setError('Unable to connect to API. Check server status.')
  }
}
```

### API Key Validation
```javascript
try {
  const result = await validateGeminiApiKey(apiKey)
  if (!result.valid) {
    setError(result.error)
  }
} catch (error) {
  // Handle specific Gemini errors
  if (error.message.includes('API_KEY')) {
    setError('Invalid API key')
  } else if (error.message.includes('quota')) {
    setError('API quota exceeded')
  }
}
```

### Gemini API Errors
```javascript
- Invalid API key
- Quota exceeded
- Safety filter blocks
- Rate limiting
- Network timeouts
```

### User Input Validation
- Form-level validation before submission
- Real-time field validation
- Clear error messages
- Prevent invalid submissions

---

## VII. Security Considerations

### 1. API Key Storage
✅ **Secure:**
- Stored in `sessionStorage` (not `localStorage`)
- Cleared when browser closes
- Never sent to backend server
- Only sent to Google's Gemini API

❌ **Not Secure:**
- Storing in `localStorage` (persists)
- Sending to backend server
- Logging in console
- Including in URLs

### 2. Data Privacy
- Birth details: Stored only in React state
- Kundali data: Stored only in React state
- Conversation history: Stored only in React state
- All data cleared on page refresh

### 3. Client-Side Processing
- All Gemini calls from browser
- No backend proxy required
- Direct communication with Google API
- User controls their own API key

### 4. CORS Considerations
- Kundali API must allow frontend origin
- Gemini API handles CORS automatically
- No CORS issues for client-side calls

---

## VIII. Code Snippets - Key Functions

### Prompt Construction Function
```javascript
// src/services/geminiApi.js

export const constructGeminiPrompt = (kundaliData, conversationHistory, currentQuestion) => {
  // 1. System Prompt
  const systemPrompt = `You are an Expert Vedic Astrologer...`
  
  // 2. Kundali Data
  const kundaliSection = `\n\n=== KUNDALI DATA ===\n${JSON.stringify(kundaliData, null, 2)}\n`
  
  // 3. Conversation Context
  let contextSection = ''
  if (conversationHistory.length > 0) {
    contextSection = `\n\n=== PREVIOUS CONTEXT ===\n`
    conversationHistory.forEach((item, index) => {
      contextSection += `\n[Exchange ${index + 1}]\nUser: ${item.question}\nYou: ${item.answer}\n`
    })
  }
  
  // 4. Current Question
  const questionSection = `\n\n=== CURRENT QUESTION ===\n${currentQuestion}\n\nPlease provide analysis...`
  
  // Combine
  return systemPrompt + kundaliSection + contextSection + questionSection
}
```

### Gemini API Call
```javascript
// src/services/geminiApi.js

export const callGeminiAPI = async (apiKey, prompt) => {
  const genAI = new GoogleGenerativeAI(apiKey)
  const model = genAI.getGenerativeModel({ model: 'gemini-pro' })
  const result = await model.generateContent(prompt)
  const response = await result.response
  return response.text()
}
```

### Conversation History Management
```javascript
// src/context/AppContext.jsx

const addToHistory = useCallback((question, answer) => {
  setConversationHistory((prev) => {
    const newHistory = [...prev, { question, answer, timestamp: new Date() }]
    // Keep only last 3 pairs (6 messages total)
    return newHistory.slice(-3)
  })
}, [])
```

---

## IX. Implementation Checklist

### Phase 1: Setup
- [x] Create React project structure
- [x] Install dependencies
- [x] Set up Vite configuration
- [x] Create base components structure

### Phase 2: State Management
- [x] Create AppContext with all state
- [x] Implement state persistence (API key)
- [x] Add state update functions

### Phase 3: API Services
- [x] Create Kundali API service
- [x] Create Gemini API service
- [x] Implement prompt construction
- [x] Add error handling

### Phase 4: Components
- [x] Build BirthDetailsForm
- [x] Build APIKeyForm
- [x] Build ChatInterface
- [x] Create main App component

### Phase 5: UI/UX
- [x] Add styling and animations
- [x] Implement step indicators
- [x] Add loading states
- [x] Error message display

### Phase 6: Testing
- [ ] Test Kundali API integration
- [ ] Test Gemini API calls
- [ ] Test conversation history
- [ ] Test error scenarios
- [ ] Test on different browsers

---

## X. Deployment Considerations

### Development
```bash
npm run dev
# Runs on http://localhost:3000
```

### Production Build
```bash
npm run build
# Creates optimized build in /dist
```

### Environment Variables
```bash
# .env file
VITE_KUNDALI_API_URL=http://localhost:8000
```

### Static Hosting
- Can be deployed to any static host:
  - Netlify
  - Vercel
  - GitHub Pages
  - AWS S3 + CloudFront

### Backend Requirements
- Kundali API must be running separately
- CORS must be configured for frontend domain
- No backend needed for Gemini (client-side only)

---

## XI. Future Enhancements

1. **Export Functionality:**
   - Download Kundali as PDF
   - Export conversation history

2. **Advanced Features:**
   - Multiple chart comparison
   - Transit predictions
   - Dasha period calendar

3. **UI Improvements:**
   - Dark mode
   - Chart visualization
   - Responsive mobile design

4. **Performance:**
   - Lazy loading
   - Code splitting
   - Caching strategies

---

## XII. Troubleshooting Guide

### Issue: Kundali API Connection Failed
**Solution:**
- Check if API server is running: `python kundali_api.py`
- Verify URL in `.env` file
- Check CORS settings in API

### Issue: Gemini API Key Invalid
**Solution:**
- Verify key at Google AI Studio
- Check for extra spaces/characters
- Ensure key has Gemini Pro access

### Issue: Conversation Context Not Working
**Solution:**
- Check `conversationHistory` state
- Verify `addToHistory` function
- Check prompt construction logic

### Issue: Build Errors
**Solution:**
- Clear `node_modules`: `rm -rf node_modules && npm install`
- Check Node.js version (v16+)
- Verify all dependencies installed

---

## Conclusion

This roadmap provides a complete implementation guide for building the AstroBuddy web application. The architecture ensures:

✅ **Client-Side AI Processing** (no backend needed)  
✅ **Secure API Key Handling** (sessionStorage only)  
✅ **Comprehensive Context** (Kundali + History + Prompt)  
✅ **Modern UI/UX** (React + Vite)  
✅ **Error Handling** (comprehensive validation)  
✅ **Privacy** (no persistent storage)

The application is ready for development and can be extended with additional features as needed.

