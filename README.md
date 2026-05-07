# SecureVision – IP Camera Surveillance System

## Features
- **Live Camera Feed** — MJPEG stream from IP camera or webcam
- **User Authentication** — Strict login with SHA-256 password hashing
- **User Registration** — Password strength enforcement (uppercase, number, special char)
- **Admin Panel** — Manage users, enable/disable accounts, view login logs
- **Login Monitoring** — Every login attempt is logged with IP address and timestamp
- **Demo Auto-Login** — One-click demo buttons on login page
- **Responsive UI** — Works on mobile, tablet, and desktop

## Demo Credentials
| Username | Password   | Role   |
|----------|------------|--------|
| admin    | Admin@1234 | Admin  |
| viewer   | Viewer@1234| Viewer |

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000

## Environment Variables

| Variable     | Default        | Description                          |
|--------------|----------------|--------------------------------------|
| CAMERA_URL   | `0`            | `0` = webcam, or RTSP URL            |
| SECRET_KEY   | (random)       | Flask session secret                 |
| PORT         | `5000`         | HTTP port                            |

### Camera URL Examples
```
CAMERA_URL=0                                          # Webcam
CAMERA_URL=rtsp://192.168.1.10:554/stream1            # Generic RTSP
CAMERA_URL=rtsp://192.168.1.10:554/Streaming/Channels/101  # Hikvision
CAMERA_URL=http://192.168.1.10:8080/video             # MJPEG HTTP
```

## Deploy on Railway

1. Push this folder to a GitHub repository
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Set environment variables in Railway dashboard:
   - `CAMERA_URL` = your RTSP stream URL
   - `SECRET_KEY` = a long random string
4. Railway auto-detects `Procfile` and deploys

> **Note:** For Railway cloud deployment, the camera must be an RTSP/HTTP stream
> accessible from the internet (use a public IP or DDNS). A local webcam (`0`) only
> works when running locally.

## Network Topology (from manual)
```
IP Camera (192.168.1.10)
    |— Ethernet —|
              [Switch]
    |— Ethernet —|        |— Ethernet —|
  Router (192.168.1.1)   Web Server (192.168.1.20:5000)
```

## File Structure
```
ipcam_system/
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── Procfile            # Railway/Heroku process
├── README.md           # This file
└── templates/
    ├── login.html      # Login page w/ demo auto-fill
    ├── register.html   # Registration w/ password rules
    ├── dashboard.html  # Live camera dashboard
    └── admin.html      # Admin: users + login logs
```
