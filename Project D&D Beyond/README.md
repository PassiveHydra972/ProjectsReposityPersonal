# D&D Beyond — LLM Character Extractor
## Requirements

- Python 3.12+
- [Ollama](https://ollama.com/) running locally
- A vision-capable model pulled in Ollama (e.g. `qwen2.5vl`, `llava`, `minicpm-v`)
## Run
python main.py
```

## Usage

1. **IMG SCAN** — drag/drop or browse an image, select a vision model, click **Analyse Image**
2. **CONFIG / TEXT** — define output categories (one per line), optionally add supplementary text, save/load presets
3. **OUTPUT** — click **Generate Output** to extract structured data; copy or save the result

## Anti-AI-Fusion

Every generation is **completely stateless**:
- No prior outputs reused
- Prompt rebuilt fresh from only three files:
  - `temp/current_image_analysis.txt`
  - `config/current_config.txt`
  - `temp/current_text_input.txt`

## Project Structure
├── main.py
├── requirements.txt
├── backend/
│   ├── config_manager.py
│   ├── file_manager.py
│   ├── image_analyser.py
│   ├── llm_handler.py
│   ├── output_generator.py
│   └── prompt_builder.py
├── ui/
│   ├── dashboard.py
│   ├── image_scan_tab.py
│   ├── config_tab.py
│   └── output_tab.py
├── config/
│   ├── current_config.txt
│   └── presets/
├── temp/
│   ├── current_image_analysis.txt
│   └── current_text_input.txt
└── output/
    └── generated_output.txt
```
