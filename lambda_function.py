import os
import json
import urllib.request

SKILL_ID = os.environ["SKILL_ID"]
API_KEY = os.environ["API_KEY"]
API_URL = "https://api.perplexity.ai/chat/completions"
WELCOME_PROMPT = "Willkommen bei Perplexity. Was möchtest du wissen?"
ERROR_PROMPT = "Entschuldigung, es ist ein Fehler aufgetreten."

def lambda_handler(event, context):
    if event["session"]["application"]["applicationId"] != SKILL_ID:
        raise ValueError("Ungültige Application ID")
    try:
        req = event["request"]
        if req["type"] == "LaunchRequest":
            return build_response(WELCOME_PROMPT, WELCOME_PROMPT, False)
        if req["type"] == "IntentRequest" and req["intent"]["name"] == "AskPerplexityIntent":
            query = req["intent"]["slots"]["query"]["value"]
            answer = ask_perplexity(query)
            return build_response(answer, None, False)
        if req["type"] == "SessionEndedRequest":
            return {}
    except Exception:
        return build_response(ERROR_PROMPT, ERROR_PROMPT, False)

def ask_perplexity(query: str) -> str:
    system_content = (
        "Du bist ein hilfreicher Assistent, der präzise und knapp antwortet. Deine Antworten werden von Alexa vorgelesen, verzichte daher vollständig auf Quellenangaben, ausser du wirst danach gefragt."
    )
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user",   "content": query}
        ]
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type":    "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read())["choices"][0]["message"]["content"].strip()

def build_response(output: str, reprompt: str = None, end_session: bool = True) -> dict:
    ssml_output = f"<speak><voice name=\"Hans\">{output}</voice></speak>"
    speech = {"outputSpeech": {"type": "SSML", "ssml": ssml_output}}
    if reprompt is not None:
        ssml_reprompt = f"<speak><voice name=\"Hans\">{reprompt}</voice></speak>"
        speech["reprompt"] = {"outputSpeech": {"type": "SSML", "ssml": ssml_reprompt}}
    return {"version": "1.0", "response": {**speech, "shouldEndSession": end_session}}

