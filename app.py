import streamlit as st
import os
import tempfile
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from googletrans import Translator
from gtts import gTTS

st.set_page_config(page_title="AI Khmer Video Dubbing", page_icon="🎬", layout="wide")

st.title("🎬 AI បកប្រែសំឡេងវីដេអូជាភាសាខ្មែរតាមសាច់រឿងពិត")
st.markdown("---")

video_file = st.file_uploader("ជ្រើសរើសវីដេអូរបស់អ្នក (MP4, AVI, MOV)", type=["mp4", "avi", "mov", "mkv"])

if video_file is not None:
    # បង្ហាញវីដេអូដើម
    st.video(video_file)
    
    if st.button("🚀 ចាប់ផ្តើមបកប្រែសំឡេងពិតពីវីដេអូ", type="primary"):
        with st.spinner("កំពុងដំណើរការ... សូមរង់ចាំបន្តិច"):
            try:
                # ១. រក្សាទុកវីដេអូជា File បណ្តោះអាសន្ន
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                video_path = tfile.name

                # ២. ទាញយកសំឡេង (Audio) ចេញពីវីដេអូ និងបម្លែងជា WAV
                audio_path = video_path.replace(".mp4", ".wav")
                video_clip = VideoFileClip(video_path)
                if video_clip.audio is not None:
                    video_clip.audio.write_audiofile(audio_path, logger=None)
                else:
                    st.error("វីដេអូនេះគ្មានសំឡេងទេ!")
                    st.stop()

                # ៣. ប្រើប្រាស់ Speech Recognition ដើម្បីអានសំឡេងពីវីដេអូ
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio_data = recognizer.record(source)
                
                # បម្លែងសំឡេងជាអត្ថបទ (English/Auto)
                original_text = recognizer.recognize_google(audio_data)
                
                # ៤. បកប្រែអត្ថបទនោះជាភាសាខ្មែរតាមសាច់រឿងពិតប្រាកដ
                translator = Translator()
                translation = translator.translate(original_text, dest='kh')
                translated_text = translation.text

                # ៥. បន្ថែមការដកដង្ហើម និងស្ទីលនិយាយតាមមាត់តួអង្គ
                formatted_script = f"[ហឺត...] {translated_text} [ដកដង្ហើមធំ]"

                st.success("✅ បកប្រែបានជោគជ័យតាមសាច់រឿងក្នុងវីដេអូ!");
                
                # បង្ហាញលទ្ធផលអត្ថបទ
                st.markdown("### 📝 អត្ថបទដើមក្នុងវីដេអូ:")
                st.info(original_text)

                st.markdown("### 🇰🇭 អត្ថបទបកប្រែជាភាសាខ្មែរ (មានបញ្ចូលការដកដង្ហើម):")
                st.success(formatted_script)

                # ៦. បម្លែងអត្ថបទខ្មែរទៅជាសំឡេង (TTS)
                tts = gTTS(text=formatted_script, lang='km', slow=False)
                output_audio_path = video_path.replace(".mp4", "_khmer.mp3")
                tts.save(output_audio_path)

                st.markdown("### 🔊 សំឡេងបកប្រែភាសាខ្មែរ៖")
                st.audio(output_audio_path)

            except sr.UnknownValueError:
                st.error("AI មិនអាចស្តាប់ឮសំឡេងច្បាស់ពីក្នុងវីដេអូនេះទេ។ សូមព្យាយាមម្តងទៀតជាមួយវីដេអូដែលមានសំឡេងច្បាស់។")
            except Exception as e:
                st.error(f"មានបញ្តាកើតឡើង: {e}")
