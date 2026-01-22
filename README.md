# ⚡ Flux 2 Studio

**Flux 2 Studio** is a professional prompt engineering tool designed specifically for **Flux.1 and Flux.2** image generation models. 

Unlike older models (Stable Diffusion 1.5/XL) that rely on "tag soup" (e.g., `masterpiece, best quality, 4k`), Flux uses a T5 Text Encoder that thrives on **natural language descriptions**. This app uses Google's **Gemini AI** to convert simple ideas into rich, descriptive, sentence-based prompts optimized for Flux.

## ✨ Features

* **🧠 Dual AI Engines:** Toggle between **Gemini Flash** (Speed) and **Gemini Pro** (Maximum Creativity/Logic).
* **🗣️ Natural Language Optimization:** Automatically enforces the sentence-based prompting style required by Flux models.
* **💾 Persistent History:** Automatically saves your prompt history to disk (`prompt_history.json`). Your history survives restarts!
* **📥 Export Data:** One-click export of all generated prompts to CSV for your records.
* **⚡ Quick Load:** A "Recent Concepts" dropdown lets you instantly reload and tweak your last 25 ideas.
* **🔐 Secure Gatekeeper:** Built-in password protection to prevent unauthorized usage when deployed to the web.
* **🎨 Cyberpunk UI:** Custom Neon/Dark styling with "Glass-morphism" cards for easy reading.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/flux-prompt-generator.git](https://github.com/YourUsername/flux-prompt-generator.git)
    cd flux-prompt-generator
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Secrets:**
    Create a folder named `.streamlit` and a file inside called `secrets.toml`:
    
    ```toml
    # .streamlit/secrets.toml
    GEMINI_API_KEY = "Your_Google_Gemini_Key"
    APP_PASSWORD = "Set_A_Secure_Password"
    IS_LOCAL = true  # Set to false when deploying!
    ```

## 🚀 Usage

Run the app locally with Streamlit:

```bash
streamlit run flux_generator_v9.py