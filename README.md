# Fair Price Application

A Flask-based web application for managing tradesmen, groups, and job tracking.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fair-price
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your settings
   nano .env
   ```

5. **Initialize the database**
   ```bash
   python sql/init_db.py
   python sql/load_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## ⚙️ Configuration

The application uses a flexible configuration system that supports multiple environments:

### Environment Variables

Copy `env.example` to `.env` and configure the following variables:

```bash
# Flask Environment
FLASK_ENV=development  # Options: development, production, testing

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE=application.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Configuration Classes

The application supports three configuration modes:

- **Development**: Debug mode, detailed logging, development database
- **Production**: Optimized for production, requires SECRET_KEY
- **Testing**: In-memory database, CSRF disabled

### Environment-Specific Settings

#### Development
```bash
export FLASK_ENV=development
python app.py
```

#### Production
```bash
export FLASK_ENV=production
export SECRET_KEY="your-production-secret-key"
python app.py
```

#### Testing
```bash
export FLASK_ENV=testing
python -m pytest
```

## 🗄️ Database Management

### Initialize Database
```bash
python sql/init_db.py
```

### Load Sample Data
```bash
python sql/load_db.py
```

### Check Database
```bash
python sql/check_db.py
```

### Reset Database
```bash
# Windows
scripts\reset_db.bat

# Linux/Mac
./scripts/reset_db.sh
```

## 🧪 Testing

Run the test suite:
```bash
python run_tests.py
```

Run specific tests:
```bash
python run_tests.py --service database
python run_tests.py --verbose
```

## 📁 Project Structure

```
fair-price/
├── app/
│   ├── routes/          # Route handlers
│   ├── services/        # Business logic
│   └── config.py        # App configuration
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── sql/                # Database scripts
├── logs/               # Application logs
├── config.py           # Main configuration
├── app.py              # Application factory
├── requirements.txt    # Dependencies
└── env.example         # Environment template
```

## 🔧 Development

### Code Organization

The application follows a service-oriented architecture:

- **Routes**: Handle HTTP requests and responses
- **Services**: Contain business logic and database operations
- **Configuration**: Environment-based settings management

### Adding New Features

1. Create service methods in appropriate service classes
2. Add route handlers in route modules
3. Update templates as needed
4. Add tests for new functionality

### Database Operations

All database operations go through service classes:

```python
from app.services.user_service import UserService

user_service = UserService()
users = user_service.get_all_users()
```

## 🚨 Troubleshooting

### Common Issues

**Application won't start**
- Check if database exists: `python sql/check_db.py`
- Verify configuration: Check `.env` file
- Check logs: `tail -f logs/app.log`

**Database errors**
- Reset database: `scripts/reset_db.sh`
- Check schema: `python sql/check_db.py`

**Import errors**
- Ensure virtual environment is activated
- Check Python path: `python -c "import sys; print(sys.path)"`

### Logs

Application logs are stored in `logs/app.log`. Check this file for detailed error information.

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
