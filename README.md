# Luxe Stays India - Multi-Platform Deployment

A Django-based web application for luxury hospitality content creation and social media marketing, configured for deployment on multiple platforms.

## 🌟 Project Overview

Luxe Stays India is a professional website showcasing luxury hospitality content creation services, featuring:
- Dynamic property showcases from Excel data
- Instagram API integration
- Contact form with email notifications
- Responsive design with Tailwind CSS
- Professional animations and UX

## 🏗️ Branching Strategy

This project uses a multi-branch strategy for different deployment platforms:

### 📋 Branch Structure

| Branch | Purpose | Platform | Configuration |
|--------|---------|----------|---------------|
| `master` | Production (Railway) | Railway.com | Full features, file-based cache |
| `vercel` | Production (Vercel) | Vercel.com | Serverless optimized, memory cache |
| `develop` | Development | Local/Testing | Development settings, debug enabled |

## 🚀 Deployment Options

### 1. Railway Deployment (Paid Service)
- **Branch**: `master`
- **Features**: Full functionality, file uploads, persistent storage
- **Best for**: When you have Railway subscription active

```bash
# Deploy to Railway
git checkout master
git push origin master
# Connect to Railway from GitHub
```

### 2. Vercel Deployment (Free Tier)
- **Branch**: `vercel`
- **Features**: Serverless optimized, static file CDN
- **Best for**: Free hosting when Railway subscription is inactive

```bash
# Deploy to Vercel
git checkout vercel
git push origin vercel
# Connect to Vercel from GitHub
```

### 3. Development
- **Branch**: `develop`
- **Features**: Debug mode, development tools
- **Best for**: Local development and testing

```bash
# Development setup
git checkout develop
python manage.py runserver
```

## 🔧 Key Differences Between Branches

### Master Branch (Railway)
- Uses `requirements.txt` (full dependencies)
- Uses `settings.py` (Railway-optimized)
- File-based caching
- Full database functionality
- File upload support

### Vercel Branch
- Uses `requirements-vercel.txt` (optimized dependencies)
- Uses `settings_vercel.py` (serverless optimized)
- Memory-based caching
- SQLite database (read-only in production)
- Limited file upload support

## 📦 Technology Stack

- **Backend**: Django 5.0.6
- **Frontend**: Tailwind CSS 4.0
- **Database**: SQLite (configurable)
- **Cache**: File-based (Railway) / Memory (Vercel)
- **Static Files**: WhiteNoise
- **Email**: SMTP (GoDaddy)
- **APIs**: RapidAPI Instagram

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js (for Tailwind CSS)
- Git

### Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/luxe-stays.git
cd luxe-stays

# Checkout development branch
git checkout develop

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## 🔄 Switching Between Deployments

### From Railway to Vercel
```bash
# When Railway subscription expires
git checkout vercel
git push origin vercel
# Update Vercel deployment settings
```

### From Vercel to Railway
```bash
# When Railway subscription is active again
git checkout master
git push origin master
# Update Railway deployment settings
```

## 📋 Environment Variables

### Required for All Deployments
```
SECRET_KEY=your-secret-key
DEBUG=False
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
RAPIDAPI_KEY=your-rapidapi-key
RAPIDAPI_HOST=instagram120.p.rapidapi.com
```

### Railway-Specific
```
DATABASE_URL=your-database-url
```

### Vercel-Specific
```
DJANGO_SETTINGS_MODULE=luxestays_project.settings_vercel
```

## 🎯 Features

- **Dynamic Content**: Excel-based property showcase
- **Social Media Integration**: Instagram followers, highlights, reels
- **Contact Management**: Form handling with email notifications
- **Responsive Design**: Mobile-first approach
- **Performance Optimized**: Caching and static file optimization
- **SEO Ready**: Meta tags and structured content

## 📁 Project Structure

```
luxestays/
├── luxestays_project/     # Django project settings
│   ├── settings.py        # Railway settings
│   ├── settings_vercel.py # Vercel settings
│   └── wsgi_vercel.py     # Vercel WSGI
├── website/               # Main Django app
├── templates/             # HTML templates
├── static/                # Static files
├── requirements.txt       # Railway dependencies
├── requirements-vercel.txt # Vercel dependencies
├── vercel.json           # Vercel configuration
├── Procfile              # Railway configuration
└── README-VERCEL.md      # Vercel-specific docs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch from `develop`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary to Luxe Stays India.

## 🆘 Support

For deployment issues:
- **Railway**: Check Railway logs and documentation
- **Vercel**: Check Vercel deployment logs
- **Development**: Check Django debug output

---

**Note**: This project is designed to be flexible between paid and free hosting services, allowing you to switch based on your subscription status. 