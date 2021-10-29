import openai


# Content Generation


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
        max_tokens=200,
        top_p=1.0,
        frequency_penalty=0.4,
        presence_penalty=0.0,
        stop=["\"\"\""]
    )
    story = response['choices'][0]['text']
    print(f"prompt:\n{code}\nquery:\n1.{story}")
    return str(story)


def fix(code):
    prompt = "##### Fix bugs in the below function\n\n" \
             "### Buggy Python" \
             f"{code}\n\n" \
             "### Fixed Python" \

    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["###"]
    )
    story = response['choices'][0]['text']
    print(f"prompt:\n{code}\nquery:\n{story}")
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

# Content filtering


def topic_related(question):
    import os
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        engine="curie-instruct-beta",
        prompt="Write \"Yes\" if the sentence is related to computers, otherwise answer \"No\"\n\n"
               f"S: {question}\n"
               "Y/N:",
        temperature=0,
        max_tokens=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]
    )
    story = response['choices'][0]['text']
    print(story)
    if story == " Yes":
        return True
    else:
        return False


def secure_filter(prompt):
    content_to_classify = prompt

    response = openai.Completion.create(
        engine="content-filter-alpha",
        prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        logprobs=10
    )
    output_label = response["choices"][0]["text"]

    toxic_threshold = -0.355

    if output_label == "2":
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"

            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

    if output_label not in ["0", "1", "2"]:
        output_label = "2"

    return output_label
