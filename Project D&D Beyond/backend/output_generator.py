"""
output_generator.py
Generates structured output using a fresh, stateless LLM call.
Saves result to output/generated_output.txt.
"""

from backend import file_manager as fm
from backend import provider_manager as pm
from backend import prompt_builder as pb


def generate_output(
    model: str,
    progress_callback=None,
    chunk_callback=None,
) -> str:
    """
    Build a fresh prompt, call the LLM once (stateless), save and return result.
    Raises llm_handler.OllamaError on failure.

    chunk_callback: optional callable(str) called with each streamed token.
    """
    if progress_callback:
        progress_callback("Building prompt…")

    system_prompt, user_prompt = pb.build_output_prompt()

    if progress_callback:
        progress_callback("Generating…")

    result = pm.generate_text(
        model=model,
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.5,
        chunk_callback=chunk_callback,
    )

    fm.write_output(result)

    if progress_callback:
        progress_callback("Done. Output saved.")

    return result
