# ⚡ STALWART AUDIT ENGINE: OPERATIONAL USER GUIDE

### Prerequisites
- Python 3.9+ installed on your local machine.
- Terminal or command prompt opened inside the project folder.

### Installation
Run the following command in your terminal to install required dependencies:
pip install streamlit pypdf

### Launching the Engine
Run the application via terminal:
streamlit run moralityengine.py
*(Your default web browser will automatically open the local interface at http://localhost:8501)*

### Running an Audit
1. Click "Browse Files" in the dashboard and upload your target legislative document (.pdf or .txt).
2. Click "GENERATE FULL SPECTRUM INDICTMENT DOSSIER" to parse the text, reveal hidden loopholes, Supreme Court precedents, money trails, and named responsible actors.

## 🔑 How to Get Your Free Gemini API Key

STALWART v12.0 uses Google's Gemini AI to dynamically parse documents and generate tailored civic action plans. To run this program, you will need to generate a free API key.

**Step-by-Step Instructions:**
1. **Visit Google AI Studio:** Go to [https://aistudio.google.com/](https://ai.google.dev/aistudio) and sign in with your Google account.
2. **Access API Keys:** On the left-hand menu, click on **"Get API key"**.
3. **Create the Key:** Click the **"Create API key"** button. If prompted, follow the dialog to create a new key-project pair. 
4. **Copy the Key:** Copy the generated string of text. Keep this key secure and never publish it publicly in a GitHub repository.
5. **Run STALWART:** Launch the STALWART Streamlit app, and paste your API key into the "Gemini API Key" box located in the left-hand configuration sidebar.

---

### ⚠️ Important Note for Free-Tier Users (503 & Rate Limit Errors)

STALWART defaults to using the `gemini-2.5-flash` model on Google's Free Tier, which costs $0.00 to operate. 

However, because the Free Tier shares server capacity with millions of developers, you may occasionally see a red error box when you click "EXECUTE DYNAMIC FORENSIC AUDIT":
* **503 UNAVAILABLE:** This simply means the free servers are experiencing a temporary spike in high demand. 
* **RESOURCE_EXHAUSTED:** You hit a temporary rate limit for requests.

**The Fix:** You do not need to pay or upgrade. Simply **wait 10 to 15 seconds** and click the "Execute" button again. The traffic usually clears up immediately on the second or third try. 

*(Note for Enterprise Users: If you are scanning hundreds of massive federal dockets and want zero throttling, you can upgrade your API key to the paid tier by setting up Cloud Billing in Google AI Studio. At roughly $0.09 per 300-page document, the cost is minimal).*
