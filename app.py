# ជំនួសកូដផ្នែកបង្កើតវីដេអូ និង FFmpeg ខាងក្រោមនេះ៖

                audio_segments = asyncio.run(create_segments())

                if len(audio_segments) > 0:
                    inputs = []
                    filter_parts = []

                    # បន្ថែមសំឡេង AI នីមួយៗចូលទៅតាម Timing
                    for idx, (start_time, audio_path) in enumerate(audio_segments):
                        inputs.extend(["-i", audio_path])
                        delay_ms = int(start_time * 1000)
                        filter_parts.append(f"[{idx+1}:a]adelay={delay_ms}|{delay_ms},volume=3.0[a{idx}]")

                    # បង្កើត string សម្រាប់ amix (រួមបញ្ចូលទាំងសំឡេងដើម stream 0:a និងសំឡេង AI ទាំងអស់)
                    total_inputs = len(audio_segments) + 1  # វីដេអូដើម (0:a) + សំឡេង AI
                    
                    mix_ai_inputs = "".join([f"[a{i}]" for i in range(len(audio_segments))])
                    
                    # បើវីដេអូដើមមានសំឡេង យើងយក 0:a មកលាយជាមួយសំឡេង AI
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
                    st.warning("⚠️ សូមបញ្ចូលព័ត៌មានក្នុងតារាងឱ្យបានត្រឹមត្រូវសិន!")
