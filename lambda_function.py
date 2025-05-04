import os
import json
import urllib.request

SKILL_ID = os.environ["SKILL_ID"]
API_KEY = os.environ["API_KEY"]
API_URL = "https://api.perplexity.ai/chat/completions"

WELCOME_TEXT = "Willkommen bei Perplexity AI. Was möchtest du wissen?"
HELP_TEXT = "Du kannst mir jede Frage stellen. Was möchtest du wissen?"
GOODBYE_TEXT = "Auf Wiedersehen!"
ERROR_TEXT = "Entschuldigung, es ist ein Fehler aufgetreten."
FOLLOWUP_TEXT = "Möchtest du sonst noch etwas wissen?"

def lambda_handler(event, context):
    if event["session"]["application"]["applicationId"] != SKILL_ID:
        raise ValueError("Ungültige Application ID")
    req = event["request"]
    if req["type"] == "LaunchRequest":
        return build_response(WELCOME_TEXT, WELCOME_TEXT, False)
    if req["type"] == "IntentRequest":
        intent = req["intent"]["name"]
        slots = req["intent"].get("slots", {})
        if intent == "AskPerplexityIntent":
            query = slots.get("query", {}).get("value")
            if not query:
                return build_response(HELP_TEXT, HELP_TEXT, False)
            answer = ask_perplexity(query)
            return build_response(answer, FOLLOWUP_TEXT, False)
        if intent == "AMAZON.HelpIntent":
            return build_response(HELP_TEXT, HELP_TEXT, False)
        if intent in ("AMAZON.CancelIntent", "AMAZON.StopIntent"):
            return build_response(GOODBYE_TEXT, None, True)
        if intent == "AMAZON.NavigateHomeIntent":
            return build_response(WELCOME_TEXT, WELCOME_TEXT, False)
    if req["type"] == "SessionEndedRequest":
        return {}
    return build_response(ERROR_TEXT, None, True)

def ask_perplexity(query: str) -> str:
    system_msg = (
        "Du bist ein hilfreicher Assistent, der präzise und knapp antwortet. "
        "Deine Antworten werden von Alexa vorgelesen, verzichte daher vollständig "
        "auf Quellenangaben, außer du wirst danach gefragt."
    )
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": query}
        ]
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return json.loads(res.read())["choices"][0]["message"]["content"].strip()
    except Exception:
        return ERROR_TEXT

def build_response(text: str, reprompt: str = None, end_session: bool = True) -> dict:
    def ssml(s: str) -> dict:
        return {"type": "SSML", "ssml": f"<speak><voice name=\"Hans\">{s}</voice></speak>"}
    speech = {"outputSpeech": ssml(text)}
    if reprompt is not None:
        speech["reprompt"] = {"outputSpeech": ssml(reprompt)}
    return {"version": "1.0", "response": {**speech, "shouldEndSession": end_session}}
