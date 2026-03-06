# Deployment Guide for WebHostingKenya (CPanel) - Single Domain

This guide configures the entire system (Frontend + Backend) to run on **one domain**: `https://linev.inphora.net`.

## System Overview
- **Frontend**: React (Static Files) at `https://linev.inphora.net`
- **Backend**: FastAPI (Python) at `https://linev.inphora.net/api`
- **Database**: MySQL (hosted on localhost)

---

## Part 1: Initial Setup

### 1. Database Setup
1.  Log in to **CPanel**.
2.  Go to **Databases** -> **MySQL Database Wizard**.
3.  **Step 1**: Create Database.
    -   Name: `batchtrack` (Full name: `username_batchtrack`).
4.  **Step 2**: Create User.
    -   Username: `batchuser` (Full name: `username_batchuser`).
    -   Password: **Use the encrypted password below if using special characters**.
5.  **Step 3**: Privileges.
    -   Check **ALL PRIVILEGES**.
    -   Click **Make Changes**.

---

## Part 2: Backend Deployment (The "Api" Folder)

*Strategy: We will deploy the backend code but map it to the `/api` URL so it doesn't conflict with your website.*

### 1. Upload Backend Files
1.  In CPanel **File Manager**:
    -   Go to your home directory (`/home/username/`).
    -   Create a folder: `batchtrack_backend`.
    -   Upload `backend.zip` and **Extract** it there.

### 2. Setup Python App
1.  Go to **Software** -> **Setup Python App**.
2.  Click **Create Application**.
    -   **Python Version**: **3.10**.
    -   **Application Root**: `batchtrack_backend`.
    -   **Application URL**:
        -   Select `linev.inphora.net`.
        -   **IMPORTANT**: In the box next to the domain, type `api` (so it reads `linev.inphora.net/api`).
        -   *If your CPanel does NOT allow adding a path here, select the root domain and see the "Advanced Troubleshooting" section below.*
    -   **Startup File**: `passenger_wsgi.py`.
    -   **Entry Point**: `application`.
3.  Click **Create**.

### 3. Install Dependencies
1.  Copy the "enter virtual environment" command from the top of the page.
2.  Open **Terminal** in CPanel, paste command.
3.  Run:
    ```bash
    pip install -r requirements.txt
    pip install pymysql
    ```

### 4. Environment Variables
1.  Go back to Python App setup -> **Environment Variables**.
2.  Add:
    -   `DATABASE_URL`: `mysql+pymysql://username_batchuser:Re4nC0%28%5B%2142Q@localhost/username_batchtrack`
        *(Note: The password `Re4nC0([!42Q` is URL-encoded here)*
    -   `SECRET_KEY`: (Random string)
    -   `ALLOWED_ORIGINS`: `https://linev.inphora.net,https://www.linev.inphora.net`
3.  Click **Save** and **Restart**.

---

## Part 3: Frontend Deployment (The Website)

### 1. Upload Frontend Files
1.  In CPanel **File Manager**, go to **public_html** (or the document root for `linev.inphora.net`).
2.  **Delete** the default `index.html` or `default.cgi` if present.
3.  Upload `frontend.zip`.
4.  **Extract** it.
    -   Move the **contents** of the extracted folder directly into the root of public_html.
    -   You should see `index.html`, `assets/`, etc., right inside `public_html`.

### 2. Configure .htaccess (Critical)
1.  Edit the `.htaccess` file in `public_html`.
2.  Ensure it looks like this (this handles React routing):
    ```apache
    <IfModule mod_rewrite.c>
      RewriteEngine On
      RewriteBase /
      
      # Prepare for React Routing
      RewriteRule ^index\.html$ - [L]
      
      # If the request is NOT for a real file/directory
      RewriteCond %{REQUEST_FILENAME} !-f
      RewriteCond %{REQUEST_FILENAME} !-d
      RewriteCond %{REQUEST_FILENAME} !-l
      
      # AND the request is NOT for the API (let Python handle /api)
      RewriteCond %{REQUEST_URI} !^/api
      
      # Then serve index.html
      RewriteRule . /index.html [L]
    </IfModule>
    ```
3.  **Save**.

---

## verification
1.  **Check API**: Visit `https://linev.inphora.net/api/health`.
    -   *Success*: `{"status":"OK"}`.
    -   *Failure (404)*: The Python app mapping to `/api` didn't work. Check if you mapped it to Root instead.
2.  **Check Site**: Visit `https://linev.inphora.net`.
    -   *Success*: Dashboard loads (Login screen).

---

## Advanced Troubleshooting: If "Setup Python App" Forced Root Domain
If CPanel forced you to map the app to `linev.inphora.net` (no `/api` option):
1.  The Python app will try to handle EVERYTHING.
2.  You must edit `.htaccess` in `public_html` to **exclude** real files from Passenger (if possible).
3.  However, usually the "Map to /api" option IS available. If not, please report back for a specific `.htaccess` override trick.
