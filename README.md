
# MimicPhish Framework 🛡️

An educational, pure Python-based reverse proxy framework designed to demonstrate Adversary-in-the-Middle (AiTM) MFA-relaying mechanics in an isolated, local lab environment.

---

## 📋 Overview
**MimicPhish** is built to study and analyze how real-time credential harvesting and Multi-Factor Authentication (MFA) bypass techniques operate. By acting as a transparent reverse proxy between a client and a target mock server, the framework intercepts HTTP POST requests, extracts sensitive payloads (usernames, passwords, and dynamic OTP codes), and forwards them seamlessly without disrupting the session flow.

---

## ⚙️ Key Features
* **Pure Python Compliance:** Built entirely using Python standard libraries (`http.server`, `urllib.request`, `argparse`, `logging`) with **zero external dependencies** (`pip install` is not required).
* **Real-Time Relaying:** Proxies traffic dynamically, capturing one-time passwords (OTP/MFA) within their validity window.
* **Lightweight & Cross-Platform:** Runs smoothly across Windows and Linux environments with minimal resource overhead.
* **Controlled Lab Design:** Strictly tailored for loopback (`127.0.0.1`) testing and academic security analysis.

---

## 📂 Project Structure
```text
MimicPhish/
│
├── mimicphish.py      # Core Reverse Proxy engine & CLI handler
├── target_site.py     # Mock target server for lab simulation
├── config.json        # Dynamic routing and port configuration
└── README.md          # Project documentation

```
## 🚀 Deployment & Testing Guide (Local Lab)
To run and test the framework locally, open **two separate terminal windows**:
### Step 1: Start the Mock Target Server (Terminal 1)
```bash
python3 target_site.py

```
*(The target mock server will start listening on port 5000)*.
### Step 2: Start the MimicPhish Proxy Engine (Terminal 2)
```bash
python3 mimicphish.py run

```
*(The proxy engine will start listening on port 8080)*.
### Step 3: Access via Browser
Open your browser (Chrome, Firefox, or Edge) and navigate to:
```text
[http://127.0.0.1:8080](http://127.0.0.1:8080)

```
Enter credentials and the MFA code; you will observe the intercepted URL-encoded payload logged instantly in the proxy terminal.
## 🛠️ Troubleshooting
| Error Symptom | Root Cause | Solution |
|---|---|---|
| **504 Gateway Timeout** | Target server was not running prior to the proxy. | Ensure target_site.py is active on port 5000 before running the proxy. |
| **ERR_PROXY_CONNECTION_FAILED** | Leftover system proxy configurations in OS settings. | Disable local proxy settings in network properties or use Incognito mode. |
| **ERR_CONNECTION_REFUSED** | Proxy script stopped listening on port 8080. | Restart mimicphish.py in the terminal. |
## 🔒 Security & Defense Countermeasures
Understanding this attack vector highlights the importance of adopting robust modern defenses:
 1. **FIDO2 / WebAuthn (Passkeys):** Utilizing domain-bound cryptographic credentials that inherently block relaying attempts to unverified domains.
 2. **TLS Fingerprinting & Header Inspection:** Monitoring network anomalies and intermediate proxy headers.
## 📝 Author & Academic Context
 * **Author:** Amani Ajlan (أماني علي عجلان)
 * **University:** Sana'a University – Faculty of Computer and Information Technology
 * **Major:** Cybersecurity (Year 3)
 * **Purpose:** Academic Research & Practical Cyber-Lab Defense Demonstration.
```

```
