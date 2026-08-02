from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .providers import AIProvider, MockProvider, ProviderError


class ReportConfig:
    def __init__(self, output_dir: Optional[Path | str] = None, provider: str = "mock", api_key: Optional[str] = None):
        self.output_dir = Path(output_dir or "./reports")
        self.provider = provider
        self.api_key = api_key


class ReportEngine:
    def __init__(self, config: ReportConfig):
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.provider = self._build_provider()

    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ai_text = self.provider.generate_report(payload)
        sections = {
            "executive_summary": self._build_executive_summary(payload),
            "target_overview": {"host": payload.get("target", {}).get("host", "unknown")},
            "scan_statistics": payload.get("scan_statistics", {}),
            "technologies_detected": {"count": len(payload.get("technologies", [])), "items": payload.get("technologies", [])},
            "dns_information": payload.get("dns", {}),
            "subdomains": {"count": len(payload.get("subdomains", [])), "items": payload.get("subdomains", [])},
            "live_hosts": {"count": len(payload.get("live_hosts", [])), "items": payload.get("live_hosts", [])},
            "open_ports_and_services": {"count": len(payload.get("open_ports", [])), "items": payload.get("open_ports", [])},
            "robots_txt_findings": payload.get("robots", {}),
            "sitemap_findings": payload.get("sitemap", {}),
            "javascript_analysis_summary": payload.get("javascript", {}),
            "historical_urls_summary": {"count": len(payload.get("historical_urls", [])), "items": payload.get("historical_urls", [])},
            "api_discovery_summary": {"count": len(payload.get("api_discovery", [])), "items": payload.get("api_discovery", [])},
            "authentication_surface_summary": {"count": len(payload.get("auth_surface", [])), "items": payload.get("auth_surface", [])},
            "parameters_discovered": {"count": len(payload.get("parameters", [])), "items": payload.get("parameters", [])},
            "http_headers_summary": payload.get("headers", {}),
            "cookies_summary": {"count": len(payload.get("cookies", [])), "items": payload.get("cookies", [])},
            "ssl_tls_summary": payload.get("ssl", {}),
            "interesting_publicly_accessible_resources": {"count": len(payload.get("interesting_resources", [])), "items": payload.get("interesting_resources", [])},
            "overall_reconnaissance_summary": self._build_overall_summary(payload),
            "suggested_areas_for_manual_security_review": self._build_manual_review(payload),
            "scan_metadata": payload.get("metadata", {}),
        }

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "provider": self.config.provider,
            "executive_summary": sections["executive_summary"],
            "ai_generated_summary": ai_text,
            "sections": sections,
        }
        return report

    def write_reports(self, payload: Dict[str, Any]) -> Dict[str, Path]:
        report = self.generate(payload)
        report_path = self._write_json(report)
        html_path = self._write_html(report)
        markdown_path = self._write_markdown(report)
        pdf_path = self._write_pdf(report)
        return {"html": html_path, "markdown": markdown_path, "pdf": pdf_path, "json": report_path}

    def _build_provider(self) -> AIProvider:
        if self.config.provider == "mock":
            return MockProvider()
        raise ProviderError(f"Unsupported provider: {self.config.provider}")

    def _build_executive_summary(self, payload: Dict[str, Any]) -> str:
        host = payload.get("target", {}).get("host", "unknown")
        discovered = payload.get("scan_statistics", {}).get("hosts_discovered", 0)
        open_ports = payload.get("scan_statistics", {}).get("ports_open", 0)
        tech_count = len(payload.get("technologies", []))
        return (
            f"Reconnaissance for {host} completed with {discovered} host(s) identified and {open_ports} open port(s) "
            f"observed. The scan surfaced {tech_count} technology indicator(s) and a summary of publicly visible resources "
            f"for manual review."
        )

    def _build_overall_summary(self, payload: Dict[str, Any]) -> str:
        return (
            "The scanner collected structured reconnaissance data and the report engine translated it into a professional summary. "
            "No exploit or decision-making activity was performed by the AI component."
        )

    def _build_manual_review(self, payload: Dict[str, Any]) -> List[str]:
        recommendations = []
        if payload.get("robots", {}).get("entries"):
            recommendations.append("Review robots.txt exposure and any publicly accessible administrative paths.")
        if payload.get("interesting_resources"):
            recommendations.append("Inspect publicly accessible resources for unintended disclosure or misconfiguration.")
        if payload.get("open_ports"):
            recommendations.append("Validate the listed services and verify that they are intended and properly secured.")
        return recommendations or ["No specific manual review items were surfaced by the scanner data."]

    def _write_json(self, report: Dict[str, Any]) -> Path:
        path = self.config.output_dir / "report.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path

    def _write_html(self, report: Dict[str, Any]) -> Path:
        path = self.config.output_dir / "report.html"
        html = "<html><body><h1>Security Report</h1>"
        html += f"<p>{report['executive_summary']}</p>"
        html += f"<p><strong>AI summary:</strong> {report['ai_generated_summary']}</p>"
        html += "<h2>Sections</h2><ul>"
        for key, value in report["sections"].items():
            html += f"<li><strong>{key}</strong>: {self._render_value(value)}</li>"
        html += "</ul></body></html>"
        path.write_text(html, encoding="utf-8")
        return path

    def _write_markdown(self, report: Dict[str, Any]) -> Path:
        path = self.config.output_dir / "report.md"
        lines = ["# Security Report", "", f"{report['executive_summary']}", "", f"AI summary: {report['ai_generated_summary']}", "", "## Sections", ""]
        for key, value in report["sections"].items():
            lines.append(f"- **{key}**: {self._render_value(value)}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def _write_pdf(self, report: Dict[str, Any]) -> Path:
        path = self.config.output_dir / "report.pdf"
        path.write_bytes(b"%PDF-1.4\n%fake pdf\n")
        return path

    def _render_value(self, value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
