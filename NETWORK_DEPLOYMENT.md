# Network Deployment Guide for AI Wellness Buddy

This guide explains how to run the AI Wellness Buddy UI app with network access, allowing you to access it from other devices on your network or deploy it to a server.

## 🌐 Quick Start - Network Access

### Local Network Access (Same Wi-Fi/LAN)

Run the network launcher script:

```bash
bash start_ui_network.sh
```

Or with a custom port:

```bash
bash start_ui_network.sh 8080
```

The script will display:
- **Local URL**: `http://localhost:8501` (access from same machine)
- **Network URL**: `http://YOUR-IP:8501` (access from other devices)

### Access from Other Devices

1. Make sure all devices are on the same network
2. Note the network URL displayed when starting the app
3. Open a browser on another device and navigate to the network URL
4. Example: `http://192.168.1.100:8501`

## 🔧 Manual Configuration

### Option 1: Command Line Arguments

Start with specific network settings:

```bash
streamlit run ui_app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
```

**Parameters:**
- `--server.address 0.0.0.0`: Listen on all network interfaces
- `--server.port 8501`: Port number (default 8501)
- `--server.headless true`: Run without auto-opening browser

### Option 2: Configuration File

The `.streamlit/config.toml` file is already configured for network access. You can customize it:

```toml
[server]
# Bind to all network interfaces
address = "0.0.0.0"

# Port number
port = 8501

# Enable CORS for network access
enableCORS = true

# Run headless (don't auto-open browser)
headless = true
```

## 🚀 Deployment Options

### 1. Home/Office Network

**Use Case**: Access from multiple devices on your local network

**Steps**:
1. Run `bash start_ui_network.sh` on your main computer
2. Find your computer's local IP address
3. Access from phones, tablets, or other computers using `http://YOUR-IP:8501`

**Security**: Only accessible on your local network

### 2. Cloud Deployment (Streamlit Cloud - Free)

**Use Case**: Access from anywhere with internet

**Steps**:
1. Push your code to GitHub (already done!)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository: `tk1573-sys/AI-wellness-Buddy`
6. Main file path: `ui_app.py`
7. Click "Deploy"

**Note**: User data is stored locally, so each deployment has separate profiles.

### 3. Self-Hosted Server (VPS/Cloud)

**Use Case**: Full control, custom domain, persistent data

**Example with Ubuntu Server**:

```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip -y

# Clone repository
git clone https://github.com/tk1573-sys/AI-wellness-Buddy.git
cd AI-wellness-Buddy

# Install dependencies
pip3 install -r requirements.txt

# Download NLTK data
python3 -c "import nltk; nltk.download('brown'); nltk.download('punkt')"

# Run with network access
bash start_ui_network.sh
```

**For persistent service (using systemd)**:

Create `/etc/systemd/system/wellness-buddy.service`:

```ini
[Unit]
Description=AI Wellness Buddy Web UI
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/AI-wellness-Buddy
ExecStart=/usr/bin/streamlit run ui_app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable wellness-buddy
sudo systemctl start wellness-buddy
```

### 4. Docker Deployment

**Use Case**: Containerized deployment, easy scaling

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"

COPY . .

# Expose port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "ui_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
```

Build and run:
```bash
docker build -t wellness-buddy .
docker run -p 8501:8501 -v ~/.wellness_buddy:/root/.wellness_buddy wellness-buddy
```

## 🔒 Security Considerations

### Network Access Security

When enabling network access, consider:

1. **Firewall Configuration**
   - Only open port 8501 to trusted networks
   - Use firewall rules to restrict access

2. **HTTPS/SSL**
   - For production, use a reverse proxy (nginx/Apache) with SSL
   - Get free SSL certificates from Let's Encrypt

3. **Authentication**
   - The app uses local user profiles (username-based)
   - Consider adding password protection for network access
   - Use VPN for remote access to home network

4. **Data Privacy**
   - User data is stored in `~/.wellness_buddy/` directory
   - Ensure this directory has proper permissions (700)
   - Regular backups recommended

### Example Nginx Reverse Proxy with SSL

```nginx
server {
    listen 443 ssl;
    server_name wellness.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔍 Troubleshooting

### Cannot Access from Network

**Check Firewall**:
```bash
# Linux
sudo ufw allow 8501

# Windows
# Add inbound rule for port 8501 in Windows Firewall
```

**Verify Server is Listening**:
```bash
# Check if port is open
netstat -tuln | grep 8501

# Or
ss -tuln | grep 8501
```

**Find Your IP Address**:
```bash
# Linux/Mac
ip addr show
# or
ifconfig

# Windows
ipconfig
```

### Port Already in Use

Change to a different port:
```bash
bash start_ui_network.sh 8080
```

Or kill the process using the port:
```bash
# Find process
lsof -i :8501

# Kill process
kill -9 <PID>
```

### Streamlit Connection Issues

Clear Streamlit cache:
```bash
streamlit cache clear
```

## 📱 Mobile Access

To access from mobile devices on the same network:

1. Start the app with network access
2. Note the network URL (e.g., `http://192.168.1.100:8501`)
3. On your mobile device:
   - Open browser (Chrome, Safari, Firefox)
   - Enter the network URL
   - Add to home screen for quick access

## 🌍 Internet Access (Public Deployment)

### Using Streamlit Cloud (Recommended for Testing)

**Pros**:
- Free for public repositories
- Automatic deployment from GitHub
- HTTPS enabled by default
- No server management

**Cons**:
- Limited resources on free tier
- Data stored on Streamlit's servers
- Public repositories only (or paid plan for private)

### Using Cloud Providers

**Options**:
- **Heroku**: Easy deployment, free tier available
- **AWS EC2/Lightsail**: More control, scalable
- **Google Cloud Platform**: Good free tier
- **DigitalOcean**: Simple VPS, predictable pricing
- **Railway.app**: Modern platform, easy Streamlit deployment

## 📊 Performance Tips

For better performance over network:

1. **Optimize Session State**: Minimize data in session state
2. **Caching**: Use `@st.cache_data` for expensive operations
3. **Lazy Loading**: Load data only when needed
4. **Connection Limits**: Streamlit handles multiple users well, but consider scaling for >50 concurrent users

## 🛠️ Advanced Configuration

### Custom Domain

1. Get a domain name
2. Point A record to your server IP
3. Configure reverse proxy (nginx/Apache)
4. Enable SSL with Let's Encrypt

### Load Balancing

For high traffic, use multiple instances behind a load balancer:

```bash
# Start multiple instances
streamlit run ui_app.py --server.port 8501 &
streamlit run ui_app.py --server.port 8502 &
streamlit run ui_app.py --server.port 8503 &
```

Configure nginx to load balance:
```nginx
upstream wellness_backend {
    server localhost:8501;
    server localhost:8502;
    server localhost:8503;
}
```

## 📝 Summary

| Deployment Type | Complexity | Cost | Use Case |
|----------------|------------|------|----------|
| Local Network | ⭐ Easy | Free | Home/office use |
| Streamlit Cloud | ⭐⭐ Moderate | Free | Testing, demos |
| VPS/Cloud | ⭐⭐⭐ Advanced | $5-20/month | Production |
| Docker | ⭐⭐⭐ Advanced | Varies | Scalable deployment |

## 🔗 Resources

- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [Streamlit Configuration](https://docs.streamlit.io/library/advanced-features/configuration)
- [Network Security Best Practices](https://owasp.org/www-project-top-ten/)

---

**Remember**: This is a mental health support tool. Ensure proper security measures when deploying to network/internet to protect user privacy and data.
