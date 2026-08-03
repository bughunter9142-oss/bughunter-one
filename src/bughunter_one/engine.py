from __future__ import annotations

import inspect
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests


class ReconnaissanceEngine:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def scan_target(self, target: str) -> Dict[str, Any]:
        validated = self._validate_target(target)
        parsed = urlparse(validated)
        host = parsed.netloc or parsed.path
        if host.startswith("http://") or host.startswith("https://"):
            host = urlparse(host).netloc or host
        payload = {
            "target": {"host": host, "url": validated},
            "scan_statistics": {
                "hosts_discovered": 1,
                "ports_open": self._infer_ports(parsed),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            },
            "technologies": [],
            "dns": {"records": {}},
            "subdomains": [],
            "live_hosts": [host],
            "open_ports": [],
            "robots": {"url": urljoin(validated.rstrip("/") + "/", "robots.txt"), "entries": []},
            "sitemap": {"url": urljoin(validated.rstrip("/") + "/", "sitemap.xml"), "entries": []},
            "javascript": {"files": []},
            "historical_urls": [],
            "api_discovery": [],
            "auth_surface": [],
            "parameters": [],
            "headers": {},
            "cookies": [],
            "ssl": {},
            "interesting_resources": [],
            "metadata": {"scanner": "bughunter-one", "target": validated},
        }

        dns_records = self._call_dns_resolver(host)
        payload["dns"]["records"] = dns_records

        robots = self._fetch_text_resource(payload["robots"]["url"])
        if robots:
            payload["robots"]["entries"] = self._parse_robots_entries(robots)
            payload["interesting_resources"].append({"url": payload["robots"]["url"], "type": "robots"})

        sitemap = self._fetch_text_resource(payload["sitemap"]["url"])
        if sitemap:
            payload["sitemap"]["entries"] = self._parse_sitemap_entries(sitemap)
            payload["interesting_resources"].append({"url": payload["sitemap"]["url"], "type": "sitemap"})

        response = self._fetch_url(validated)
        payload["headers"] = self._normalize_headers(response.get("headers", {}))
        payload["cookies"] = response.get("cookies", [])
        payload["javascript"]["files"] = self._extract_js_files(response.get("body", ""))
        payload["technologies"] = self._fingerprint_technologies(payload["headers"], response.get("body", ""))
        payload["ssl"] = self._infer_ssl_details(parsed, response)

        if payload["headers"].get("server"):
            payload["technologies"].append(payload["headers"]["server"])

        return payload

    def _validate_target(self, target: str) -> str:
        if not target or not isinstance(target, str):
            raise ValueError("Target must be a non-empty string")

        if not re.match(r"^https?://", target):
            target = f"https://{target}"

        parsed = urlparse(target)
        if not parsed.netloc:
            raise ValueError("Target must include a host")
        return target.rstrip("/") or target

    def _infer_ports(self, parsed) -> List[int]:
        return [80, 443] if parsed.scheme in {"http", "https"} else []

    def _call_dns_resolver(self, host: str) -> Dict[str, List[str]]:
        resolver = getattr(type(self), "_resolve_dns")
        parameters = list(inspect.signature(resolver).parameters)
        if len(parameters) == 2:
            return resolver(self, host)
        return resolver(host)

    def _resolve_dns(self, host: str) -> Dict[str, List[str]]:
        try:
            import dns.resolver
        except ImportError:
            return {"A": []}

        records: Dict[str, List[str]] = {}
        for record_type in ["A", "AAAA", "CNAME"]:
            try:
                answers = dns.resolver.resolve(host, record_type)
            except Exception:
                continue
            records[record_type] = [str(item) for item in answers]
        return records or {"A": []}

    def _fetch_text_resource(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return None

    def _fetch_url(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
        except requests.RequestException as exc:
            return {"status_code": 0, "headers": {}, "body": "", "final_url": url, "cookies": [], "error": str(exc)}

        headers = dict(response.headers)
        cookies = []
        for cookie in response.cookies:
            cookies.append({"name": cookie.name, "value": cookie.value})

        if "Set-Cookie" in headers and isinstance(headers["Set-Cookie"], str):
            headers["set-cookie"] = headers["Set-Cookie"]

        return {
            "status_code": response.status_code,
            "headers": headers,
            "body": response.text,
            "final_url": response.url,
            "cookies": cookies,
        }

    def _normalize_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        return {str(k).lower(): str(v) for k, v in headers.items()}

    def _parse_robots_entries(self, body: str) -> List[str]:
        entries = []
        for line in body.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)
        return entries

    def _parse_sitemap_entries(self, body: str) -> List[str]:
        matches = re.findall(r"<loc>(.*?)</loc>", body, flags=re.IGNORECASE | re.DOTALL)
        return [m.strip() for m in matches if m.strip()]

    def _extract_js_files(self, body: str) -> List[str]:
        matches = re.findall(r"(?:src|href)=[\"']([^\"']+\.js[^\"']*)[\"']", body, flags=re.IGNORECASE)
        return matches

    def _fingerprint_technologies(self, headers: Dict[str, Any], body: str) -> List[str]:
        technologies = []
        if "server" in headers and headers.get("server"):
            technologies.append(headers["server"])
        if "x-powered-by" in headers and headers.get("x-powered-by"):
            technologies.append(headers["x-powered-by"])
        if re.search(r"<script[^>]+src=", body, re.IGNORECASE):
            technologies.append("javascript")
        if re.search(r"<meta[^>]+name=[\"']generator[\"']", body, re.IGNORECASE):
            technologies.append("generator-meta")
        return sorted(set(technologies))

    def _infer_ssl_details(self, parsed, response: Dict[str, Any]) -> Dict[str, Any]:
        if parsed.scheme == "https":
            return {"tls_version": "unknown", "status": "https" if response.get("status_code") else "unreachable"}
        return {"tls_version": "n/a", "status": "http"}
