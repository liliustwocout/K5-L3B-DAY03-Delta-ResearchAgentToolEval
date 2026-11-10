from __future__ import annotations

from collections import Counter
from graphlib import CycleError, TopologicalSorter
from typing import Any

from tools._shared import domain, err, telegram_markdown_text, telegram_markdown_url


MAX_NODES = 12


def trace_source_chain(articles: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        if not isinstance(articles, list) or not 1 <= len(articles) <= MAX_NODES:
            raise ValueError(f"articles must contain 1 to {MAX_NODES} documents")

        titles: dict[str, str] = {}
        citations: dict[str, tuple[str, ...]] = {}
        for index, article in enumerate(articles):
            if not isinstance(article, dict):
                raise ValueError(f"articles[{index}] must be an object")
            url = telegram_markdown_url(article.get("url"), f"articles[{index}].url")
            title = article.get("title", "")
            if not isinstance(title, str):
                raise ValueError(f"articles[{index}].title must be a string")
            cited = article.get("cites")
            if not isinstance(cited, list) or len(cited) > MAX_NODES:
                raise ValueError(f"articles[{index}].cites must be an array of at most {MAX_NODES} URLs")

            titles[url] = titles.get(url) or title.strip()
            links = tuple(
                telegram_markdown_url(target, f"articles[{index}].cites") for target in cited
            )
            citations[url] = tuple(dict.fromkeys((*citations.get(url, ()), *links)))

        titles = {url: title or domain(url) for url, title in titles.items()}
        cited_urls = {target for targets in citations.values() for target in targets}
        missing_urls = sorted(cited_urls.difference(titles))
        if len(titles) + len(missing_urls) > MAX_NODES:
            raise ValueError(f"At most {MAX_NODES} distinct document URLs fit in one source map")

        # Topological order visits cited documents before the articles that cite them.
        reachable_roots: dict[str, set[str]] = {}
        for url in TopologicalSorter(citations).static_order():
            if url not in titles:
                reachable_roots[url] = set()
            elif not citations[url]:
                reachable_roots[url] = {url}
            else:
                reachable_roots[url] = set().union(*(reachable_roots[target] for target in citations[url]))

        entries = [url for url, targets in citations.items() if targets and url not in cited_urls]
        counts = Counter(root for url in entries for root in reachable_roots[url])
        roots = [
            {"url": url, "title": titles[url], "article_count": counts[url]}
            for url in sorted(counts, key=lambda url: (-counts[url], url))
        ]
        nodes = [
            {"url": url, "title": title, "kind": "root" if url in counts else "article"}
            for url, title in titles.items()
        ] + [
            {"url": url, "title": domain(url), "kind": "unresolved"}
            for url in missing_urls
        ]
        edges = [
            {"from_url": url, "to_url": target}
            for url, targets in citations.items() for target in targets
        ]

        lines = [
            "🔗 *Truy dấu nguồn tin*",
            f"{len(entries)} bài đầu chuỗi · {len(roots)} nguồn cuối chuỗi trong dữ liệu đã cho.",
        ]
        for index, root in enumerate(roots, 1):
            title = telegram_markdown_text(root["title"])
            lines.append(f"• [Nguồn {index}]({root['url']}) · {title} · {root['article_count']} bài dẫn tới")
        if missing_urls:
            lines.append(f"🧩 {len(missing_urls)} nguồn được dẫn chưa có dữ liệu để lần tiếp.")
            lines.extend(f"• [Nguồn chưa rõ {index}]({url})" for index, url in enumerate(missing_urls, 1))
        if not edges:
            lines.append("Chưa có liên kết trích dẫn để đối chiếu.")
        markdown = "\n".join(lines)
        if len(markdown.encode("utf-16-le")) // 2 > 4096:
            raise ValueError("Source summary is too long for one Telegram message")
        return {
            "tool": "trace_source_chain",
            "entry_count": len(entries),
            "roots": roots,
            "unresolved_urls": missing_urls,
            "nodes": nodes,
            "edges": edges,
            "markdown": markdown,
        }
    except CycleError:
        return err("trace_source_chain", ValueError("The citations contain a cycle"))
    except ValueError as exc:
        return err("trace_source_chain", exc)
