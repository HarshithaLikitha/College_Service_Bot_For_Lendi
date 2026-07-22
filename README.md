# 🎓 College Service Bot

A complete AI-powered chatbot for answering student queries about college information using Python Flask backend, Gemini API for NLP, and a modern web interface.

## 📋 Features

- **Academic Information**: Block locations, lab details, department info
- **Faculty Details**: HOD information, contact details, specializations
- **Administration**: Principal, Dean, Exam Cell, Fees Office, Scholarship Cell
- **Facilities**: Hostel, Transport, Canteen, Library, Sports Complex
- **General Information**: College details, courses, placements

## 🏗️ Project Structure

```
college-service-bot/
│
├── backend/
│   ├── app.py              # Flask backend with Gemini integration
│   └── requirements.txt    # Python dependencies
│
├── data/
│   └── info.json          # College information database
│
├── frontend/
│   ├── index.html         # Chat interface
│   ├── style.css          # Styling
│   └── script.js          # Frontend logic
│
└── README.md              # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Gemini API Key (Get it from: https://makersuite.google.com/app/apikey)

### Step 1: Clone/Download the Project
```bash
mkdir college-service-bot
cd college-service-bot
```

### Step 2: Set Up Backend
```bash
# Create backend directory
mkdir backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key (IMPORTANT!)
# Option 1: Set environment variable (Recommended)
export GEMINI_API_KEY="your_api_key_here"  # On Linux/Mac
set GEMINI_API_KEY=your_api_key_here       # On Windows

# Option 2: Or edit app.py and replace YOUR_API_KEY_HERE with your actual key
```

### Step 3: Create Data Directory
```bash
# Go back to project root
cd ..

# Create data directory and add info.json
mkdir data
# Copy the info.json content from the provided file
```

### Step 4: Set Up Frontend
```bash
# Create frontend directory
mkdir frontend
# Copy index.html, style.css, and script.js to this directory
```

### Step 5: Run the Application

**Terminal 1 - Start Backend:**
```bash
cd backend
python app.py
# Server will start on http://localhost:5000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
# Option 1: Using Python's built-in server
python -m http.server 8000

# Option 2: Using Node.js http-server (if installed)
npx http-server -p 8000

# Option 3: Simply open index.html in your browser
```

### Step 6: Access the Application
Open your browser and go to:
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000/health (to verify backend is running)

## 🧪 Testing Queries

Try these example queries:

### Academic Queries
- "Where is CSIT block?"
- "Tell me about CSE block"
- "Where are the computer labs?"
- "What facilities are in main block?"

### Faculty Queries
- "Who is HOD of CSE?"
- "Who is HOD of CSIT?"
- "Contact details of CSE department"
- "Tell me about mechanical department"

### Administration Queries
- "Who is the principal?"
- "Where is exam cell?"
- "How to pay fees?"
- "Tell me about scholarships"

### Facilities Queries
- "Is there girls hostel?"
- "Tell me about boys hostel"
- "Transport facility details"
- "Library timings"
- "Canteen information"

### General Queries
- "When was college established?"
- "What courses are offered?"
- "Tell me about placements"
- "Top recruiters"

## 🔧 Configuration

### Changing API Key
Edit `backend/app.py`:
```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_NEW_KEY_HERE')
```

### Updating College Data
Edit `data/info.json` to add/modify college information. Follow the existing JSON structure.

### Changing Backend Port
In `backend/app.py`:
```python
app.run(debug=True, port=5000)  # Change port here
```

In `frontend/script.js`:
```javascript
const API_URL = 'http://localhost:5000/chat';  # Update port here
```

## 🐛 Troubleshooting

### Backend Issues

**Problem: "CORS error"**
- Make sure flask-cors is installed: `pip install flask-cors`
- Check that CORS(app) is in app.py

### Frontend Issues

**Problem: "Failed to fetch" error**
- Ensure backend is running on http://localhost:5000
- Check browser console for detailed error
- Verify the API_URL in script.js matches backend port

**Problem: Chat interface not loading**
- Make sure all three files (index.html, style.css, script.js) are in the frontend folder
- Check browser console for errors
- Try opening index.html directly in browser

### Connection Issues

**Problem: Backend and Frontend can't communicate**
1. Verify backend is running: Visit http://localhost:5000/health
2. Check if you see {"status": "ok", "message": "College Service Bot is running"}
3. Make sure CORS is enabled in backend
4. Try disabling browser extensions that might block requests

## 📊 API Endpoints

### POST /chat
Send a message to the bot
```json
Request:
{
  "message": "Where is CSE block?"
}

Response:
{
  "reply": "**CSE Block:** {location: North Campus, Building A, ...}",
  "category": "academic",
  "debug": {...}
}
```

### GET /health
Check if backend is running
```json
Response:
{
  "status": "ok",
  "message": "College Service Bot is running"
}
```

## 🔄 How It Works

1. **User Input**: Student types a query in the chat interface
2. **Frontend**: Sends query to Flask backend via POST request
3. **Gemini API**: Extracts keywords, category, and intent from query
4. **Database Search**: Searches info.json for relevant information
5. **Response Formatting**: Formats results into natural language
6. **Display**: Shows formatted response in chat interface

## 🎨 Customization Ideas

### Change Theme Colors
Edit `frontend/style.css`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 /* Change to your college colors */
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### Add More Quick Questions
Edit `frontend/index.html`:
```html
<button class="quick-btn" data-question="Your question">Button Text</button>
```

### Expand Database
Edit `data/info.json` to add new categories:
```json
{
  "new_category": {
    "item1": "details",
    "item2": "more details"
  }
}
```

## 🚀 Future Improvements

### Phase 1 (Easy)
- [ ] Add typing indicator animation
- [ ] Implement message timestamps
- [ ] Add "clear chat" button
- [ ] Voice input support
- [ ] Dark mode toggle

### Phase 2 (Medium)
- [ ] User authentication system
- [ ] Save chat history to database
- [ ] Multi-language support
- [ ] Image recognition for campus maps
- [ ] Mobile app version (React Native)

### Phase 3 (Advanced)
- [ ] Replace JSON with SQL/MongoDB database
- [ ] Add admin panel for updating information
- [ ] Implement feedback system
- [ ] Analytics dashboard
- [ ] Integration with college ERP system
- [ ] WhatsApp/Telegram bot integration
- [ ] Push notifications for important updates
- [ ] AI-powered personalized recommendations

### Enhanced Features
- [ ] **Context Awareness**: Remember previous questions in conversation
- [ ] **Smart Suggestions**: Suggest related questions based on current query
- [ ] **File Upload**: Accept and process documents (PDFs, images)
- [ ] **Calendar Integration**: Show exam schedules, events
- [ ] **Map View**: Interactive campus map
- [ ] **Multilingual**: Support regional languages
- [ ] **Voice Output**: Text-to-speech responses
- [ ] **Sentiment Analysis**: Detect student mood and respond appropriately

## 📱 Deployment Options

### Option 1: Local Network (College WiFi)
- Deploy on college server
- Access via local IP: http://192.168.x.x:5000

### Option 2: Cloud Deployment

**Backend (Python Flask)**
- Heroku
- Railway.app
- PythonAnywhere
- AWS EC2
- Google Cloud Run

**Frontend**
- Netlify
- Vercel
- GitHub Pages
- Firebase Hosting

### Option 3: Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "backend/app.py"]
```

## 🔒 Security Considerations

1. **API Key Protection**: Never commit API keys to Git
2. **Input Validation**: Sanitize user inputs
3. **Rate Limiting**: Implement rate limiting for API calls
4. **HTTPS**: Use HTTPS in production
5. **Authentication**: Add user authentication for sensitive data

## 📝 Database Schema (Future SQL Migration)

When migrating to SQL, use this schema:
```sql
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    description TEXT
);

CREATE TABLE information (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT,
    key_name VARCHAR(200),
    value TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available for educational purposes.

## 👥 Support

For issues or questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gemini API Guide](https://ai.google.dev/tutorials/python_quickstart)
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

## ✅ Checklist Before Running

- [ ] Python 3.8+ installed
- [ ] Gemini API key obtained
- [ ] All dependencies installed via pip
- [ ] info.json file created in data folder
- [ ] API key set in environment variable or app.py
- [ ] Backend running on port 5000
- [ ] Frontend accessible on port 8000
- [ ] CORS enabled in backend
- [ ] Browser allows localhost connections

## 🎉 Success Metrics

Your bot is working correctly if:
- ✅ Backend health check returns "ok" status
- ✅ Chat interface loads without errors
- ✅ Messages send and receive responses
- ✅ Responses are relevant to queries
- ✅ Quick questions work properly
- ✅ No CORS errors in browser console

---

**Made with ❤️ for Students**

Happy Coding! 🚀
```