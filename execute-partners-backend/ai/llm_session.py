from config import get_model
from session_prompts import PROMPTS


class Conversation:
    def __init__(self, conversation_id, max_history=5):
        self.conversation_id = conversation_id
        self.history = []
        self.max_history = max_history

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[2:]

    def get_history_as_string(self):
        history_string = ""
        for message in self.history:
            history_string += f"{message['role']}: {message['content']}\n"
        return history_string

    def clear_history(self):
        self.history = []


conversations = {}


def call_gemini(conversation_id, prompt_key, context_vars=None, max_tok=None, use_history=True):
    try:
        if prompt_key not in PROMPTS:
            return f"Error: Prompt key '{prompt_key}' not found."

        if conversation_id not in conversations:
            conversations[conversation_id] = Conversation(conversation_id)
        conversation = conversations[conversation_id]

        prompt_config = PROMPTS[prompt_key]
        prompt_template = prompt_config["prompt"]

        if use_history:
            history_string = conversation.get_history_as_string()
            if context_vars is None:
                context_vars = {}
            context_vars["history"] = history_string
        else:
            if context_vars is None:
                context_vars = {}
            if "history" not in context_vars:
                context_vars["history"] = ""

        final_prompt = prompt_template.format(**context_vars)
        max_output_tokens = max_tok if max_tok is not None else prompt_config["max_tokens"]

        response = get_model().generate_content(
            final_prompt,
            generation_config={"max_output_tokens": max_output_tokens},
        )
        response_text = response.text.strip()

        user_input = context_vars.get("userInput", "") if context_vars else ""
        conversation.add_message("user", user_input)
        conversation.add_message("model", response_text)

        return response_text

    except Exception as e:
        return f"An error occurred with the Gemini API: {e}"


def close_conversation(conversation_id):
    if conversation_id in conversations:
        conversations[conversation_id].clear_history()
        del conversations[conversation_id]
