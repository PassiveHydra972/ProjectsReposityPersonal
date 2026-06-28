"""
image_analyser.py
Sends an image to a vision-capable LLM and saves the raw analysis.
ALWAYS overwrites — never appends.
"""

from pathlib import Path

from backend import file_manager as fm
from backend import provider_manager as pm

IMAGE_ANALYSIS_SYSTEM = (
    "You are a precise visual analysis assistant. "
    "Describe only what you can directly observe in the image. "
    "Do not invent or guess details you cannot see. "
    "Organise your output into clear labelled sections."
)

IMAGE_ANALYSIS_PROMPT = (
    "Analyse this image in detail. "
    "Describe every observable physical characteristic of the subject(s). "
    "Cover: hair colour and style, eye colour, skin tone, approximate age appearance, "
    "height impression, build, clothing, accessories, expression, and any other "
    "notable visual features. "
    "Format your response with clear section labels followed by concise descriptions. "
    "Only describe what you can actually see. "
    "Do not speculate beyond the image."
)


def analyse_image(
    image_path: str | Path,
    model: str,
    progress_callback=None,
) -> str:
    """
    Analyse an image using the given vision model.
    Saves result to temp/current_image_analysis.txt (always overwritten).
    Returns the analysis text.
    Raises llm_handler.OllamaError on failure.

    progress_callback: called with each streamed token (str).
    """
    result = pm.generate_with_image(
        model=model,
        prompt=IMAGE_ANALYSIS_PROMPT,
        image_path=image_path,
        system=IMAGE_ANALYSIS_SYSTEM,
        temperature=0.3,
        chunk_callback=progress_callback,
    )

    # CRITICAL: Always overwrite, never append
    fm.write_image_analysis(result)

    return result
