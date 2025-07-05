# 🚀 Render Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. **Repository Setup**
- [ ] Code is pushed to GitHub
- [ ] All files are committed
- [ ] No sensitive data in repository
- [ ] `.gitignore` is properly configured

### 2. **Required Files**
- [ ] `app.py` - Main Flask application
- [ ] `requirements.txt` - Python dependencies with versions
- [ ] `Procfile` - Render deployment configuration
- [ ] `runtime.txt` - Python version specification
- [ ] `build.sh` - Build script for NLTK data
- [ ] `data/movies_links.txt` - Movie database
- [ ] `templates/` - All HTML templates
- [ ] `static/css/style.css` - Styling

### 3. **File Permissions**
- [ ] `build.sh` is executable (chmod +x build.sh)

## 🎯 Render Deployment Steps

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Verify email address

### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Select your repository

### Step 3: Configure Service
- **Name**: `movie-search-recommendation`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (if app is in root)
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2`

### Step 4: Advanced Settings
- **Plan**: Free (or paid for better performance)
- **Auto-Deploy**: Enabled
- **Health Check Path**: `/` (optional)

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build process (5-10 minutes)
3. Monitor build logs for any errors

## 🔍 Post-Deployment Verification

### 1. **Check Build Logs**
- [ ] NLTK data downloaded successfully
- [ ] All dependencies installed
- [ ] Cache directory created
- [ ] No build errors

### 2. **Test Application**
- [ ] Home page loads correctly
- [ ] Search functionality works
- [ ] Genre recommendations work
- [ ] All links and navigation work
- [ ] Mobile responsiveness

### 3. **Performance Check**
- [ ] Page load times < 3 seconds
- [ ] Search results appear quickly
- [ ] Recommendations load fast
- [ ] No timeout errors

## 🛠️ Troubleshooting

### Common Issues

#### Build Fails
- **NLTK Download Error**: Check internet connection in build logs
- **Dependency Error**: Verify `requirements.txt` versions
- **Permission Error**: Ensure `build.sh` is executable

#### App Won't Start
- **Port Error**: Check `Procfile` configuration
- **Import Error**: Verify all files are in correct locations
- **Memory Error**: Consider upgrading to paid plan

#### Performance Issues
- **Slow Loading**: Check cache directory creation
- **Timeout Errors**: Increase timeout in `Procfile`
- **Memory Issues**: Reduce workers in `Procfile`

### Debug Commands
```bash
# Check build logs
# View in Render dashboard

# Test locally before deployment
python app.py

# Check file permissions
ls -la build.sh

# Verify requirements
pip install -r requirements.txt
```

## 📊 Monitoring

### Render Dashboard
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, response times
- **Events**: Deployments, restarts, errors

### Health Checks
- **Endpoint**: `https://your-app.onrender.com/`
- **Expected**: 200 OK response
- **Frequency**: Every 30 seconds

## 🔄 Updates

### Automatic Deployments
- Push to main branch triggers auto-deploy
- Build process runs automatically
- Zero-downtime deployments

### Manual Deployments
- Use "Manual Deploy" in Render dashboard
- Useful for testing specific commits

## 📞 Support

### Render Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Render Status](https://status.render.com)

### Application Issues
- Check application logs in Render dashboard
- Review build logs for errors
- Test locally to isolate issues

---

**🎉 Your app should now be live at: `https://your-app-name.onrender.com`** 