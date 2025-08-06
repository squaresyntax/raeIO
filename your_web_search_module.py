"""Utility for performing web search, summarising the results and
extracting code snippets.

This module integrates with the Bing Web Search API.  An API key must be
available in the environment variable ``BING_SEARCH_KEY``.  If the key is
missing or a network error occurs the function will raise an exception so
callers can decide how to handle the failure.

For summarisation a very small rule‑based approach is used.  If an
``OPENAI_API_KEY`` environment variable is present, the function will try to
use the OpenAI chat completion end‑point; otherwise it falls back to the
rule‑based summariser.

The main entry point ``web_search_and_summarize`` returns:

``summary`` – a short text summary of the combined search snippets.
``sources`` – list of URLs that were returned by the search.
``code_suggestions`` – list of dictionaries each containing a snippet of
code that was detected on a page and the corresponding URL.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup


BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"


def _bing_search(query: str, num_results: int) -> List[Dict[str, str]]:
    """Query the Bing Web Search API and return basic result metadata.

    Parameters
    ----------
    query: str
        Search query.
    num_results: int
        Number of search results to return.
    """

    api_key = os.environ.get("BING_SEARCH_KEY")
    if not api_key:
        raise RuntimeError("BING_SEARCH_KEY environment variable is required")

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": num_results, "textDecorations": True, "textFormat": "HTML"}

    resp = requests.get(BING_ENDPOINT, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    pages = data.get("webPages", {}).get("value", [])
    return [
        {"title": p.get("name", ""), "url": p.get("url", ""), "snippet": p.get("snippet", "")}
        for p in pages
    ]


def _summarize(text: str, max_sentences: int = 2) -> str:
    """Summarise ``text`` with an optional LLM fallback."""

    text = text.strip()
    if not text:
        return ""

    # Try OpenAI if a key is available; otherwise fall back to simple rules.
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai

            openai.api_key = api_key
            chat_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Provide a short summary of the following text."},
                    {"role": "user", "content": text},
                ],
                max_tokens=120,
            )
            return chat_resp.choices[0].message["content"].strip()
        except Exception:
            # Silently fall back to rule based summarisation below
            pass

    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:max_sentences]).strip()


def _extract_code_from_url(url: str) -> str:
    """Retrieve ``url`` and attempt to extract the first code block."""

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Look for <pre><code> or standalone <code> blocks
    code_block = soup.find("pre")
    if code_block and code_block.find("code"):
        code_block = code_block.find("code")
    if not code_block:
        code_block = soup.find("code")

    if not code_block:
        return ""

    snippet = code_block.get_text("\n").strip()
    return snippet


def web_search_and_summarize(query: str, num_results: int = 5) -> Tuple[str, List[str], List[Dict[str, str]]]:
    """Search the web, summarise results and collect code snippets.

    Parameters
    ----------
    query: str
        Query to search for.
    num_results: int, optional
        Number of results to retrieve, default 5.
    """

    results = _bing_search(query, num_results)
    sources = [r["url"] for r in results if r.get("url")]

    # Combine snippets for summarisation
    combined_snippet = " ".join(r.get("snippet", "") for r in results)
    summary = _summarize(combined_snippet)

    code_suggestions: List[Dict[str, str]] = []
    for r in results:
        url = r.get("url")
        if not url:
            continue
        snippet = _extract_code_from_url(url)
        if snippet:
            code_suggestions.append({"url": url, "code": snippet})

    return summary, sources, code_suggestions


__all__ = ["web_search_and_summarize"]

