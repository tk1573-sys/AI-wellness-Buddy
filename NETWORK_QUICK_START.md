# Quick Network Access Guide

## 🌐 Access UI from Network Devices

### Quick Start (3 Steps)

1. **Start the network UI**:
   ```bash
   bash start_ui_network.sh
   ```

2. **Note the Network URL** displayed:
   ```
   Network URL: http://192.168.1.100:8501
   ```

3. **Open on any device** on the same network:
   - Phone: Open browser → Enter the Network URL
   - Tablet: Open browser → Enter the Network URL
   - Another computer: Open browser → Enter the Network URL

### What You'll See

When you start the network UI, you'll see:

```
==========================================
AI Wellness Buddy - Network UI Launcher
==========================================

🚀 Starting Web UI on network...
📍 Local access: http://localhost:8501
📍 Network access: http://192.168.1.100:8501

⚠️  SECURITY NOTE:
   This allows network access to your wellness buddy.
   Only use on trusted networks!

To stop: Press Ctrl+C
==========================================

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

### Access Methods

| Device Type | Steps |
|------------|-------|
| **Same Computer** | Open browser → `http://localhost:8501` |
| **Phone/Tablet** | Open browser → `http://YOUR-IP:8501` |
| **Other Computer** | Open browser → `http://YOUR-IP:8501` |

### Finding Your IP Address

**Linux/Mac**:
```bash
ip addr show
# or
ifconfig
```

**Windows**:
```bash
ipconfig
```

Look for your local network IP (usually starts with 192.168.x.x or 10.x.x.x)

### Troubleshooting

**Cannot access from another device?**

1. **Check Firewall**: Allow port 8501
   ```bash
   # Linux
   sudo ufw allow 8501
   
   # Windows: Add inbound rule in Windows Firewall
   ```

2. **Verify same network**: All devices must be on the same Wi-Fi/LAN

3. **Try different port**:
   ```bash
   bash start_ui_network.sh 8080
   ```

### Security Tips

✅ **Safe**:
- Using on your home Wi-Fi
- Using on trusted office network
- All devices are yours or trusted

⚠️ **Caution**:
- Public Wi-Fi
- Shared networks
- Untrusted devices on network

🔒 **Best Practice**:
- Use only on trusted networks
- Stop the server when not in use (Ctrl+C)
- Consider VPN for remote access

### Mobile Phone Quick Access

1. Start the UI with network access
2. On your phone, open browser
3. Enter the Network URL
4. **Add to Home Screen** for quick access:
   - **iPhone**: Tap Share → Add to Home Screen
   - **Android**: Menu → Add to Home screen

Now you have an app icon on your phone!

### For More Details

- **Full deployment guide**: See [NETWORK_DEPLOYMENT.md](NETWORK_DEPLOYMENT.md)
- **Cloud deployment**: See "Streamlit Cloud" section in deployment guide
- **Docker/VPS**: See "Advanced Deployment" in deployment guide

---

**Need help?** Check the main [README.md](README.md) or deployment guide.
