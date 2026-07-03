from config import get_model
from prompts import PROMPTS

def call_gemini(prompt_key, context_vars=None, max_tok=None):
    """
    Calls the Gemini API with a structured prompt and returns response + token usage.
    """
    try:
        if prompt_key not in PROMPTS:
            return {"error": f"⚠️ Error: Prompt key '{prompt_key}' not found."}

        prompt_config = PROMPTS[prompt_key]
        prompt_template = prompt_config["prompt"]
        final_prompt = prompt_template.format(**context_vars) if context_vars else prompt_template
        max_output_tokens = max_tok if max_tok is not None else prompt_config.get("max_tokens", 256)

        # === Gemini API Call ===
        response = get_model().generate_content(
            final_prompt,
            generation_config={"max_output_tokens": max_output_tokens}
        )

        # Optional: estimate token count manually if not available
        input_tokens = len(final_prompt.split())
        output_tokens = len(response.text.strip().split())

        return {
            "text": response.text.strip()
        }

    except Exception as e:
        return {"error": f"⚠️ An error occurred with the Gemini API: {e}"}
