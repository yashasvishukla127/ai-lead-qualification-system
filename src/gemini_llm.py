# import os

# import google.generativeai as genai

# from dotenv import load_dotenv

# from models import LeadProfile, EmailDraft

# from pydantic import ValidationError


# load_dotenv()

# genai.configure(
#     api_key=os.getenv("GOOGLE_API_KEY")
# )

# model = genai.GenerativeModel(
#     "gemini-2.5-flash"
# )


# async def analyse_lead(lead_text: str) -> LeadProfile | None:

#     system_prompt = """
# You are a mortgage broker assistant.

# You must respond ONLY with valid JSON.

# The JSON must match this schema exactly:

# {
#     "intent_score": 8,
#     "situation_summary": "Customer is looking for a first home loan.",
#     "urgency": "high",
#     "is_first_buyer": true,
#     "recommended_approach": "Schedule a consultation call immediately.",
#     "confidence": 0.92
# }

# Rules:
# - intent_score must be between 1 and 10
# - urgency must be one of: low, medium, high
# - confidence must be between 0 and 1
# - Return ONLY JSON
# """

#     full_prompt = f"""
# {system_prompt}

# Lead:
# {lead_text}
# """

#     try:

#         response = model.generate_content(
#             full_prompt,
#             generation_config={
#                 "temperature": 0,
#                 "max_output_tokens": 500
#             }
#         )

#         text = response.text.strip()

#         print("\nRAW GEMINI RESPONSE:")
#         print(text)

#         cleaned_text = (
#             text.replace("```json", "")
#             .replace("```", "")
#             .strip()
#         )

#         lead_profile = LeadProfile.model_validate_json(
#             cleaned_text
#         )

#         return lead_profile

#     except ValidationError as e:
#         print(f"Pydantic validation failed:\n{e}")
#         return None

#     except Exception as e:
#         print(f"Unexpected error:\n{e}")
#         return None


# async def draft_email(
#     lead_profile: LeadProfile
# ) -> EmailDraft | None:

#     system_prompt = """
# You are an expert mortgage broker assistant.

# Write warm, human, personalised mortgage outreach emails.

# You must respond ONLY with valid JSON.

# JSON schema:

# {
#   "subject": "Helping You With Your First Home Loan",
#   "body": "Hi John...",
#   "tone_score": 8,
#   "word_count": 120,
#   "key_personalisation": "Mentions urgency and first-home situation."
# }

# Rules:
# - tone_score between 1 and 10
# - Return ONLY raw JSON.
# - Do NOT use markdown.
# - Do NOT use ```json.
#  -Do NOT explain anything.
# """

#     full_prompt = f"""
# {system_prompt}

# Lead Profile:
# {lead_profile.model_dump()}
# """

#     try:

#         response = model.generate_content(
#             full_prompt,
#             generation_config={
#                 "temperature": 0.6,
#                 "max_output_tokens": 600
#             }
#         )

#         text = response.text.strip()

#         cleaned_text = (
#             text.replace("```json", "")
#             .replace("```", "")
#             .strip()
#         )

#         email_draft = EmailDraft.model_validate_json(
#             cleaned_text
#         )

#         return email_draft

#     except Exception as e:
#         print(f"Error generating email: {e}")
#         return None


# async def process_lead(lead_text: str):

#     lead_profile = await analyse_lead(
#         lead_text
#     )

#     if lead_profile is None:
#         return {"error": "Lead analysis failed"}

#     email_draft = await draft_email(
#         lead_profile
#     )

#     return {
#         "lead_profile": lead_profile,
#         "email_draft": email_draft
#     }