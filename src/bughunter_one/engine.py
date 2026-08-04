from __future__ import annotations

import inspect
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests


class ReconnaissanceEngine:
    def __init__(
        self,
        timeout: int = 5,
        active_checks: bool = False,
        directory_wordlist: Optional[List[str]] = None,
        directory_rate_limit: float = 0.2,
        user_agent: str = "BugHunter-One/0.2.0",
        retries: int = 1,
        concurrency: int = 2,
        enabled_modules: Optional[Dict[str, bool]] = None,
    ):
        self.timeout = timeout
        self.active_checks = active_checks
        self.directory_wordlist = directory_wordlist
        self.directory_rate_limit = directory_rate_limit
        self.user_agent = user_agent
        self.retries = max(0, retries)
        self.concurrency = max(1, concurrency)
        self.enabled_modules = enabled_modules or {}
        self.logger = logging.getLogger("bughunter_one.scanner")

    def scan_target(self, target: str) -> Dict[str, Any]:
        self.logger.info("scan_started target=%s", target)
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
            "javascript": {"files": [], "metadata": {"source": "response-body"}},
            "historical_urls": [],
            "api_discovery": [],
            "auth_surface": [],
            "parameters": [],
            "headers": {},
            "cookies": [],
            "ssl": {},
            "interesting_resources": [],
            "metadata": {"scanner": "bughunter-one", "target": validated},
            "public_ports": [],
            "public_directories": [],
        }

        dns_records = self._call_dns_resolver(host) if self._module_enabled("dns") else {"A": []}
        payload["dns"]["records"] = dns_records

        robots, sitemap = self._fetch_standard_resources(payload)
        if robots:
            payload["robots"]["entries"] = self._parse_robots_entries(robots)
            payload["interesting_resources"].append({"url": payload["robots"]["url"], "type": "robots"})

        if sitemap:
            payload["sitemap"]["entries"] = self._parse_sitemap_entries(sitemap)
            payload["interesting_resources"].append({"url": payload["sitemap"]["url"], "type": "sitemap"})

        response = self._fetch_url(validated)
        payload["headers"] = self._normalize_headers(response.get("headers", {})) if self._module_enabled("headers") else {}
        payload["cookies"] = response.get("cookies", []) if self._module_enabled("cookies") else []
        payload["javascript"]["files"] = self._extract_js_files(response.get("body", "")) if self._module_enabled("javascript") else []
        payload["javascript"]["metadata"]["assets_count"] = len(payload["javascript"]["files"])
        payload["technologies"] = self._fingerprint_technologies(payload["headers"], response.get("body", "")) if self._module_enabled("technologies") else []
        payload["ssl"] = self._infer_ssl_details(parsed, response) if self._module_enabled("ssl") else {}

        if payload["headers"].get("server"):
            payload["technologies"].append(payload["headers"]["server"])

        payload["subdomains"] = self._discover_subdomains(host, response.get("body", "")) if self._module_enabled("subdomains") else []
        payload["live_hosts"] = self._identify_live_hosts(host, payload["subdomains"], response, parsed, active=self.active_checks) if self._module_enabled("live_hosts") else []
        payload["public_ports"] = self._identify_public_ports_and_services(host, response, parsed, active=self.active_checks) if self._module_enabled("public_ports") else []
        payload["historical_urls"] = self._collect_historical_urls(host, response.get("body", "")) if self._module_enabled("historical_urls") else []
        payload["public_directories"] = self._discover_public_directories(
            validated,
            wordlist=(self.directory_wordlist if self.directory_wordlist is not None else (self._default_directory_wordlist() if self.active_checks else [])),
            rate_limit=self.directory_rate_limit,
            timeout=self.timeout,
        ) if self._module_enabled("public_directories") else []
        payload["api_discovery"] = self._discover_api_endpoints(response.get("body", ""), payload["robots"]["entries"], payload["sitemap"]["entries"]) if self._module_enabled("api_discovery") else []
        payload["auth_surface"] = self._discover_auth_surface(
            response.get("body", ""),
            [validated, payload["robots"]["url"], payload["sitemap"]["url"]] + payload["historical_urls"],
        ) if self._module_enabled("auth_surface") else []

        self.logger.info("scan_completed target=%s", host)
        return payload

    def _module_enabled(self, name: str) -> bool:
        return self.enabled_modules.get(name, True)

    def _fetch_standard_resources(self, payload: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """Fetch independent robots and sitemap resources concurrently when enabled."""
        jobs = {
            "robots": payload["robots"]["url"] if self._module_enabled("robots") else None,
            "sitemap": payload["sitemap"]["url"] if self._module_enabled("sitemap") else None,
        }
        with ThreadPoolExecutor(max_workers=min(self.concurrency, 2)) as executor:
            futures = {name: executor.submit(self._fetch_text_resource, url) for name, url in jobs.items() if url}
            results = {name: future.result() for name, future in futures.items()}
        return results.get("robots"), results.get("sitemap")

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
        return self._request_text(url)

    def _request_text(self, url: str) -> Optional[str]:
        for attempt in range(self.retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout, allow_redirects=True, headers={"User-Agent": self.user_agent})
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                self.logger.debug("request_failed url=%s attempt=%s error=%s", url, attempt + 1, exc)
        return None

    def _fetch_url(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": self.user_agent})
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

    def _discover_subdomains(self, host: str, body: str) -> List[str]:
        normalized_host = host.lower().strip("/")
        base_domain = self._get_base_domain(normalized_host)
        candidates = set()

        for match in re.findall(r"https?://([^/\s'\"<>]+)", body, flags=re.IGNORECASE):
            cleaned = match.split("//", 1)[-1].split("/", 1)[0]
            cleaned = cleaned.split(":", 1)[0]
            cleaned = cleaned.lower().strip(".")
            if not cleaned or cleaned == normalized_host:
                continue
            if cleaned.endswith(base_domain) or cleaned == normalized_host:
                candidates.add(cleaned)

        return sorted(candidates)

    def _get_base_domain(self, host: str) -> str:
        labels = [part for part in host.split(".") if part]
        if len(labels) <= 2:
            return host
        return ".".join(labels[-2:])

    def _identify_live_hosts(self, host: str, subdomains: List[str], response: Dict[str, Any], parsed, active: bool = False) -> List[str]:
        live_hosts = [host]
        if not active:
            return live_hosts

        for candidate in subdomains[:5]:
            probe_url = f"https://{candidate}"
            try:
                probe_response = requests.get(probe_url, timeout=self.timeout, allow_redirects=True)
                if probe_response.ok:
                    live_hosts.append(candidate)
            except requests.RequestException:
                continue

        return sorted(set(live_hosts))

    def _identify_public_ports_and_services(self, host: str, response: Dict[str, Any], parsed, active: bool = False) -> List[Dict[str, Any]]:
        services: List[Dict[str, Any]] = []
        if parsed.scheme in {"http", "https"}:
            services.append({"port": 80, "service": "http", "status": "passive"})
        if parsed.scheme == "https" or response.get("status_code"):
            services.append({"port": 443, "service": "https", "status": "passive"})
        if active:
            for entry in services:
                entry["status"] = "open"
        return services

    def _collect_historical_urls(self, host: str, body: str, timeout: int = 5) -> List[str]:
        urls = []
        for match in re.findall(r"https?://[^\s\"'<>]+", body, flags=re.IGNORECASE):
            if host in match:
                urls.append(match)
        if urls:
            return sorted(set(urls))[:25]

        archive_url = f"https://web.archive.org/web/timemap/json/https://{host}/"
        try:
            response = requests.get(archive_url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            for line in response.text.splitlines():
                if "http" in line and host in line:
                    urls.append(line.strip())
                    if len(urls) >= 25:
                        break
        except requests.RequestException:
            return []
        return sorted(set(urls))[:25]

    def _discover_public_directories(self, base_url: str, wordlist: Optional[List[str]] = None, rate_limit: float = 0.2, timeout: int = 5) -> List[str]:
        if not wordlist:
            return []

        results = []
        for path in wordlist:
            candidate_url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
            try:
                response = requests.get(candidate_url, timeout=timeout, allow_redirects=False)
                if response.status_code in {200, 301, 302, 403}:
                    results.append(path)
            except requests.RequestException:
                continue
            if rate_limit > 0:
                time.sleep(rate_limit)
        return results

    def _default_directory_wordlist(self) -> List[str]:
        return ["/admin", "/login", "/wp-admin", "/portal", "/api"]

    def _discover_api_endpoints(self, body: str, robots_entries: List[str], sitemap_entries: List[str]) -> List[str]:
        candidates = []
        for entry in robots_entries + sitemap_entries:
            if "/api/" in entry or "/graphql" in entry.lower() or "/v1" in entry:
                candidates.append(entry)

        for match in re.findall(r"/(?:api|graphql|v[0-9]+)[^\s\"'<>]*", body, flags=re.IGNORECASE):
            candidates.append(match)

        return sorted(set(candidates))

    def _discover_auth_surface(self, body: str, urls: List[str]) -> List[str]:
        patterns = [
            r"/login",
            r"/signup",
            r"/register",
            r"/logout",
            r"/reset-password",
            r"/profile",
        ]
        matches = set()
        for pattern in patterns:
            for entry in urls + [body]:
                if isinstance(entry, str) and re.search(pattern, entry, flags=re.IGNORECASE):
                    matches.add(re.search(pattern, entry, flags=re.IGNORECASE).group(0))
        return sorted(matches)

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
