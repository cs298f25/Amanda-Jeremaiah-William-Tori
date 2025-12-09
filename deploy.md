# Deployment Guide

## Local Development

To deploy and run the application locally, follow these steps:

### Prerequisites
- Python 3.7 or higher installed on your system

### Setup Instructions

1. **Navigate to the project directory:**
   ```bash
   cd Amanda-Jeremaiah-William-Tori
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```
   
   Or alternatively:
   ```bash
   flask run
   ```

6. **Access the application:**
   - Open your browser and navigate to: `http://localhost:5000` or `http://127.0.0.1:5000`



## Deploy on AWS

### Configure:
   - **AMI:** Amazon Linux
   - **Instance Type:** t2.micro or t3.micro
   - **Key Pair:** Select or create a key pair (save the .pem file)
   - **Security Group:** Add rule for **Custom TCP port 8000** from **0.0.0.0/0**
   - **Storage:** Default 8GB

1. **Create your EC2 instance on AWS**
Paste this into your User Data when creating the instance:
```bash
#!/bin/bash
sudo yum update -y
sudo yum install -y git python3 python3-pip
git clone https://github.com/cs298f25/Amanda-Jeremaiah-William-Tori.git /home/ec2-user/Amanda-Jeremaiah-William-Tori
cd /home/ec2-user/Amanda-Jeremaiah-William-Tori
chmod +x ec2-deploy.sh
sudo ./ec2-deploy.sh
```
        
3. **SSH into your created instance**
```bash
ssh -i ~/.ssh/labsuser.pem ec2-user@<IPv 4 address>
```
   
3. **Install Git**
```bash
sudo yum install -y git
```
        
4. **Clone the repo into your EC2 instance**
```bash
git clone https://github.com/cs298f25/Amanda-Jeremaiah-William-Tori.git
cd Amanda-Jeremaiah-William-Tori
```

5. **Change permissions on the script file**
```bash
chmod +x ec2-deploy.sh
```     

6. **Run the Deploy script**
```bash
sudo ./ec2-deploy.sh
```

7. **Access the Web Page**
```bash
http://[your-public-ip]:8000
```

**Systemctl commands**
```bash
# Start the service
sudo systemctl start flask-app

# Stop the service
sudo systemctl stop flask-app

# Restart the service
sudo systemctl restart flask-app

# Check status
sudo systemctl status flask-app

# View logs (live)
sudo journalctl -u flask-app -f

# View recent logs
sudo journalctl -u flask-app -n 50

# Disable auto-start on boot
sudo systemctl disable flask-app

# Enable auto-start on boot
sudo systemctl enable flask-app
```




### Note
- The app runs in development mode by default
- To stop the server, press `Ctrl+C` in your terminal
