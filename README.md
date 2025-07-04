# Fair Price Jobs
#### Video Demo:  https://www.youtube.com/watch?v=vg5jIKvffYA
#### Description:

This project was developed to address a real life headache faced by anyone who wants to renovate a property in the South of France (where I live).
Finding a reasonably priced tradesman to lay tiles, do the electrics, check the roof etc. is very difficult.

The idea is to build a platform where friends can share information on jobs that they have had done:
- contact details of the tradesman, pricing, rating, job description etc.

Anyone can register and create a group or search for an existing group. Groups are associated with postcodes.
To join an existing group will require approval from that groups owner.

Once joined the user can see the different members and the tradesmen who have been entered along with the jobs they have done.


### Design choices

I worked outside the cs50.dev environment for this project
I used flask, html with bootstrap and sqlite3
In addition to files below I wrote some sql scripts to reset the database and enter dummy data
The social group aspect was more complex than I originally anticipated


## 📁 Project Structure

```
fair-price/
├── app/                    # Main application
│   ├── routes/            # Route handlers (auth, groups, tradesmen, jobs, etc.)
│   ├── services/          # Business logic (UserService, GroupService, etc.)
│   └── config.py          # Configuration
├── templates/             # HTML templates
│   ├── layout.html        # Base layout template
│   ├── index.html         # Homepage
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   └── ...                # Other templates
├── static/               # CSS, JavaScript, images
├── sql/                  # Database scripts
│   ├── init_db.py        # Initialize database
│   ├── load_db.py        # Load sample data
│   └── schema.sql        # Database schema
├── docs/                 # 📚 Documentation
│   ├── README.md         # Documentation index
│   ├── DEVELOPER_GUIDE.md # Developer quick reference
│   ├── USEFUL_COMMANDS.md # Command reference
│   └── TEST_README.md    # Testing guide
├── scripts/              # 🔧 Utility scripts
│   ├── *.bat            # Windows scripts
│   └── *.sh             # Linux/Mac scripts
├── logs/                 # Application logs
├── tests/                # 🧪 Test files
│   └── test_app.py       # Test suite
├── run_tests.py          # Test runner
└── app.py               # Main application entry point
```

## 🚀 Quick Start

### For Developers
1. **Setup**: See [Developer Guide](docs/DEVELOPER_GUIDE.md)
2. **Testing**: See [Test Documentation](docs/TEST_README.md)
3. **Commands**: See [Useful Commands](docs/USEFUL_COMMANDS.md)

### For Users
1. **Install**: `pip install -r requirements.txt`
2. **Setup**: `python sql/init_db.py`
3. **Run**: `python app.py`
4. **Access**: http://localhost:5000

## 📚 Documentation

- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Quick reference for developers
- **[Useful Commands](docs/USEFUL_COMMANDS.md)** - Comprehensive command reference
- **[Test Documentation](docs/TEST_README.md)** - Complete testing guide
- **[Scripts Documentation](scripts/README.md)** - Utility scripts guide

## 🔧 Utility Scripts

### Windows
```cmd
scripts\reset_db.bat      # Reset database
scripts\quick_test.bat    # Run quick tests
scripts\backup_db.bat     # Backup database
scripts\cleanup.bat       # Clean up files
```

### Linux/Mac
```bash
./scripts/reset_db.sh     # Reset database
./scripts/quick_test.sh   # Run quick tests
./scripts/backup_db.sh    # Backup database
./scripts/cleanup.sh      # Clean up files
```

## 🗄️ Database Schema

The application uses SQLite with the following tables:
- **users**: User information and credentials
- **groups**: Group information with postcodes
- **user_groups**: User-group memberships and statuses
- **tradesmen**: Tradesman details and contact information
- **group_tradesmen**: Group-tradesman associations
- **jobs**: Job records with pricing and ratings
