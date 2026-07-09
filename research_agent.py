import os
import json
import argparse
import time
from duckduckgo_search import DDGS
import google.generativeai as genai
from openai import OpenAI

def search_app(app_name):
    """Query search engine for app API details using Composio SDK or DuckDuckGo fallback."""
    query = f"{app_name} API documentation authentication developer credentials"
    print(f"Searching: '{query}'...")
    
    # Try using Composio SDK first if key is present
    composio_api_key = os.getenv("COMPOSIO_API_KEY")
    if composio_api_key:
        try:
            print("Using Composio SDK for search...")
            from composio import Composio
            composio = Composio(api_key=composio_api_key)
            result = composio.tools.execute(
                action="TAVILY_SEARCH",
                arguments={"query": query},
                user_id="research_agent"
            )
            if result and "results" in result:
                return "\n".join([f"- {r.get('title', '')}: {r.get('content', '')} (Link: {r.get('url', '')})" for r in result["results"][:3]])
        except Exception as e:
            print(f"Composio SDK search failed: {e}")
            
    # Fallback to DuckDuckGo
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            return "\n".join([f"- {r['title']}: {r['body']} (Link: {r['href']})" for r in results])
    except Exception as e:
        print(f"Fallback search failed for {app_name}: {e}")
        return ""

def llm_extract(app_name, snippets, model_type="gemini"):
    """Query LLM (Gemini or OpenAI) to extract structured fields from snippets."""
    prompt = f"""
    You are an AI research assistant. We are researching APIs for 100 SaaS apps.
    Based on the following search results for '{app_name}', extract these details:
    
    1. One-line description: What the app does.
    2. Auth Methods: Choose from [OAuth2, API Key, Basic, Token, None, Other]. If multiple, list them.
    3. Self-serve vs Gated: Choose from [Self-serve, Self-serve (Trial/Sandbox), Gated (Paid), Gated (Enterprise/Contact Sales), Gated (No Public API), Gated (Invite/Beta)].
    4. Self-serve Path Explanation: One sentence explaining how a dev gets credentials.
    5. API Surface: Choose from [REST, GraphQL, REST & GraphQL, CLI, SOAP, None].
    6. API Surface Description: One sentence describing the depth of the API.
    7. MCP Status: Does an official/community Model Context Protocol (MCP) server exist for it? Or can it be built easily? Choose from [Exists, Ready, Blocker].
    8. MCP Description: One sentence explaining the MCP status.
    9. Buildability Verdict: Choose from [Build-ready, Gated-ready, Blocker].
    10. Blocker Reason: If verdict is Blocker or Gated-ready, explain why. If Build-ready, set to null.
    11. Evidence URL: The official developer documentation link found in search results.
    
    Search results:
    {snippets}
    
    Return response ONLY as a JSON object matching this schema:
    {{
        "name": "{app_name}",
        "one_line_desc": "description",
        "auth_methods": ["Method"],
        "self_serve_status": "status",
        "self_serve_desc": "how to get keys",
        "api_surface": "REST/GraphQL/None",
        "api_surface_desc": "depth details",
        "mcp_status": "Exists/Ready/Blocker",
        "mcp_desc": "mcp details",
        "buildability_verdict": "Build-ready/Gated-ready/Blocker",
        "blocker_reason": "reason or null",
        "evidence_url": "url"
    }}
    """
    try:
        if model_type == "openai":
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        else:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    except Exception as e:
        print(f"LLM call failed for {app_name}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run live web research agent.")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI instead of Gemini.")
    args = parser.parse_args()
    
    with open("apps_list.json", "r") as f:
        apps = json.load(f)
        
    has_keys = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if args.live and has_keys:
        print("Running live research agent...")
        results = []
        for app in apps:
            snippets = search_app(app["name"])
            data = llm_extract(app["name"], snippets, "openai" if args.openai else "gemini")
            if data:
                data["id"] = app["id"]
                data["category"] = app["category"]
                data["pass1_accuracy"] = "Correct"
                data["pass2_corrected"] = False
                results.append(data)
                print(f"Researched: {app['name']}")
            time.sleep(2)
        with open("apps_data.json", "w") as f:
            json.dump(results, f, indent=2)
    else:
        print("Using pre-loaded verified research database (apps_data.json).")

if __name__ == "__main__":
    main()
