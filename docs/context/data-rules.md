# Data rules (what may go to an AI tool)
- Allowed: this repo's code, the BRD, stories, test cases with placeholder tokens.
- Mask first: screenshots or page text from Verify Users / Manage Users (customer names, phones, emails) - replace with [USER_NAME_1], [PHONE_1], [EMAIL_1] before pasting anywhere.
- Never: .env contents, passwords (even demo ones), API tokens, Xray client secrets, real customer PII.
- Only org-managed AI seats (no free consumer chat tools) for any client work.
- Test data in fixtures/ must be synthetic or non-sensitive.
