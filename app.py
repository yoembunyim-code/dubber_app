# ជំនួសកូដផ្នែកតារាង និងផ្នែកដំណើរការខាងក្រោមនេះ៖

st.markdown("---")
st.subheader("3. កំណត់តារាងអត្ថបទ សំឡេង និងពេលវេលា (Timeline Mapping)")

if "timeline_data" not in st.session_state:
    st.session_state.timeline_data = pd.DataFrame([
        {"Start (s)": 0.0, "End (s)": 4.0, "Voice": "km-KH-PisethNeural (ប្រុស)", "Text": "បញ្ចូលអត្ថបទដែលចង់ឱ្យតួអង្គប្រុសនិយាយនៅទីនេះ"},
        {"Start (s)": 4.5, "End (s)": 8.0, "Voice": "km-KH-SreymomNeural (ស្រី)", "Text": "បញ្ចូលអត្ថបទដែលចង់ឱ្យតួអង្គស្រីនិយាយនៅទីនេះ"}
    ])

# ប្រើ key ដើម្បីរក្សាទុកទិន្នន័យដែលបានកែប្រែ
edited_df = st.data_editor(
    st.session_state.timeline_data, 
    num_rows="dynamic", 
    use_container_width=True, 
    key="timeline_editor"
)

start_dubbing = st.button("🚀 ចាប់ផ្តើមបង្កើតវីដេអូតាម Timeline នេះ", type="primary", use_container_width=True)

if start_dubbing:
    if video_file is None:
        st.error("សូមដាក់បញ្ចូលវីដេអូជាមុនសិន!")
    else:
        can_run, status_msg = check_license(is_vip)
        if not can_run:
            st.error(f"❌ អ្នកបានប្រើប្រាស់អស់កូតាឥតគិតថ្លៃ! សូមទាក់ទងមក Telegram {CONTACT_TELEGRAM}")
            st.stop()
        
        if not is_vip:
            save_license(usage + 1, is_vip=False)

        try:
            with st.spinner("🤖 កំពុងដំណើរការកាត់តសំឡេង និងផ្គុំចូលវីដេអូ..."):
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                vid_in = tfile.name
                vid_out = vid_in.replace(".mp4", "_precision_dubbed.mp4")
                temp_dir = tempfile.mkdtemp()

                async def generate_tts(text, voice, output_path):
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(output_path)

                async def create_segments():
                    audio_segments = []
                    # ទាញយកទិន្នន័យពិតប្រាកដដែលអ្នកបានកែក្នុងຕារាង
                    current_data = st.session_state.get("timeline_editor", edited_df)
                    
                    for idx, row in current_data.iterrows():
                        try:
                            start_t = float(row["Start (s)"])
                            end_t = float(row["End (s)"])
                            v_choice = str(row["Voice"])
                            text_val = str(row["Text"]).strip()
                        except Exception:
                            continue

                        if not text_val or text_val == "nan" or end_t <= start_t:
                            continue

                        voice_code = "km-KH-PisethNeural" if "ប្រុស" in v_choice else "km-KH-SreymomNeural"
                        
                        raw_audio = os.path.join(temp_dir, f"raw_{idx}.mp3")
                        fitted_audio = os.path.join(temp_dir, f"fitted_{idx}.wav")
                        target_duration = end_t - start_t

                        await generate_tts(text_val, voice_code, raw_audio)

                        probe_cmd = [
                            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1', raw_audio
                        ]
                        res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        try:
                            gen_duration = float(res.stdout.strip())
                        except Exception:
                            gen_duration = target_duration

                        speed_ratio = gen_duration / target_duration
                        speed_ratio = max(0.5, min(speed_ratio, 2.0))

                        stretch_cmd = [
                            'ffmpeg', '-i', raw_audio,
                            '-filter:a', f'atempo={speed_ratio}',
                            '-ar', '44100', '-ac', '2', fitted_audio, '-y'
                        ]
                        subprocess.run(stretch_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        audio_segments.append((start_t, fitted_audio))

                    return audio_segments

                audio_segments = asyncio.run(create_segments())

                if len(audio_segments) > 0:
                    inputs = []
                    filter_parts = []

                    for idx, (start_time, audio_path) in enumerate(audio_segments):
                        inputs.extend(["-i", audio_path])
                        delay_ms = int(start_time * 1000)
                        filter_parts.append(f"[{idx+1}:a]adelay={delay_ms}|{delay_ms},volume=3.0[a{idx}]")

                    mix_ai_inputs = "".join([f"[a{i}]" for i in range(len(audio_segments))])
                    
                    filter_str = ";".join(filter_parts) + f";{mix_ai_inputs}amix=inputs={len(audio_segments)}:duration=longest:dropout_transition=0[ai_mix];[0:a][ai_mix]amix=inputs=2:weights=0.3 1.0[outa]"

                    cmd = ["ffmpeg", "-i", vid_in] + inputs + [
                        "-filter_complex", filter_str,
                        "-map", "0:v:0", "-map", "[outa]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-y", vid_out
                    ]

                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    st.success("✅ បង្កើតវីដេអូជោគជ័យ ១០០%!")
                    st.video(vid_out)

                    with open(vid_out, "rb") as f:
                        st.download_button("📥 ទាញយកវីដេអូ", data=f, file_name="dubbed_story.mp4", mime="video/mp4", use_container_width=True)
                else:
                    st.warning("⚠️ សូមបំពេញអត្ថបទ និងម៉ោងក្នុងតារាងឱ្យបានត្រឹមត្រូវសិន!")

                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            st.error(f"⚠️ មានបញ្ហាក្នុងការដំណើរការ៖ {e}")
