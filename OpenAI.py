import openai


def explain(code):
    prompt = "# Python 3\n" \
             f"{code}\n\n" \
             "\"\"\"\n" \
             "Here is what the code above is doing:\n" \
             "1."

    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        temperature=0,
        max_tokens=64*3,
        top_p=1.0,
        frequency_penalty=0.4,
        presence_penalty=0.0,
        stop=["\"\"\""]
    )
    story = response['choices'][0]['text']
    print(f"prompt:\n{code}\nquery: {story}")
    return str(story)


def code(instructions):
    prompt = '"""\n' \
             f'{instructions}' \
             '"""'
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1.0,
        frequency_penalty=0.4,
        presence_penalty=0.0,
        stop=['"""']
    )
    story = response['choices'][0]['text']
    print(f"prompt:\n{instructions}\nquery: {story}")
    return str(story)


def ask(question):
    prompt = "Python chatbot\n\n\n" \
             "You: How do I combine lists?\n" \
             "Python chatbot: You can use the `extend()` method.\n" \
             f"You: {question}\n" \
             "Python chatbot:"
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        temperature=0,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=['You:']
    )
    story = response['choices'][0]['text']
    print(f"prompt: {question}\nquery: {story}")
    return str(story)
