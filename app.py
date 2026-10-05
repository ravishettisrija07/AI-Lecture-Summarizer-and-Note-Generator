import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types
import urllib.parse as urlparse
from gtts import gTTS
import io

# 1. Setup the web page layout
st.set_page_config(page_title="AI Lecture Summarizer", layout="centered")
st.title("🎓 Automated AI Lecture Summarizer")
st.write("Turn YouTube videos, text transcripts, or recorded audio files into study notes instantly.")

# 2. API Key Input
api_key = st.text_input("Enter your Google Gemini API Key:", type="password")

# 3. Create three user tabs
tab1, tab2, tab3 = st.tabs(["🔗 YouTube Link Mode", "📝 Direct Text Mode", "🎙️ Audio Upload Mode"])

# Initialize data holders
video_url = ""
pasted_text = ""
uploaded_audio = None
recorded_audio_file = None

with tab1:
    video_url = st.text_input("Paste YouTube Lecture URL here:")

with tab2:
    pasted_text = st.text_area("Paste the transcript text directly here:", height=200)

with tab3:
    st.subheader("Option 1: Upload an Audio File")
    uploaded_audio = st.file_uploader("Upload a lecture recording (.mp3, .wav, or .m4a):", type=["mp3", "wav", "m4a"])
    
    st.write("---")
    st.subheader("Option 2: Record Live Microphone Audio")
    recorded_audio_file = st.audio_input("Click the microphone icon below to record your lecture live:")

# Helper function to extract clean Video ID
def get_video_id(url):
    try:
        if "v=" in url:
            parts = url.split("v=")
            if len(parts) > 1:
                return parts[1].split("&")[0]
        url_data = urlparse.urlparse(url)
        query = urlparse.parse_qs(url_data.query)
        if "v" in query:
            return query["v"][0]
        if url_data.hostname == "youtu.be":
            return url_data.path[1:]
    except Exception:
        return None
    return None

# 4. Action button
if st.button("Generate Lecture Notes", type="primary"):
    if not api_key:
        st.error("Please provide your Gemini API key to proceed.")
    else:
        full_transcript = ""
        audio_bytes = None
        audio_mime = "audio/wav"
        
        # Priority check for active inputs
        if pasted_text.strip():
            full_transcript = pasted_text
            st.success("Custom text loaded successfully!")
        
        elif recorded_audio_file is not None:
            audio_bytes = recorded_audio_file.read()
            st.success("Live audio recording captured successfully!")
            
        elif uploaded_audio is not None:
            audio_bytes = uploaded_audio.read()
            audio_mime = uploaded_audio.type
            st.success(f"Audio file '{uploaded_audio.name}' uploaded successfully!")
        
        elif video_url.strip():
            video_id = get_video_id(video_url)
            if not video_id:
                st.error("Could not parse the YouTube Video ID. Check the link.")
            else:
                with st.spinner("Attempting to extract YouTube transcript..."):
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-IN'])
                        full_transcript = " ".join([item['text'] for item in transcript_list])
                        st.success("Transcript fetched from YouTube successfully!")
                    except Exception:
                        st.error("YouTube blocked the direct transcript request or captions are disabled.")
        else:
            st.warning("Please provide input in one of the modes before clicking generate.")

        # 5. Send to Gemini Engine with Updated Resilient Model Routing
        if full_transcript or audio_bytes:
            with st.spinner("AI is analyzing and organizing your notes..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    if full_transcript:
                        prompt_content = f"""
                        You are an expert academic assistant. Read the following lecture text and generate structured, comprehensive study notes. 
                        Include a brief summary, key core concepts explained clearly, and a bulleted list of main takeaways.
                        
                        Text content:
                        {full_transcript}
                        """
                        content_payload = prompt_content
                    else:
                        prompt_audio = "You are an expert academic assistant. Listen closely to this audio recording and generate structured, comprehensive study notes with summaries and bulleted core concepts."
                        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=audio_mime)
                        content_payload = [prompt_audio, audio_part]

                    # --- UPDATED FAULT-TOLERANT ARCHITECTURE ---
                    try:
                        # Attempt the bleeding edge flagship model first
                        response = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=content_payload,
                        )
                    except Exception as inner_error:
                        # Catch server traffic bottlenecks (503 / 429) smoothly
                        if "503" in str(inner_error) or "UNAVAILABLE" in str(inner_error).upper() or "429" in str(inner_error):
                            st.info("⚠️ Primary server crowded. Routing to high-capacity baseline model...")
                            # Fallback instantly to the hyper-stable high-throughput production engine
                            response = client.models.generate_content(
                                model="gemini-3.5-flash",
                                contents=content_payload,
                            )
                        else:
                            raise inner_error
                    
                    notes_text = response.text
                    
                    if notes_text:
                        st.subheader("📚 Generated Study Notes")
                        st.markdown(notes_text)
                        
                        # Text to Speech Player
                        st.write("---")
                        st.subheader("🔊 Audio Notes Player")
                        with st.spinner("Generating audio voiceover..."):
                            try:
                                clean_text = notes_text.replace("*", "").replace("#", "")
                                tts = gTTS(text=clean_text[:1000], lang='en')
                                fp = io.BytesIO()
                                tts.write_to_fp(fp)
                                fp.seek(0)
                                st.audio(fp, format='audio/mp3')
                            except Exception:
                                st.warning("Audio player generation skipped.")
                        
                        # File Download Button
                        st.write("---")
                        st.download_button(
                            label="💾 Download Notes as File",
                            data=notes_text,
                            file_name="lecture_notes.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("The API endpoint responded successfully but returned empty string data.")
                        
                except Exception as e:
                    st.error(f"AI Generation failed: {e}")