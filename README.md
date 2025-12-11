# Log-Application-# 🚀 Advanced Multi-Log Analysis Application  
A powerful Flask-based dashboard that analyzes and visualizes logs from **8 different systems** such as Apache, Nginx, Docker, Ejabberd, MongoDB, MySQL, PostgreSQL, and Redis.

This tool automatically extracts insights like errors, warnings, status codes, IP activity, authentication failures, DB queries, and hourly trends — similar to a Grafana-style analysis but running locally.

---

##  Features

###  Supported Log Types (8 Types)
- Apache Logs  
- Nginx Logs  
- Docker Logs  
- Ejabberd Logs  
- MongoDB Logs  
- MySQL Logs  
- PostgreSQL Logs  
- Redis Logs  

###  Key Capabilities
- Automatic REGEX-based log parsing  
- Detects status codes, IPs, timestamps, events, queries, components, users  
- Extracts insights:
  - Error / Warning / Notice count  
  - Status code distribution  
  - Top IPs  
  - Top URLs / paths  
  - DB query types  
  - Failed logins  
  - Active users  
  - Log volume over time  
- Accepts `.txt`, `.log`, `.csv`, `.xlsx` files  
- Clean dashboard UI (Flask)  
- Shows structured JSON output for chart usage  

---

## 📁 Project Structure

