# Luxe Stays India - Vercel Deployment

This branch is specifically configured for deployment on Vercel.

## 🚀 Vercel Deployment Features

- **Serverless Architecture**: Optimized for Vercel's serverless functions
- **Static File Optimization**: Uses WhiteNoise for efficient static file serving
- **Memory Cache**: Uses LocMemCache instead of file-based cache
- **Vercel-specific Settings**: Custom settings file for Vercel environment

## 📋 Key Differences from Railway Branch

1. **Requirements**: Uses `requirements-vercel.txt` (lighter dependencies)
2. **Settings**: Uses `settings_vercel.py` (optimized for serverless)
3. **WSGI**: Uses `wsgi_vercel.py` (Vercel-specific configuration)
4. **Cache**: Memory-based cache instead of file-based
5. **Static Files**: Optimized for Vercel's CDN

## 🔧 Environment Variables for Vercel

Set these in your Vercel project settings:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
RAPIDAPI_KEY=your-rapidapi-key
RAPIDAPI_HOST=instagram120.p.rapidapi.com
```

## 📦 Files Specific to Vercel

- `vercel.json` - Vercel deployment configuration
- `requirements-vercel.txt` - Optimized Python dependencies
- `luxestays_project/settings_vercel.py` - Vercel-specific Django settings
- `luxestays_project/wsgi_vercel.py` - Vercel-specific WSGI configuration
- `build_files.sh` - Build script for Vercel deployment

## 🚀 Deployment Steps

1. Connect your GitHub repository to Vercel
2. Set the branch to `vercel`
3. Configure environment variables
4. Deploy!

## ⚠️ Limitations

- **Database**: Uses SQLite (read-only in production)
- **File Uploads**: Limited to Vercel's serverless constraints
- **Media Files**: Consider using external storage (AWS S3, etc.)

## 🔄 Switching Between Deployments

- **Railway**: Use `master` branch
- **Vercel**: Use `vercel` branch
- **Development**: Use `develop` branch 