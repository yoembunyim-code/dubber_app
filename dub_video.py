#!/usr/bin/env python3
"""
dub_video.py
------------
Local / free English -> Khmer video dubbing pipeline.

Pipeline:
  1. Extract audio from the source video (ffmpeg)
  2. Transcribe English speech to text with timestamps (Whisper, runs locally)
  2b. (optional, --single-speaker) Identify who speaks the most and drop
      segments belonging to anyone else (pyannote.audio, runs locally)
  3. Translate each segment English -> Khmer (deep-translator, free, no API key)
  4. Generate Khmer speech for each segment (Facebook MMS-TTS, runs locally
     after the model is downloaded once from Hugging Face)
  5. Stretch/compress each Khmer clip to roughly fit the original segment's
     duration, then stitch all clips into one dubbed audio track
  6. Mux the new audio track onto the original video and compress the
     video stream so the final file stays small, while keeping the audio
     bitrate high for clarity

Install (one time):
    pip install openai-whisper deep-translator transformers torch \
        soundfile pydub numpy scipy
    # optional, only needed for --single-speaker:
    pip install pyannote.audio

    ffmpeg must also be installed and on PATH:
        Windows : https://www.gyan.dev/ffmpeg/builds/ (add bin/ to PATH)
        macOS   : brew install ffmpeg
        Linux   : sudo apt install ffmpeg

Usage:
    python dub_video.py input.mp4 -o output_khmer.mp4
    python dub_video.py input.mp4 -o output_khmer.mp4 --single-speaker
    python dub_video.py input.mp4 -o output_khmer.mp4 --whisper-model medium
    python dub_video.py input.mp4 --srt-only            # just export SRT files
    python dub_video.py input.mp4 -o out.mp4 \
        --self-pronoun "អូន" --other-pronoun "បង"        # customize pronouns

Notes:
  * First run downloads the Whisper model and the MMS-TTS Khmer model
    (facebook/mms-tts-khm). After that everything runs offline.
  * --single-speaker requires a (free) Hugging Face token for the
    pyannote speaker-diarization model; pass it with --hf-token or set
    the HF_TOKEN environment variable.
"""

import argparse
import os
import sys
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass
class Segment:
    start: float
    end: float
    text_en: str
    text_km: str = ""
    speaker: Optional[str] = None
    audio_path: Optional[str] = None

    @property
    def duration(self) -> float:
        return max(self.end - self.start, 0.05)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def log(msg: str) -> None:
    print(f"[dub_video] {msg}", flush=True)


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "ERROR: ffmpeg was not found on PATH. Install it first "
            "(see the docstring at the top of this script)."
        )


def run(cmd: List[str]) -> None:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({' '.join(cmd)}):\n{result.stdout.decode(errors='ignore')}"
        )


def seconds_to_srt_timestamp(t: float) -> str:
    if t < 0:
        t = 0
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments: List[Segment], path: str, khmer: bool) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            text = seg.text_km if khmer else seg.text_en
            f.write(f"{i}\n")
            f.write(
                f"{seconds_to_srt_timestamp(seg.start)} --> "
                f"{seconds_to_srt_timestamp(seg.end)}\n"
            )
            f.write(f"{text.strip()}\n\n")
    log(f"Wrote {path}")


# --------------------------------------------------------------------------- #
# Step 1: extract audio
# --------------------------------------------------------------------------- #

def extract_audio(video_path: str, out_wav: str) -> None:
    log("Step 1/6: extracting audio with ffmpeg ...")
    run([
        "ffmpeg", "-y", "-i", video_path,
        "-ac", "1", "-ar", "16000", "-vn",
        out_wav,
    ])


# --------------------------------------------------------------------------- #
# Step 2: transcribe with Whisper
# --------------------------------------------------------------------------- #

def transcribe(audio_path: str, model_name: str) -> List[Segment]:
    log(f"Step 2/6: transcribing with Whisper model '{model_name}' "
        f"(first run downloads the model) ...")
    import whisper  # openai-whisper

    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, language="en", verbose=False)

    segments = [
        Segment(start=s["start"], end=s["end"], text_en=s["text"].strip())
        for s in result["segments"]
        if s["text"].strip()
    ]
    log(f"  -> {len(segments)} segments transcribed.")
    return segments


# --------------------------------------------------------------------------- #
# Step 2b: (optional) single-speaker filtering via diarization
# --------------------------------------------------------------------------- #

def filter_main_speaker(
    segments: List[Segment], audio_path: str, hf_token: Optional[str]
) -> List[Segment]:
    log("Step 2b: running speaker diarization to find the main speaker ...")
    if not hf_token:
        sys.exit(
            "ERROR: --single-speaker requires a Hugging Face token. "
            "Pass --hf-token YOUR_TOKEN or set the HF_TOKEN env var. "
            "You also need to accept the pyannote/speaker-diarization "
            "user agreement on huggingface.co once."
        )

    from pyannote.audio import Pipeline

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=hf_token
    )
    diarization = pipeline(audio_path)

    # tally total speaking time per speaker
    totals = {}
    turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        totals[speaker] = totals.get(speaker, 0.0) + (turn.end - turn.start)
        turns.append((turn.start, turn.end, speaker))

    if not totals:
        log("  -> No speakers detected, skipping filter.")
        return segments

    main_speaker = max(totals, key=totals.get)
    log(f"  -> Main speaker: {main_speaker} "
        f"({totals[main_speaker]:.1f}s of speech)")

    def overlap(a_start, a_end, b_start, b_end) -> float:
        return max(0.0, min(a_end, b_end) - max(a_start, b_start))

    kept = []
    for seg in segments:
        seg_len = seg.end - seg.start
        main_time = sum(
            overlap(seg.start, seg.end, t_start, t_end)
            for t_start, t_end, spk in turns
            if spk == main_speaker
        )
        # keep segment if the main speaker accounts for most of it
        if seg_len == 0 or main_time / seg_len >= 0.5:
            seg.speaker = main_speaker
            kept.append(seg)

    log(f"  -> Kept {len(kept)}/{len(segments)} segments belonging to the "
        f"main speaker.")
    return kept


# --------------------------------------------------------------------------- #
# Step 3: translate EN -> KM
# --------------------------------------------------------------------------- #

# Stiff / literal Khmer phrasing -> more natural spoken equivalent.
# This is a lightweight, rule-based pass (no API key needed). It cannot
# match a real LLM for nuance, but it smooths out the most common
# "Google-Translate-isms" so the subtitle reads less like a textbook.
NATURALIZE_MAP = {
    "តើអ្នកសុខសប្បាយទេ": "សុខសប្បាយទេ",
    "ខ្ញុំមិនដឹងថា": "អត់ដឹងថា",
    "សូមអភ័យទោស": "សុំទោសណា",
    "អរគុណច្រើន": "អរគុណណា",
    "តើអ្នកចង់": "ចង់",
    "វាគឺជា": "គឺជា",
    "តើវាជាអ្វី": "អីនោះ",
    "ដូច្នេះហើយ": "អញ្ចឹងហើយ",
    "យ៉ាងណាក៏ដោយ": "ទោះយ៉ាងណា",
    "សូមមេត្តា": "សូម",
}


def naturalize_khmer(text: str, self_pronoun: str = "", other_pronoun: str = "") -> str:
    """Rule-based cleanup pass to make raw MT output read more like
    natural spoken Khmer, plus optional pronoun swapping."""
    for stiff, natural in NATURALIZE_MAP.items():
        text = text.replace(stiff, natural)

    if self_pronoun:
        text = text.replace("ខ្ញុំ", self_pronoun)
    if other_pronoun:
        text = text.replace("អ្នក", other_pronoun).replace("លោកអ្នក", other_pronoun)

    # light emotional-particle heuristics based on end punctuation
    stripped = text.strip()
    if stripped.endswith("?") and not stripped.endswith("ទេ?"):
        stripped = stripped.rstrip("?") + " ដែរ?"
    elif stripped.endswith("!") and not stripped.endswith("ណា!"):
        stripped = stripped.rstrip("!") + " ណា!"

    return stripped


def translate_segments(
    segments: List[Segment],
    self_pronoun: str = "",
    other_pronoun: str = "",
) -> None:
    log("Step 3/6: translating English -> Khmer ...")
    from deep_translator import GoogleTranslator

    translator = GoogleTranslator(source="en", target="km")
    for i, seg in enumerate(segments, start=1):
        try:
            raw = translator.translate(seg.text_en)
            seg.text_km = naturalize_khmer(raw, self_pronoun, other_pronoun)
        except Exception as e:
            log(f"  ! translation failed for segment {i} ({e}); keeping English.")
            seg.text_km = seg.text_en
        if i % 10 == 0 or i == len(segments):
            log(f"  -> translated {i}/{len(segments)} segments")


# --------------------------------------------------------------------------- #
# Step 4: Khmer TTS with Facebook MMS-TTS
# --------------------------------------------------------------------------- #

class KhmerTTS:
    """Wraps facebook/mms-tts-khm, loaded once and reused for every segment."""

    def __init__(self):
        log("Loading Facebook MMS-TTS Khmer model "
            "(first run downloads it from Hugging Face) ...")
        import torch
        from transformers import VitsModel, AutoTokenizer

        self.torch = torch
        self.model = VitsModel.from_pretrained("facebook/mms-tts-khm")
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-khm")
        self.sample_rate = self.model.config.sampling_rate

    def synthesize(self, text: str, out_path: str) -> None:
        import soundfile as sf

        if not text.strip():
            text = " "
        inputs = self.tokenizer(text, return_tensors="pt")
        with self.torch.no_grad():
            output = self.model(**inputs).waveform
        waveform = output.squeeze().cpu().numpy()
        sf.write(out_path, waveform, self.sample_rate)


def synthesize_segments(segments: List[Segment], tmp_dir: str) -> None:
    log("Step 4/6: generating Khmer speech for each segment ...")
    tts = KhmerTTS()
    for i, seg in enumerate(segments, start=1):
        clip_path = os.path.join(tmp_dir, f"seg_{i:04d}.wav")
        tts.synthesize(seg.text_km, clip_path)
        seg.audio_path = clip_path
        if i % 10 == 0 or i == len(segments):
            log(f"  -> synthesized {i}/{len(segments)} clips")


# --------------------------------------------------------------------------- #
# Step 5: time-stretch each clip and stitch into one track
# --------------------------------------------------------------------------- #

def get_wav_duration(path: str) -> float:
    import soundfile as sf
    info = sf.info(path)
    return info.frames / float(info.samplerate)


def stretch_clip(in_path: str, out_path: str, target_duration: float) -> None:
    """Time-stretch a clip to roughly match target_duration using ffmpeg's
    atempo filter (chained to cover ranges outside 0.5-2.0x)."""
    current = get_wav_duration(in_path)
    if current <= 0:
        shutil.copy(in_path, out_path)
        return

    ratio = current / target_duration  # >1 means original is longer -> speed up
    ratio = max(0.5, min(ratio, 2.0))   # clamp so a single atempo stage suffices

    if abs(ratio - 1.0) < 0.03:
        shutil.copy(in_path, out_path)
        return

    run([
        "ffmpeg", "-y", "-i", in_path,
        "-filter:a", f"atempo={ratio:.4f}",
        out_path,
    ])


def build_dubbed_track(segments: List[Segment], total_duration: float,
                        tmp_dir: str, out_wav: str) -> None:
    log("Step 5/6: time-stretching clips and stitching the dubbed track ...")

    # Build one silent base track, then overlay each stretched clip at its
    # original start time using ffmpeg's amix/adelay via a filter_complex.
    stretched_paths = []
    for i, seg in enumerate(segments, start=1):
        stretched_path = os.path.join(tmp_dir, f"stretched_{i:04d}.wav")
        stretch_clip(seg.audio_path, stretched_path, seg.duration)
        stretched_paths.append(stretched_path)

    inputs = []
    filter_parts = []
    for i, (seg, path) in enumerate(zip(segments, stretched_paths)):
        inputs += ["-i", path]
        delay_ms = int(seg.start * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[a{i}]")

    mix_inputs = "".join(f"[a{i}]" for i in range(len(segments)))
    filter_complex = ";".join(filter_parts) + \
        f";{mix_inputs}amix=inputs={len(segments)}:duration=longest:normalize=0[out]"

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", str(total_duration),
        out_wav,
    ]
    run(cmd)
    log(f"  -> dubbed track written to {out_wav}")


# --------------------------------------------------------------------------- #
# Step 6: mux onto original video + compress
# --------------------------------------------------------------------------- #

def mux_and_compress(video_path: str, dubbed_audio: str, out_path: str) -> None:
    log("Step 6/6: muxing dubbed audio onto video and compressing ...")
    run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", dubbed_audio,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-crf", "26", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_path,
    ])
    log(f"  -> final dubbed video written to {out_path}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def get_video_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        return float(result.stdout.decode().strip())
    except ValueError:
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local / free English -> Khmer video dubbing pipeline."
    )
    parser.add_argument("video", help="Path to the source video file.")
    parser.add_argument("-o", "--output", default=None,
                         help="Path for the final dubbed video "
                              "(default: <name>_khmer.mp4).")
    parser.add_argument("--whisper-model", default="small",
                         choices=["tiny", "base", "small", "medium", "large"],
                         help="Whisper model size (default: small).")
    parser.add_argument("--single-speaker", action="store_true",
                         help="Keep only segments from the most-talking "
                              "speaker (requires pyannote.audio + HF token).")
    parser.add_argument("--hf-token", default=os.environ.get("HF_TOKEN"),
                         help="Hugging Face token (needed only with "
                              "--single-speaker). Can also be set via "
                              "the HF_TOKEN environment variable.")
    parser.add_argument("--srt-only", action="store_true",
                         help="Only run steps 1-3 and export EN/KM .srt "
                              "files, skip TTS/mux.")
    parser.add_argument("--self-pronoun", default="",
                         help="Replace the generic 'ខ្ញុំ' with this word "
                              "everywhere (e.g. 'បង', 'អូន', 'ខ្ញុំបាទ').")
    parser.add_argument("--other-pronoun", default="",
                         help="Replace the generic 'អ្នក' with this word "
                              "everywhere (e.g. 'អូន', 'បង', 'ឯង').")
    parser.add_argument("--keep-temp", action="store_true",
                         help="Do not delete the temporary working folder.")
    args = parser.parse_args()

    check_ffmpeg()

    video_path = os.path.abspath(args.video)
    if not os.path.isfile(video_path):
        sys.exit(f"ERROR: video file not found: {video_path}")

    stem = Path(video_path).stem
    out_path = args.output or os.path.join(
        os.path.dirname(video_path), f"{stem}_khmer.mp4"
    )

    tmp_dir = tempfile.mkdtemp(prefix="dub_video_")
    log(f"Working folder: {tmp_dir}")

    try:
        raw_audio = os.path.join(tmp_dir, "audio.wav")
        extract_audio(video_path, raw_audio)

        segments = transcribe(raw_audio, args.whisper_model)
        if not segments:
            sys.exit("No speech detected in the video.")

        if args.single_speaker:
            segments = filter_main_speaker(segments, raw_audio, args.hf_token)
            if not segments:
                sys.exit("No segments left after speaker filtering.")

        translate_segments(segments, args.self_pronoun, args.other_pronoun)

        en_srt = os.path.join(os.path.dirname(video_path), f"{stem}_en.srt")
        km_srt = os.path.join(os.path.dirname(video_path), f"{stem}_km.srt")
        write_srt(segments, en_srt, khmer=False)
        write_srt(segments, km_srt, khmer=True)

        if args.srt_only:
            log("SRT-only mode: skipping TTS and video muxing.")
            return

        synthesize_segments(segments, tmp_dir)

        total_duration = get_video_duration(video_path) or segments[-1].end
        dubbed_track = os.path.join(tmp_dir, "dubbed.wav")
        build_dubbed_track(segments, total_duration, tmp_dir, dubbed_track)

        mux_and_compress(video_path, dubbed_track, out_path)

        log("Done!")
        log(f"  Final video : {out_path}")
        log(f"  English SRT : {en_srt}")
        log(f"  Khmer SRT   : {km_srt}")

    finally:
        if args.keep_temp:
            log(f"Temporary files kept at: {tmp_dir}")
        else:
            shutil.rmtree(tmp_dir, ignore_errors=True)
import streamlit as st

st.title("Video Dubbing (English -> Khmer)")
st.write("សូមស្វាគមន៍មកកាន់ប្រព័ន្ធបកប្រែសំឡេងវីដេអូ!")
if __name__ == "__main__":
    main()import streamlit as st

st.title("Video Dubbing (English -> Khmer)")
st.write("សូមស្វាគមន៍មកកាន់ប្រព័ន្ធបកប្រែសំឡេងវីដេអូ!")

uploaded_file = st.file_uploader("សូមជ្រើសរើស ឬទម្លាក់ឯកសារវីដេអូនៅទីនេះ (MP4, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("ចាប់ផ្តើមបកប្រែសំឡេង (Start Dubbing)"):
        st.success("វីដេអូកំពុងដំណើរការបកប្រែ សូមរង់ចាំបន្តិច...")
