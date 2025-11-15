# PolicyPath System Architecture

## 🏗️ High-Level Architecture

┌─────────────────────────────────────────────────────────────────┐
│ USER INTERFACE │
│ (HTML Dashboard + JavaScript) │
└────────────────────────────┬────────────────────────────────────┘
│ HTTP POST (JSON)
↓
┌─────────────────────────────────────────────────────────────────┐
│ n8n WORKFLOW ENGINE │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Webhook │→ │ Edit Fields │→ │ Get Patient │ │
│ │ Trigger │ │ │ │ Data │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ ↓ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AI AGENT 1: CLINICAL ANALYZER │ │
│ │ (Google Gemini 2.5 Flash) │ │
│ │ - Extract diagnosis codes │ │
│ │ - Parse genomic markers │ │
│ │ - Identify prior treatments │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ↓ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AI AGENT 2: POLICY MATCHER Decision Engine │ │
│ │ (Google Gemini 2.5 Flash) │ │
│ │ - Match against policy rules │ │
│ │ - Determine approval/denial │ │
│ │ - Calculate confidence score │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ↓ │
│ ┌────────────────────SWITCH NODE──────────────────────────┐ │
│ │ │ │
│ │ ┌──────────┐ ┌──────────┐ ┌─────────────────┐ │ │
│ │ │ APPROVED │ │ DENIED │ │ NEEDS_REVIEW │ │ │
│ │ │ (≥90% │ │ (≥90% │ │ (Fallback) │ │ │
│ │ │confidence)│ │confidence)│ │ │ │ │
│ │ └─────┬────┘ └────┬─────┘ └────────┬────────┘ │ │
│ └────────│────────────│─────────────────│────────────────┘ │
│ ↓ ↓ ↓ │
│ ┌────────────┐ ┌────────────┐ ┌────────────────┐ │
│ │Write PA │ │Write PA │ │Write Review │ │
│ │Tracking │ │Tracking │ │Queue │ │
│ └──────┬─────┘ └──────┬─────┘ └───────┬────────┘ │
│ ↓ ↓ ↓ │
│ ┌────────────┐ ┌────────────┐ ┌────────────────┐ │
│ │Write │ │Write │ │Write Learning │ │
│ │Learning │ │Learning │ │Dataset │ │
│ │Dataset │ │Dataset │ │ │ │
│ └──────┬─────┘ └──────┬─────┘ └───────┬────────┘ │
│ └──────────┬────────────────────┘ │
│ ↓ │
│ ┌─────────────┐ │
│ │ MERGE │ │
│ └──────┬──────┘ │
│ ↓ │
│ ┌────────────────┐ │
│ │ Respond to │ │
│ │ Webhook │ │
│ └────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│ JSON Response
↓
┌─────────────────────────────────────────────────────────────────┐
│ GOOGLE SHEETS DATABASE │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Patient │ │Policy Rules │ │PA Tracking │ │
│ │ Database │ │ │ │Ledger │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ ┌──────────────┐ ┌──────────────┐ │
│ │Review Queue │ │AI Learning │ │
│ │ │ │Dataset │ │
│ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘



## 🔄 Data Flow Sequence

### 1. Request Submission
User fills form → JavaScript captures data → POST to webhook
### 2. Clinical Analysis
Get patient data from sheet → Pass to Gemini → Extract:

Diagnosis code (ICD-10)

Genomic markers (PD-L1, EGFR, etc.)

Prior treatments

Clinical stage


### 3. Policy Matching
Get policy rules → Pass with clinical data to Gemini → Determine:
Which criteria are met
Which criteria are missing
Overall decision (APPROVE/DENY/REVIEW)
Confidence score (0-100)



### 4. Intelligent Routing
IF decision = APPROVED AND confidence ≥ 90:
→ Auto-approve path
ELSE IF decision = DENIED AND confidence ≥ 90:
→ Auto-deny path
ELSE:
→ Human review queue path


### 5. Data Persistence
Write to PA Tracking Ledger (all cases)
Write to AI Learning Dataset (for ML improvement)
Write to Review Queue (if needed)


### 6. Response Generation
Format decision + reasoning → Return JSON → Display in dashboard


## 📊 Database Schema

### Patient Database
patient_id (PK), name, dob, diagnosis_code, diagnosis_name,
treatment_requested, genomic_markers, prior_therapies,
payer_id, clinical_notes_url, status


### Policy Rules
rule_id (PK), policy_name, treatment_name, criteria_description,
approval_criteria, denial_criteria, documentation_requirements,
effective_date, payer_id

### PA Tracking Ledger
request_id (PK), patient_id (FK), submission_time, decision,
decision_time, processing_seconds, confidence_score,
reviewer_name, notes, criteria_met, criteria_missing


### Review Queue
request_id (PK), patient_id (FK), flag_reason,
ai_preliminary_decision, extracted_data, status,
assigned_to, priority, submission_time


### AI Learning Dataset
learning_id (PK), request_id (FK), patient_diagnosis,
genomic_markers, treatment_requested, payer_id,
ai_decision, ai_confidence, ai_reasoning,
human_decision, human_reasoning, disagreement_type,
timestamp, feedback_incorporated



## 🤖 AI Agent Configuration

### Agent 1: Clinical Data Extractor
**Model**: Google Gemini 2.5 Flash  
**Temperature**: 0.1 (deterministic)  
**Prompt**: Extract clinical data from patient record

### Agent 2: Policy Decision Maker
**Model**: Google Gemini 2.5 Flash  
**Temperature**: 0.2 (mostly deterministic)  
**Prompt**: Match clinical data against policy rules

## 🔒 Security Considerations

### Current Implementation (Demo)
- Google Sheets with restricted access
- HTTPS webhook endpoints
- Client-side validation

### Production Requirements
- HIPAA-compliant hosting
- Encrypted data at rest and in transit
- Audit logging of all access
- Role-based access control (RBAC)
- PHI de-identification options

## 📈 Scalability

### Current Capacity
- **Requests**: 100/hour
- **Storage**: Google Sheets (10K rows)
- **Response Time**: 8-15 seconds

### Production Scaling
- **Database**: Migrate to PostgreSQL
- **Caching**: Redis for policy rules
- **Load Balancing**: Multiple n8n instances
- **Async Processing**: Queue system for high volume
- **Target**: 10K+ requests/hour

## 🔧 Configuration

### Environment Variables
N8N_WEBHOOK_URL=https://localhost:5678/webhook/policypath-submit
GOOGLE_SHEETS_ID=your-sheet-id
GEMINI_API_KEY=your-api-key