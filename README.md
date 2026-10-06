# 🎓 Automated AI Lecture Summarizer

A multi-modal Python application built with **Streamlit** and the **Google Gemini API** that converts YouTube video links, direct text inputs, or raw audio recordings into highly structured, academic study notes. It also features automated text-to-speech voiceovers.

## 🚀 Features
- **YouTube Link Mode:** Automatically extracts video transcripts using `youtube-transcript-api`.
- **Direct Text Mode:** Allows manual input of long lecture articles or documents.
- **Audio Upload Mode:** Processes local audio files (`.mp3`, `.wav`) and live microphone recordings natively through the model layout.
- **Fault-Tolerant Redundancy:** Automatically switches from `gemini-3.8-flash` to `gemini-3.5-flash` if servers experience high demand.
- **Audio Voiceover Player:** Converts text study notes into MP3 format via `gTTS`.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI Engine:** Google GenAI SDK (`gemini-3.8-flash`)
- **Speech Engine:** gTTS (Google Text-to-Speech)
- **Language:** Python 3.10+

## 💻 How to Run Locally

1. Clone this repository or download `app.py`.
2. Install the dependencies:
   ```bash
   pip install streamlit youtube-transcript-api google-genai gtts
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## 🧑‍💻 Author
- **Name:** Srija Ravishetti
- **Roll Number:** 25RH1A05KF
- **College:** Malla Reddy Engineering College for Women(MRECW)
