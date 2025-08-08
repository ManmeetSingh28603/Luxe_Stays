# 🚀 Quick Deployment Guide

## 📋 Current Setup

✅ **Successfully created 3 branches:**
- `master` - Railway deployment (paid service)
- `vercel` - Vercel deployment (free tier)
- `develop` - Development branch

## 🔄 How to Switch Between Deployments

### When Railway Subscription is ACTIVE (Use `master` branch)
```bash
# 1. Switch to master branch
git checkout master

# 2. Push to GitHub
git push origin master

# 3. Railway will auto-deploy from master branch
```

### When Railway Subscription EXPIRES (Use `vercel` branch)
```bash
# 1. Switch to vercel branch
git checkout vercel

# 2. Push to GitHub
git push origin vercel

# 3. Connect Vercel to GitHub and set branch to 'vercel'
```

## 🎯 Key Differences

| Feature | Railway (master) | Vercel (vercel) |
|---------|------------------|-----------------|
| **Cost** | Paid | Free |
| **Database** | Full SQLite/PostgreSQL | SQLite (read-only) |
| **File Uploads** | ✅ Full support | ⚠️ Limited |
| **Cache** | File-based | Memory-based |
| **Static Files** | WhiteNoise | CDN optimized |
| **Requirements** | `requirements.txt` | `requirements-vercel.txt` |

## 📝 Environment Variables

### For Railway (master branch)
Set these in Railway dashboard:
```
SECRET_KEY=your-secret-key
DEBUG=False
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
RAPIDAPI_KEY=your-rapidapi-key
RAPIDAPI_HOST=instagram120.p.rapidapi.com
```

### For Vercel (vercel branch)
Set these in Vercel dashboard:
```
SECRET_KEY=your-secret-key
DEBUG=False
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
RAPIDAPI_KEY=your-rapidapi-key
RAPIDAPI_HOST=instagram120.p.rapidapi.com
DJANGO_SETTINGS_MODULE=luxestays_project.settings_vercel
```

## 🚨 Important Notes

1. **Always commit changes before switching branches**
2. **Environment variables must be set in both platforms**
3. **Vercel has limitations for file uploads and database writes**
4. **Railway provides full functionality when subscription is active**

## 🔧 Development Workflow

```bash
# 1. Work on develop branch
git checkout develop
# Make your changes
git add .
git commit -m "Your changes"
git push origin develop

# 2. When ready for Railway deployment
git checkout master
git merge develop
git push origin master

# 3. When ready for Vercel deployment
git checkout vercel
git merge develop
git push origin vercel
```

## 📞 Support

- **Railway Issues**: Check Railway logs and documentation
- **Vercel Issues**: Check Vercel deployment logs
- **Code Issues**: Check Django debug output

---

**🎉 You're all set! You can now switch between paid and free hosting seamlessly!** 