# Bandwise

**IELTS practice backend scaffold — Team Hackoholics.**

Bandwise explores the backend of an IELTS speaking and writing practice service: account registration, submission storage, speech transcription, and practice-history summaries.

**Status:** prototype backend. Speaking and writing band scores are fixed placeholders in the code. A trained scoring model, criterion-level assessment, and examiner validation have not been implemented in this repository.

## What exists

| Feature | Current behavior |
| --- | --- |
| Registration & login | Stores password hashes and returns JWTs |
| Speaking submission | Saves uploaded audio and calls Google's speech-recognition service |
| Speaking scores | Returns hardcoded criterion scores and overall band |
| Writing submission | Stores essay text with hardcoded scores and empty corrections |
| Practice dashboard | Returns counts, average stored scores, and mistake-log entries |
| Subscription route | Updates stored plan fields; no payment integration |

The project consists of [bandwise.py](bandwise.py). There is no React frontend, FastAPI backend, trained PyTorch model, or published validation dataset in this checkout.

## Technologies

Python · Flask · Flask-CORS · Flask-SQLAlchemy · SQLite by default · PyJWT · SpeechRecognition · python-dotenv

Audio is sent to an external transcription service by `recognize_google`; transcription is not local or offline. There is no timestamp/prosody analysis in the current implementation.

## Run locally

```bash
git clone https://github.com/vvsanjay/AI-Powered-IELTS-preparation-ans-evaluation-platform-.git
cd AI-Powered-IELTS-preparation-ans-evaluation-platform-
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
mkdir -p uploads
python bandwise.py
```

Set a locally generated `SECRET_KEY` in `.env`. Windows users can create the environment file and `uploads` folder through their file manager or PowerShell.

The development server listens on `http://127.0.0.1:5000` and creates its database tables at startup. These setup instructions follow the source imports; dependency resolution and the full runtime workflow still need verification.

## API routes

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Obtain a login token |
| POST | `/api/speaking/upload` | Upload audio and store a transcript |
| POST | `/api/writing/submit` | Store an essay |
| GET | `/api/dashboard/<user_id>` | Summarize practice records |
| POST | `/api/subscription/upgrade` | Change stored subscription fields |

## Important prototype boundaries

The non-auth routes accept supplied user IDs without enforcing the issued JWTs. Input validation, ownership checks, upload limits, and error handling need work before hosting this beyond a local prototype. The app runs with Flask debug mode enabled.

Current scores should be read only as demonstration values. There is no evidence here for accuracy percentages, agreement with examiners, processing-time benchmarks, or thousands of rated training responses.

## Next milestones

- Enforce authentication and ownership across all user-specific routes.
- Replace placeholder scores with a clearly specified, testable assessment pipeline.
- Add a practice UI, upload handling, and meaningful feedback.
- Evaluate with independently rated examples and publish the methodology and results.
- Add integration tests and a reproducible deployment configuration.

## Team credit

The original README identifies **Team Hackoholics** and a hackathon submission. That team credit is retained; individual application-code contributions are not inferred.
