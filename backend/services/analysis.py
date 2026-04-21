import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def search_web(query: str) -> str:
    """Uses DuckDuckGo to silently search the web and return the top 2 snippets."""
    try:
        results = DDGS().text(query, max_results=2)
        if not results:
            return ""
        return "\n".join([f"Source ({r['href']}): {r['body']}" for r in results])
    except Exception as e:
        print(f"Search failed for query '{query}': {e}")
        return ""

def analyze_transcript(segments: list, websocket=None) -> list:
    """
    RAG Pipeline:
    1. Fast extraction of main topics.
    2. DuckDuckGo search for live context.
    3. Final JSON fact-check generation.
    """
    transcript_text = "\n".join([f"[{s['start']:.2f}s - {s['end']:.2f}s]: {s['text']}" for s in segments])
    
    # Optional: Send WS update
    if websocket:
        import asyncio
        asyncio.run(websocket.send_text(json.dumps({"status": "Searching the live web for context..."})))

    # Step 1: Quick Search Query Generation
    # For a short video, we just ask the LLM to generate 1-2 broad search queries to verify the claims.
    query_prompt = f"Based on this transcript, what is the single most important factual claim to verify on Google? Reply with ONLY the search query text, nothing else.\n\nTranscript:\n{transcript_text}"
    try:
        query_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": query_prompt}],
            temperature=0.1,
            max_tokens=50
        )
        search_query = query_response.choices[0].message.content.strip().replace('"', '')
        
        # Step 2: Perform the live search
        live_context = search_web(search_query)
    except Exception:
        live_context = "No live web context available."

    if websocket:
        import asyncio
        asyncio.run(websocket.send_text(json.dumps({"status": "Generating final Community Notes..."})))

    # Step 3: Final JSON Generation
    system_prompt = f"""
    You are an expert, unbiased factual analysis engine. 
    You act as a real-time "Community Notes" fact-checker.
    
    You have access to the video transcript and Live Web Search Context.
    Live Web Context from DuckDuckGo:
    {live_context}
    
    Analyze the transcript for clear, objective factual claims.
    
    For each factual claim:
    1. Identify the exact timestamp (in seconds, as a float).
    2. Extract the claim clearly.
    3. Determine the truthfulness ("True", "False", or "Context") using the live web context.
    4. Provide a valid source URL (use the URL from the live web context if applicable).
    5. Provide a 1-2 sentence succinct explanation.
    
    You MUST respond in valid JSON format matching this exact schema:
    {{
      "fact_checks": [
        {{
          "timestamp": 12.5,
          "claim": "String",
          "rating": "True" | "False" | "Context",
          "source_url": "https://...",
          "explanation": "String"
        }}
      ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the transcript:\n\n{transcript_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result_str = response.choices[0].message.content
        result_data = json.loads(result_str)
        return result_data.get("fact_checks", [])

    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")
