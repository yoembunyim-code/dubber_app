# វិធីប្រើប្រាស់ - Video Dubbing (English -> Khmer)

## តម្រូវការ (Requirements)
- Python 3.9+
- ffmpeg ត្រូវបានដំឡើងហើយនៅលើម៉ាស៊ីនរបស់អ្នក
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: ទាញយកពី https://ffmpeg.org/download.html ហើយបន្ថែមទៅ PATH

## ការដំឡើង (Installation)
បើកកម្មវិធី Terminal ហើយវាយ៖

```bash
pip install openai-whisper deep-translator transformers torch soundfile pydub numpy scipy
```

ចំណាំ៖ លើកទីមួយដែលរត់ script នេះ វានឹងទាញយក model មួយចំនួន (Whisper + MMS-TTS Khmer)
ដោយស្វ័យប្រវត្តិពី internet (ប្រហែល ~1-2GB) ។ បន្ទាប់ពីនោះ model ត្រូវបានរក្សាទុក
(cache) នៅលើម៉ាស៊ីនរបស់អ្នក ហើយអាចប្រើ offline បាន។

## របៀបប្រើ (Usage)

```bash
python dub_video.py input.mp4 output.mp4
```

### ជម្រើសបន្ថែម (Optional flags)

```bash
python dub_video.py input.mp4 output.mp4 \
    --whisper-model small \
    --crf 30 \
    --scale 854:-2 \
    --audio-bitrate 192k
```

| Flag | អត្ថន័យ | លំនាំដើម |
|---|---|---|
| `--whisper-model` | ភាពត្រឹមត្រូវនៃការស្តាប់សំឡេង (tiny/base/small/medium/large) | small |
| `--crf` | គុណភាព/ទំហំវីដេអូ (លេខធំ = ទំហំតូច គុណភាពទាប) | 30 |
| `--scale` | គុណភាពបង្ហាញវីដេអូ | 854:-2 (~480p) |
| `--audio-bitrate` | គុណភាពសំឡេង (រក្សាឲ្យខ្ពស់ដើម្បីឲ្យសំឡេងច្បាស់) | 192k |

## ដើម្បីកាត់បន្ថយទំហំឯកសារបន្ថែមទៀត
- បង្កើន `--crf` ទៅ 32-35
- បន្ថយ `--scale` ទៅ `640:-2` ឬ `480:-2`
- កុំបន្ថយ `--audio-bitrate` ក្រោម 128k បើចង់ឲ្យសំឡេងនៅតែច្បាស់

## កំណត់ចំណាំសំខាន់ៗ
1. **deep-translator** ជាឧបករណ៍ឥតគិតថ្លៃ ប្រើ Google Translate តាម Internet
   ក្នុងផ្ទៃខាងក្រោយ (មិនតម្រូវ API Key ទេ ប៉ុន្តែតម្រូវការ internet connection)។
2. **MMS-TTS Khmer** ជាម៉ូដែលសំឡេងឥតគិតថ្លៃ ដំណើរការ local ពេលទាញយករួច ប៉ុន្តែសំឡេង
   អាចមិនល្អឥតខ្ចោះដូចសំឡេងមនុស្សពិត។
3. ការកែសម្រួល "speed" របស់ clip ដើម្បីតម្រូវទៅនឹង timestamp ដើម ជាវិធីសាមញ្ញ
   (pitch នឹងផ្លាស់ប្តូរបន្តិចបើត្រូវលឿន/យឺតខ្លាំង) ។ បើចង់បានគុណភាពសំឡេងកាន់តែល្អ
   អាចប្តូរទៅប្រើ library ដូចជា `pyrubberband` ដើម្បីផ្លាស់ប្តូរល្បឿនដោយមិនប៉ះពាល់ pitch។
