"""
prompt_builder.py
Constructs a fresh, stateless prompt for every generation.
No history. No memory. No hidden context.
"""

from backend import file_manager as fm


SYSTEM_PROMPT = (
    "You are a structured data extraction assistant. "
    "You extract and format information ONLY from the provided context. "
    "Never invent details not supported by the context. "
    "Never reference prior conversations or sessions. "
    "Respond only with the structured output — no commentary, no preamble."
)


def build_output_prompt() -> tuple[str, str]:
    """
    Build a completely isolated prompt from current files only.

    Returns:
        (system_prompt, user_prompt)

    Sources used (and only these):
        - temp/current_image_analysis.txt
        - config/current_config.txt
        - temp/current_text_input.txt
    """
    image_analysis = fm.read_image_analysis().strip()
    config_text = fm.read_config().strip()
    text_input = fm.read_text_input().strip()

    categories = [line.strip() for line in config_text.splitlines() if line.strip()]

    # Build category instructions
    category_block = "\n".join(f"- {cat}" for cat in categories)

    sections = []

    sections.append(
        "=== REQUIRED OUTPUT CATEGORIES ===\n"
        f"{category_block}\n\n"
        "For each category:\n"
        "  - If clearly visible/stated: provide a direct answer.\n"
        "  - If uncertain: prefix with 'Estimated'.\n"
        "  - If unknown: write 'Unknown' or 'Not specified'.\n"
        "  - Never invent details not present in the provided context.\n"
        "  - Output ONLY the listed categories. Nothing else."
    )

    if image_analysis and not image_analysis.startswith("(No image"):
        sections.append(f"=== IMAGE ANALYSIS ===\n{image_analysis}")
    else:
        sections.append("=== IMAGE ANALYSIS ===\n(No image analysis available.)")

    if text_input:
        sections.append(f"=== SUPPLEMENTARY TEXT INPUT ===\n{text_input}")

    sections.append(
        "=== TASK ===\n"
        "Using ONLY the information provided above, fill in each required category. "
        "Format your response exactly as:\n\n"
        + "\n\n".join(f"{cat}:\n[value]" for cat in categories)
    )

    user_prompt = "\n\n".join(sections)

    return SYSTEM_PROMPT, user_prompt
