"""Lightweight browser automation utilities.

This module provides a very small HTML automation helper used only for the
unit tests in this repository.  The original implementation relied on the
`playwright` package, which is not available in the execution environment used
for the tests.  To keep the examples working we provide a tiny HTTP based
engine that supports a subset of the Playwright API used in the tests:

* query elements by simple CSS selectors (tag names or ``#id``)
* extract text content
* fill form inputs
* click links or submit forms and follow the resulting navigation
* conditional branching based on the presence of an element

The goal is not to be feature complete but to offer enough behaviour to drive
multi‑page workflows in a predictable way without external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlencode, urljoin
import time

import requests


# ---------------------------------------------------------------------------
# Basic DOM model


@dataclass
class Node:
    tag: str
    attrs: Dict[str, str]
    parent: Optional["Node"] = None
    children: List["Node"] = field(default_factory=list)
    text: str = ""

    def get_attribute(self, name: str) -> Optional[str]:
        return self.attrs.get(name)

    def inner_text(self) -> str:
        return self.text + "".join(child.inner_text() for child in self.children)

    def iter(self) -> Iterable["Node"]:
        yield self
        for child in self.children:
            yield from child.iter()


class _DOMParser(HTMLParser):
    """Very small HTML parser building a tree of :class:`Node` objects."""

    def __init__(self) -> None:
        super().__init__()
        self.root = Node("document", {})
        self.stack = [self.root]
        self.id_index: Dict[str, Node] = {}

    # HTMLParser interface -------------------------------------------------
    def handle_starttag(self, tag: str, attrs: List[tuple[str, str]]) -> None:
        node = Node(tag, dict(attrs), self.stack[-1])
        self.stack[-1].children.append(node)
        self.stack.append(node)
        node_id = node.attrs.get("id")
        if node_id:
            self.id_index[node_id] = node

    def handle_endtag(self, tag: str) -> None:  # noqa: D401 - HTMLParser API
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        if data and self.stack:
            self.stack[-1].text += data

    # Utility --------------------------------------------------------------
    def parse(self, html: str) -> Node:
        self.feed(html)
        return self.root


@dataclass
class Page:
    url: str
    content: str
    root: Node
    id_index: Dict[str, Node]

    def query_selector_all(self, selector: str) -> List[Node]:
        if selector.startswith("#"):
            node = self.id_index.get(selector[1:])
            return [node] if node else []
        return [n for n in self.root.iter() if n.tag == selector]

    def query_selector(self, selector: str) -> Optional[Node]:
        nodes = self.query_selector_all(selector)
        return nodes[0] if nodes else None


# ---------------------------------------------------------------------------
# Browser automation engine


class BrowserAutomation:
    """Execute scripted interactions against a very small HTML engine."""

    def __init__(self, logger: Any | None = None) -> None:
        self.logger = logger

    # -- helpers ----------------------------------------------------------
    def _load(self, url: str) -> Page:
        resp = requests.get(url)
        resp.raise_for_status()
        parser = _DOMParser()
        root = parser.parse(resp.text)
        return Page(url=url, content=resp.text, root=root, id_index=parser.id_index)

    def _find_form(self, node: Node) -> Optional[Node]:
        while node:
            if node.tag == "form":
                return node
            node = node.parent  # type: ignore[assignment]
        return None

    def _inputs_in_form(self, form: Node) -> Iterable[Node]:
        return [n for n in form.iter() if n.tag == "input"]

    # -- public API -------------------------------------------------------
    def run_script(self, url: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a list of ``actions`` starting at ``url``.

        The supported action types are ``click``, ``type``, ``wait``, ``query``,
        ``extract``, ``navigate`` and ``conditional``.  Results from ``query`` or
        ``extract`` steps are stored under keys in the returned ``data``
        dictionary and can be referenced by later actions using the ``from`` key.
        """

        results: Dict[str, Any] = {}
        page = self._load(url)

        def resolve(ref: Optional[str], index: int = 0) -> Optional[Node]:
            if not ref:
                return None
            elems = results.get(ref, [])
            return elems[index] if len(elems) > index else None

        def exec_actions(sequence: List[Dict[str, Any]]) -> None:
            nonlocal page
            for act in sequence:
                a_type = act.get("type")
                if a_type == "click":
                    if "selector" in act:
                        elems = page.query_selector_all(act["selector"])
                        el = elems[act.get("index", 0)] if elems else None
                    else:
                        el = resolve(act.get("from"), act.get("index", 0))
                    if not el:
                        continue
                    if el.tag == "a":
                        href = el.get_attribute("href")
                        if href:
                            page = self._load(urljoin(page.url, href))
                    elif el.tag in {"button", "input"}:
                        form = self._find_form(el)
                        if form:
                            action_url = form.get_attribute("action") or page.url
                            action_url = urljoin(page.url, action_url)
                            data = {}
                            for inp in self._inputs_in_form(form):
                                name = inp.get_attribute("name")
                                if name:
                                    data[name] = inp.get_attribute("value") or ""
                            query = f"?{urlencode(data)}" if data else ""
                            page = self._load(action_url + query)
                elif a_type == "type":
                    value = act.get("value", "")
                    if "selector" in act:
                        elems = page.query_selector_all(act["selector"])
                        el = elems[0] if elems else None
                    else:
                        el = resolve(act.get("from"), act.get("index", 0))
                    if el:
                        el.attrs["value"] = value
                elif a_type == "wait":
                    time.sleep(act.get("timeout", 1000) / 1000.0)
                elif a_type == "query":
                    elems = page.query_selector_all(act.get("selector", ""))
                    results[act.get("store", "results")] = elems
                elif a_type == "extract":
                    if "selector" in act:
                        elems = page.query_selector_all(act["selector"])
                    else:
                        elems = results.get(act.get("from"), [])
                    texts = [e.inner_text() for e in elems]
                    results[act.get("store", "text")] = texts
                elif a_type == "navigate":
                    if "url" in act:
                        page = self._load(urljoin(page.url, act["url"]))
                    elif "selector" in act:
                        elems = page.query_selector_all(act["selector"])
                        if elems:
                            href = elems[act.get("index", 0)].get_attribute("href")
                            if href:
                                page = self._load(urljoin(page.url, href))
                    else:
                        el = resolve(act.get("from"), act.get("index", 0))
                        if el:
                            href = el.get_attribute("href")
                            if href:
                                page = self._load(urljoin(page.url, href))
                elif a_type == "conditional":
                    selector = act.get("selector")
                    branch = act.get("then", []) if (selector and page.query_selector(selector)) else act.get("else", [])
                    exec_actions(branch)

        exec_actions(actions)
        return {"content": page.content, "data": results}


# End of file

