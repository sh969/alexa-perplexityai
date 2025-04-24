# Perplexity-Alexa Skill (Lambda)

A tiny Python 3.11 Lambda that lets Alexa query Perplexity’s **sonar** model – no external layers, no extra packages.

## Requirements
- AWS account (for Lambda)
- Alexa Dev account (to create the skill)
- Perplexity Pro API key – \$5 free credit, sonar is ~\$0.0006 per 1 k tokens

## Deployment (5 steps)
1. **AWS Lambda** → *Create function* → Python 3.12  
   Upload `lambda_function.py`
2. **Env vars**  
   `SKILL_ID` = Alexa Skill ID  
   `API_KEY`  = Perplexity secret key
3. Memory 128 MB, Timeout 15 s, Save & Deploy
4. Add trigger **Alexa Skills Kit**, paste Skill ID
5. **Alexa Dev Console**  
   *Create skill* → Custom → *Provision your own*  
   Invocation name: “perplexity”  
   Add intent

## Author
Sebastian Horstmann