# Anime Chatbot

A full-stack web application that enables real-time conversations with AI-powered anime characters, featuring voice synthesis and speech recognition capabilities.

## Features

- Real-time chat with AI characters
- Voice synthesis for character responses
- Speech-to-text input support
- Redis caching for improved performance
- Rate limiting and security measures
- Prometheus metrics integration
- Multi-language support
- Responsive web interface

## Tech Stack

### Backend
- FastAPI
- Redis
- SQLite
- Prometheus
- GPT-SoVITS for voice synthesis
- Authentication with OAuth2

### Frontend
- React
- TypeScript
- Tailwind CSS
- Headless UI
- Google Analytics

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Redis server
- FFmpeg

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/anime-chatbot.git
cd anime-chatbot
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Set up environment variables:
Create `.env` files in both backend and frontend directories with the necessary configurations.

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## API Endpoints

- `POST /api/chat/{character_id}` - Send messages to characters
- `POST /api/stt` - Convert speech to text
- `GET /api/characters` - Get available characters
- `GET /api/conversations` - Get chat history
- `GET /api/voice_output/{conversation_id}` - Get synthesized voice output
- `GET /api/metrics` - Prometheus metrics endpoint

## Security Features

- CORS protection
- Rate limiting
- XSS protection
- Security headers
- Input validation
- Trusted host middleware

## Monitoring

The application includes Prometheus metrics for:
- Request counts
- Request latency
- User actions
- System health

## Caching

Redis caching is implemented for:
- Character listings
- Conversation history
- API responses

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) for voice synthesis capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework

---

Note: This project is for educational purposes only. Please ensure you have the necessary rights and permissions before using any character voices or likenesses.