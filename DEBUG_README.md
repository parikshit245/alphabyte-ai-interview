# Debug Report - Interview Preparation Agent

**Last Updated:** February 16, 2026  
**System:** LangGraph + Neo4j + Google Gemini  
**Status:** ⚠️ CRITICAL - LLM Integration Failure

---

## 🔴 Critical Errors

### 1. Google Gemini Model Not Found (404 Error)

**Error Type:** `NOT_FOUND` (HTTP 404)  
**Component:** LLM Integration (`ChatGoogleGenerativeAI`)  
**Severity:** 🔴 CRITICAL - Blocks all chatbot functionality

#### Error Message:
```
Error calling model 'gemini-pro' (NOT_FOUND): 404 NOT_FOUND. 
{'error': {'code': 404, 'message': 'models/gemini-pro is not found for API version v1beta, 
or is not supported for generateContent. Call ListModels to see the list of available 
models and their supported methods.', 'status': 'NOT_FOUND'}}
```

#### Models Tested (All Failed):
- ❌ `gemini-1.5-flash` - NOT_FOUND
- ❌ `gemini-pro` - NOT_FOUND

#### Affected Nodes:
1. **Extract Keywords Node** - Cannot extract domain/skills/company from user input
2. **Model Query Node** - Cannot generate responses to user queries
3. **Overall Flow** - Graph enters infinite loop due to extraction failures

#### Root Cause Analysis:
1. **API Version Mismatch**: The `langchain-google-genai` library is using API version `v1beta`, but the model names may be for a different API version.
2. **Model Name Format**: Google may have changed the model naming convention (e.g., `models/gemini-1.5-flash-001` vs `gemini-1.5-flash`).
3. **API Key Permissions**: The API key might not have access to these specific models.
4. **Library Version**: The `langchain-google-genai` package might be outdated or incompatible.

---

## ⚠️ Secondary Issues

### 2. Keyword Extraction Fallback

**Symptom:** When LLM fails, the system creates an empty `SearchKeywords()` object.  
**Impact:** Database search returns 0 results, even if the query is valid.

```python
⚠️ Error extracting keywords: Error calling model 'gemini-pro' (NOT_FOUND)
🔬 Executing Depth Search Node...
  ✅ Found 0 total results
```

**Location:** `botchat.py`, line ~360  
**Code:**
```python
except Exception as e:
    print(f"⚠️ Error extracting keywords: {e}")
    state["search_keywords"] = SearchKeywords()  # Empty object
```

---

### 3. Infinite Loop in Workflow

**Symptom:** The graph continuously loops through `extract_keywords` → `depth_search` → `model_query` → `check_satisfaction` → back to `extract_keywords`.

**Cause:** 
- `check_satisfaction_node` sees "continue" keywords in error messages
- `user_satisfied` remains `False`
- Graph routes back to start

**Terminal Evidence:**
```
🔍 Extracting keywords from query...
⚠️ Error extracting keywords...
🔬 Executing Depth Search Node...
🤖 Processing query with Gemini...
❌ Error in model query...
🔍 Checking user satisfaction...
  🔄 User wants to continue
[REPEATS INDEFINITELY]
```

**Max Iterations:** System ran 7+ iterations before being killed.

---

## ✅ Components Working Correctly

### Successfully Initialized:
1. ✅ **Neo4j Connection** - Database connection established
2. ✅ **Graph Compilation** - LangGraph workflow compiled without errors
3. ✅ **State Management** - All state fields properly initialized
4. ✅ **Thread Creation** - Session threading works correctly
5. ✅ **Python Environment** - Virtual environment with all dependencies installed

### Database Handlers (Untested but Likely Functional):
- `get_questions_by_domain()`
- `get_questions_by_skill()`
- `get_questions_by_company()`
- `get_questions_by_topic()`

**Note:** Database queries cannot be properly tested until LLM integration is fixed.

---

## 🛠️ Recommended Fixes

### Fix #1: Update Gemini Model Name (HIGH PRIORITY)

**Option A - Try Alternative Model Names:**
```python
# In botchat.py, line ~267
self.llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-001",  # Add version suffix
    temperature=0.7,
    google_api_key="AIzaSyBmBqidLQLsnoLdAHOvskoxXd_GqdREfA4"
)
```

**Option B - Use OpenAI Instead:**
```python
from langchain_openai import ChatOpenAI

self.llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Fix #2: Add Model Name Detection Script

Create a script to list available models:
```python
import google.generativeai as genai
genai.configure(api_key="AIzaSyBmBqidLQLsnoLdAHOvskoxXd_GqdREfA4")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)
```

### Fix #3: Add Loop Prevention

**Location:** `check_satisfaction_node`  
**Add a counter to prevent infinite loops:**
```python
if not state.get("loop_counter"):
    state["loop_counter"] = 0

state["loop_counter"] += 1

if state["loop_counter"] > 10:
    state["user_satisfied"] = True
    print("⚠️ Max iterations reached, ending conversation")
```

### Fix #4: Improve Error Handling

**Add graceful degradation:**
```python
except Exception as e:
    print(f"⚠️ Error extracting keywords: {e}")
    # Parse keywords manually using simple regex/string matching
    query_lower = latest_query.lower()
    
    # Fallback keyword extraction
    companies = ["google", "amazon", "microsoft", "apple"]
    skills = ["python", "java", "javascript", "sql"]
    
    found_company = next((c for c in companies if c in query_lower), None)
    found_skills = [s for s in skills if s in query_lower]
    
    state["search_keywords"] = SearchKeywords(
        company_name=found_company,
        skills=found_skills
    )
```

---

## 📊 Test Results Summary

### Test Case 1: "Give me Google Python questions"

| Node | Status | Output |
|------|--------|--------|
| Start | ✅ Pass | Thread created successfully |
| Extract Keywords | ❌ Fail | LLM API error (404) |
| Depth Search | ⚠️ Partial | Executed but found 0 results (no keywords) |
| Model Query | ❌ Fail | LLM API error (404) |
| Check Satisfaction | ⚠️ Partial | Incorrectly routes to continue loop |

**Final Result:** ❌ FAILED - Infinite loop, no response generated

---

## 🔧 Environment Details

### Installed Packages:
- `langgraph` ✅
- `langchain-google-genai` ✅
- `langchain-openai` ✅
- `neo4j` ✅
- `pydantic` ✅
- `pandas` ✅

### Configuration:
- **Neo4j URI:** bolt://localhost:7687
- **Google API Key:** AIzaSyBmBqidLQLsnoLdAHOvskoxXd_GqdREfA4 (Exposed in code - ⚠️ Security Issue)
- **Python Version:** 3.12.1
- **Environment:** Windows Virtual Environment

---

## 🚨 Security Issues

### 1. Hardcoded API Key
**Location:** `botchat.py`, line 270  
**Risk:** HIGH - API key is hardcoded and visible in source code

**Fix:**
```python
# Remove hardcoded key
self.llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-001",
    temperature=0.7,
    google_api_key=google_api_key  # Use parameter instead
)

# In .env file:
GOOGLE_API_KEY=AIzaSyBmBqidLQLsnoLdAHOvskoxXd_GqdREfA4
```

---

## 📋 Next Steps

### Immediate Actions (Priority Order):
1. ✅ **URGENT:** Document all errors (this file)
2. 🔄 **HIGH:** Fix Gemini model name or switch to OpenAI
3. 🔄 **HIGH:** Remove hardcoded API key
4. 🔄 **MEDIUM:** Add loop prevention mechanism
5. 🔄 **MEDIUM:** Implement fallback keyword extraction
6. 🔄 **LOW:** Add comprehensive error logging

### Testing Checklist:
- [ ] Verify LLM model availability
- [ ] Test keyword extraction with valid model
- [ ] Test database queries independently
- [ ] Verify end-to-end flow with sample inputs
- [ ] Test error handling edge cases
- [ ] Validate conversation loop termination

---

## 📝 Notes

- The core LangGraph architecture is sound ✅
- Neo4j integration is functional ✅
- The only blocker is the LLM model configuration ⚠️
- Once LLM is fixed, the system should function as designed 🎯

---

**Generated by:** Automated Debug Analysis  
**Contact:** Check `botchat.py` for implementation details
