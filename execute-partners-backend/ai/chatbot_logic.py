import re
from llm_service import call_gemini
from config import ARTICLE

# === Article Writer Module ===
class ArticleWriterModule:
    """Manages the multi-step process of writing an article."""
    def __init__(self):
        self.stage = "idle"
        self.context = {}

    def reset(self):
        self.stage = "idle"
        self.context = {}

    def handle(self, user_msg: str):
        """Processes user input through the article writing workflow."""
        msg_lower = user_msg.strip().lower()

        # === Interrupt Check ===
        interrupt_intent = detect_intent(user_msg)
        if interrupt_intent in ["summary", "topic", "cancel", "resume"] and self.stage != "idle":
            return {"interrupt": True, "intent": interrupt_intent, "user_msg": user_msg}

        if self.stage == "idle":
            if "write" in msg_lower or "new article" in msg_lower:
                self.stage = "awaiting_context"
                return "Great! Let's write an article. First, please tell me: 1. What industry or topic is this for? 2. Who is the target audience?"
            return None  # Not handled by this module

        elif self.stage == "awaiting_context":
            self.context["description"] = user_msg
            self.stage = "generating_titles"
            return self._generate_titles()

        elif self.stage == "awaiting_title_choice":
            self.context["chosen_title"] = user_msg
            self.context["title"] = user_msg
            self.stage = "generating_blog_ideas"
            return self._generate_blog_ideas()

        elif self.stage == "awaiting_blog_choice":
            self.context["chosen_blog"] = user_msg
            self.context["blog_idea"] = user_msg
            self.stage = "generating_final_article"
            return self._generate_article()

        return None  # Should not be reached

    def _generate_titles(self):
        titles = call_gemini("generate_titles", context_vars={"description": self.context["description"]})
        self.context["titles"] = titles
        self.stage = "awaiting_title_choice"
        return f"Here are the Generated Titles:{titles['text']}"

    def _generate_blog_ideas(self):
        ideas = call_gemini("generate_blog_ideas", context_vars=self.context)
        self.context["ideas"] = ideas
        self.stage = "awaiting_blog_choice"
        return f"Here are Generated Blog Ideas: {ideas['text']}"

    def _generate_article(self):
        context_vars = {
            "title": self.context.get("title", ""),
            "blog_idea": self.context.get("chosen_blog", ""),
            "description": self.context.get("description", "")
        }
        article = call_gemini("generate_article", context_vars=context_vars)
        final_response = f"Here is the Generated article: {article['text']}"
        self.reset()
        return final_response

# === Intent Detection ===
def detect_intent(msg: str):
    msg_lower = msg.lower()

    if "summary" in msg_lower or "summarize" in msg_lower:
        return "summary"
    # if "topic" in msg_lower or "suggest" in msg_lower:
    #     return "topic"
    if any(x in msg_lower for x in ["stop", "cancel", "exit"]):
        return "cancel"
    if any(x in msg_lower for x in ["continue", "go on", "resume"]):
        return "resume"
    else:
        return "qa"
    return "unknown"

# === Main Chat Engine Function ===
def get_bot_response(user_msg: str, text: str, writer_module: ArticleWriterModule) -> str:
    """
    Determines the user's intent and gets the appropriate response.
    This is the main entry point for the logic.
    """
    # Greeting
    if re.match(r"^\s*(hi|hello|hey)\b.*", user_msg.lower()):
        return "Hi there! How can I help you today? You can ask me to summarize the article, suggest new topics, ask a question about it, or write a new article."

    # Try article writing flow
    module_response = writer_module.handle(user_msg)

    # Handle interrupt logic
    if isinstance(module_response, dict) and module_response.get("interrupt"):
        intent = module_response["intent"]
        interrupted_msg = module_response["user_msg"]

        if intent == "summary":
            return call_gemini("summary", context_vars={"text": text}) + "\n\n(You're currently in the middle of writing an article. You can continue when ready.)"
        # elif intent == "topic":
        #     return call_gemini("suggest_topics", context_vars={"text": text}) + "\n\n(You're currently in the middle of writing an article. You can continue when ready.)"
        elif intent == "qa":
            return call_gemini("question_answering", context_vars={"text": text, "question": interrupted_msg}) + "\n\n(You're currently in the middle of writing an article. You can continue when ready.)"
        elif intent == "cancel":
            writer_module.reset()
            return "Okay, I’ve cancelled the current article-writing process. Let me know if you'd like to start again."
        elif intent == "resume":
            return "You're currently in the middle of writing an article. Please continue by providing the next input based on the last step."

    elif module_response:
        return module_response

    # Fallback intent logic (if not in article flow)
    intent = detect_intent(user_msg)
    if intent == "summary":
        return call_gemini("summary", context_vars={"text": text})
    elif intent == "topic":
        return call_gemini("suggest_topics", context_vars={"text": text})
    elif intent == "qa":
        return call_gemini("question_answering", context_vars={"text": text, "question": user_msg})
    elif intent == "cancel":
        writer_module.reset()
        return "Cancelled any ongoing tasks. Let me know if you'd like to begin again."
    elif intent == "resume":
        return "You haven't started writing an article yet. Say 'write a new article' to begin."
    else:
        return "I'm not sure how to respond to that. Could you please clarify your request?"
