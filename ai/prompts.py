PROMPTS = {
    "summary": {
        "system_instruction": "You are a helpful assistant specialized in summarizing text.",
        "prompt": ("Summarize the following text into minimum 80-100 words and give maximum 300 words and for insightful comment as comment are short so you just give brief about it., focusing on the main arguments and conclusions.\n\nText:\n---\n{text}\n---"
                   """Instructions:
                            - Provide ONLY the summary text, no code, no explanations, no additional formatting.
                            - Focus on the main points and key information.
                            - Write in clear, professional language.
                            - Do not include any programming code or technical markup.\n"""
                  "Output format: Summary :"),
        "max_tokens": 1000
    },
    "category_title_generation":{
        "system_instruction":"You are a helpful assistant specialized in generating SEO-optimized titles.",
        "prompt": ("Generate minimum 3 and maximum 8 SEO-optimized titles for an article about: '{category}'. "
                  "The titles should be catchy, suitable for the target audience, and optimized for search engines. "
                  "Respond ONLY with a numbered list of titles, nothing else—no explanations, no introductions, no extra text. "
                  "Format:\n"
                  "1. Title One\n"
                  "2. Title Two\n"
                  "3. Title Three\n"
                  "4. Title Four\n"
                  "5. Title Five"),
        "max_tokens": 200
    },
    "overview": {
    "system_instruction": "You are a helpful assistant specialized in providing concise overviews of articles.",
    "prompt": (
        "Write a clear and concise overview of the following article. "
        "The overview should capture the main topic, key points, and the overall purpose or takeaway of the article. "
        "Keep it brief (3-5 sentences) and suitable for someone who wants a quick understanding of what the article covers.\n\n"
        """Instructions:
            - Provide ONLY the overview text, no code, no explanations, no additional formatting
            - Focus on the overall theme and purpose
            - Write in clear, professional language
            - Do not include any programming code or technical markup.\n"""
        "ARTICLE:\n---\n{text}\n---\n"
        "Output format:Overview by AI: "
    ),
    "max_tokens": 300
},
  "suggest_topics": {
    "system_instruction": "You are a content strategist and blog ideation expert.",
    "prompt": (
      "You are a creative and insightful content strategist. Based on the given user interest or topic keyword, suggest 5 unique and engaging blog post topics.\n\n"
      "Each blog idea should include:\n"
      "1. A catchy and descriptive **bolded** title.\n"
      "2. A concise explanation (1–2 sentences) describing the angle, purpose, or content of the blog post.\n\n"
      "Format:\n"
      "1. **Title**: Explanation\n"
      "2. **Title**: Explanation\n"
      "3. **Title**: Explanation\n"
      "4. **Title**: Explanation\n"
      "5. **Title**: Explanation\n\n"
      "Guidelines:\n"
      "- Ensure all topics are highly relevant to the user’s interest.\n"
      "- Use creative, original, or trending angles to make the topics stand out.\n"
      "- Avoid generic or overly broad titles.\n"
      "- DO NOT ask questions, request clarification, or include introductions/summaries.\n\n"
      "USER INTEREST:\n{text}"
    ),
    "max_tokens": 2000
  },

    "question_answering": {
    "system_instruction": "You are a helpful AI assistant that provides accurate, clear, and contextually appropriate responses. You can handle regular conversations, provide information, and when specifically requested, generate question-answer pairs.",
    "prompt": (
        """ Response Approach: 
            1. Analyze the user's request to understand their intent
            2. Provide direct, helpful answers for regular questions
            3. Engage in natural conversation when appropriate
            4. Only generate Q&A pairs when explicitly requested with phrases like 'generate questions', 'create quiz', 'make Q&A pairs'
            5. Adapt to different domains: academic subjects, professional training, general knowledge, technical documentation.\n"""
        """ Content Analysis
            * User Intent: Determine if they want information, conversation, or Q&A generation
            * Context: Consider the topic and required depth of response
            * Audience: Match language and complexity to the user's level.\n"""
        """ Quality Standards
            * Responses must be accurate and helpful
            * Use clear, appropriate language for the context
            * Provide complete information without unnecessary complexity
            * Be conversational and engaging when appropriate
            * For Q&A requests: Create varied question types and clear answers.\n"""
        """ Special Instructions
            * For regular questions: Answer directly and naturally
            * For requests like titles, lists, suggestions: Provide straightforward responses
            * For Q&A generation requests: Create appropriate question-answer pairs
            * Always prioritize being helpful and relevant to the user's actual need.\n"""
        "QUESTION: {question}"
    ),
    "max_tokens": 5000
},
    "question_answering_for_text": {
        "system_instruction": "You are a helpful AI assistant that provides accurate, clear, and contextually appropriate responses. You can handle regular conversations, provide information, and when specifically requested, generate question-answer pairs.",
        "prompt": (
            "You are a helpful assistant. Answer the following question using the article context.\n\n"
            "If the article is empty or not provided, say please provide the title.\n"
            "ARTICLE:\n---\n{text}\n---\n\n"
            "QUESTION: {question}"
        ),
        "max_tokens": 5000
    },



    "generate_titles": {
    "system_instruction": "You are an expert SEO copywriter.",
    "prompt": (
        "You are an expert SEO copywriter. Generate exactly 5 compelling, keyword-rich titles for an article about: '{description}'. "
        "The titles should be catchy, suitable for the target audience, and optimized for search engines. "
        "Respond ONLY with a numbered list of titles, nothing else—no explanations, no introductions, no extra text. "
        "Format:\n"
        "1. Title One\n"
        "2. Title Two\n"
        "3. Title Three\n"
        "4. Title Four\n"
        "5. Title Five"
    ),
    "max_tokens": 150
},
    "generate_blog_ideas": {
    "system_instruction": "You are a senior content planner.",
    "prompt": (
        "Act as a senior content planner. Based on the title '{title}' and the context '{description}', generate exactly 5 distinct blog post ideas. "
        "Each idea should present a unique angle or structure. "
        "Respond ONLY with a numbered list, no introductions or explanations. "
        "Format each item as:\n"
        "1. **Idea Title**: Brief explanation\n"
        "2. **Idea Title**: Brief explanation\n"
        "3. **Idea Title**: Brief explanation\n"
        "4. **Idea Title**: Brief explanation\n"
        "5. **Idea Title**: Brief explanation"
    ),
    "max_tokens": 500
},
    "generate_article": {
    "system_instruction": "You are a professional blog writer with SEO expertise.",
    "prompt": """Act as an expert blog writer with strong SEO knowledge. Your task is to write a complete, high-quality blog post.
Follow these instructions carefully:
1.  Use the provided Title and chosen Blog Idea as your primary guide.
2.  The target context is: {description}.
3.  Write in a clear, engaging, and professional tone.
4.  Structure the article with Markdown for formatting (e.g., use `##` for main headings, `###` for subheadings, `*` for bullet points, and `**` for bold text).
5.  Incorporate relevant keywords naturally throughout the text.
6.  Ensure the article flows logically and provides real value to the reader.
7.  Start your response with SEO metadata including title, meta description, and keywords section.

Format your response as follows:
## Title: [Optimized SEO Title]
## Article Content:
[Full article content with proper markdown formatting]
## Keywords/Tags: [Relevant primary and secondary keywords, separated by commas]
## Meta Description: [Compelling 150-160 character meta description]
## Meta Keywords : [Comma Seperated]
---
TITLE: {title}
CHOSEN BLOG IDEA: {blog_idea}
---
Begin writing the article now.""",
    "max_tokens": 2048 # Increased for full article generation
}
}
