"""
SERB Research Grants Scraper
Scrapes funding opportunities from https://serb.gov.in/page/english/research_grants
Falls back to curated data if live scraping fails.
"""
import json
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from config import SERB_URL

logger = logging.getLogger(__name__)

# Curated fallback data from SERB/ANRF (real program info)
FALLBACK_GRANTS: List[Dict[str, Any]] = [
    {
        "program_name": "Core Research Grant (CRG)",
        "description": "The Core Research Grant (CRG) scheme supports investigator-centric basic research proposals across all areas of Science & Engineering. It funds individual-centric, hypothesis-driven research in frontier areas of science and engineering including inter-disciplinary research. The scheme aims to provide competitive research funding to active researchers across the country.",
        "eligibility": "The PI must hold a regular academic/research position in a recognized institution. The PI should hold a PhD degree. Researchers up to 60 years (extendable to 62 for certain categories) of age at the time of submission are eligible. The PI's institution must provide basic infrastructure support.",
        "evaluation_criteria": "Proposals are evaluated on: (1) Scientific merit and novelty of the research idea (30%), (2) Competence of the investigator and track record (25%), (3) Methodology and feasibility of the approach (20%), (4) Expected impact and significance of results (15%), (5) Reasonableness of budget and timeline (10%). Proposals are peer-reviewed by expert committees.",
        "funding_limit": "Budget up to INR 50 lakhs for a duration of 3 years. Equipment costs should not exceed 30% of the total budget. International travel limited to one trip during the project duration. Manpower costs as per SERB norms.",
        "proposal_requirements": "Title page, Project summary (500 words max), Introduction and literature review, Objectives, Methodology, Work plan with timeline, Budget justification, PI's CV and publication list, List of ongoing/completed projects, Institutional endorsement letter",
        "application_guidelines": "Submit through SERB online portal (www.serbonline.in). Applications accepted throughout the year with quarterly review cycles. All documents must be in prescribed format. Budget should follow SERB financial norms.",
        "deadlines": "Rolling basis with quarterly review cycles (April, July, October, January)"
    },
    {
        "program_name": "Scientific and Useful Profound Research Advancement (SUPRA)",
        "description": "SUPRA supports unconventional and high-risk, high-reward research ideas that are transformative in nature. The scheme is designed to fund far-sighted, out-of-the-box proposals that may not find support through regular funding channels. It aims to push the boundaries of current understanding and enable paradigm-shifting discoveries.",
        "eligibility": "Active researchers with a proven track record of high-quality research. PI must hold a regular academic/research position. The proposal must demonstrate clearly the transformative potential and why it cannot be funded through regular schemes. Multi-institutional collaborations are encouraged.",
        "evaluation_criteria": "Proposals are evaluated on: (1) Transformative potential and paradigm-shifting nature (35%), (2) Scientific vision and clarity of the idea (25%), (3) Investigator's capability and track record (20%), (4) Feasibility and risk mitigation strategy (10%), (5) Budget justification (10%). Expert committees with domain knowledge review proposals.",
        "funding_limit": "Budget up to INR 1 crore for a duration of 3-5 years. Higher budgets considered for exceptional proposals with proper justification. Equipment costs permissible as per project needs.",
        "proposal_requirements": "Title page, Executive summary highlighting transformative nature, Detailed research proposal explaining the unconventional approach, Risk assessment and mitigation plan, Detailed methodology, Expected outcomes and timeline, Budget with justification, PI's profile highlighting relevant expertise",
        "application_guidelines": "Submit through SERB online portal. Proposals undergo multi-stage review including presentation to expert committee. Annual progress review mandatory.",
        "deadlines": "Annual call - typically announced in April/May each year"
    },
    {
        "program_name": "Fund for Industrial Research Engagement (FIRE)",
        "description": "FIRE aims to promote industry-relevant research by fostering collaboration between academia and industry. The scheme supports joint research projects that address industrial challenges through fundamental scientific inquiry. It bridges the gap between academic research and industrial application.",
        "eligibility": "Joint proposals from academic researchers and industry partners. PI must be from a recognized academic institution. Industry partner must provide matching contribution (at least 50% of the project cost). Proposal must address a specific industrial challenge with scientific approach.",
        "evaluation_criteria": "Proposals are evaluated on: (1) Industrial relevance and potential for technology translation (30%), (2) Scientific merit of the proposed approach (25%), (3) Quality of academia-industry collaboration plan (20%), (4) Competence of the team (15%), (5) Budget and resource planning (10%).",
        "funding_limit": "SERB provides up to INR 50 lakhs. Industry partner must match with at least 50% contribution. Total project duration up to 3 years.",
        "proposal_requirements": "Joint proposal with clearly defined roles, Problem statement with industrial context, Research methodology, Collaboration plan between academia and industry, IP sharing agreement, Technology transfer plan, Budget from both SERB and industry, Letters of commitment from industry partner",
        "application_guidelines": "Submit through SERB portal with industry partner endorsement. MoU between academic institution and industry partner must be submitted. Quarterly progress reports required.",
        "deadlines": "Annual call - typically announced in June/July each year"
    },
    {
        "program_name": "Start-up Research Grant (SRG)",
        "description": "The Start-up Research Grant provides research support to young scientists and engineers who are in the early stages of their career. It helps them establish their research program and build a competitive research profile. The scheme supports innovative research ideas from researchers who have recently joined academic/research institutions.",
        "eligibility": "Researchers within 7 years of obtaining PhD. Must have joined a regular academic/research position within the last 3 years. Age limit of 40 years at the time of application. Must not have received any other major research grant as PI.",
        "evaluation_criteria": "Proposals evaluated on: (1) Innovation and novelty of research idea (30%), (2) Potential of the young investigator (25%), (3) Methodology and feasibility (20%), (4) Expected impact (15%), (5) Budget appropriateness (10%).",
        "funding_limit": "Budget up to INR 30 lakhs for a duration of 2 years. Equipment costs should not exceed 25% of total budget.",
        "proposal_requirements": "Title page, Project summary (300 words), Research proposal (max 10 pages), Work plan with milestones, Budget justification, PI's CV with publications, Future research vision statement",
        "application_guidelines": "Submit through SERB online portal. Applications accepted on rolling basis. Mentorship plan recommended.",
        "deadlines": "Rolling basis - reviewed quarterly"
    }
]


class SERBScraper:
    """Scrapes SERB research grant programs from the official website."""

    def __init__(self):
        self.base_url = SERB_URL
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def scrape_programs(self) -> List[Dict[str, Any]]:
        """Scrape grant programs from SERB website, with fallback."""
        try:
            logger.info(f"Attempting to scrape {self.base_url}")
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            programs = self._parse_programs(soup)

            if programs and len(programs) >= 2:
                logger.info(f"Successfully scraped {len(programs)} programs from SERB")
                return programs
            else:
                logger.warning("Insufficient data scraped, using fallback data")
                return FALLBACK_GRANTS

        except Exception as e:
            logger.warning(f"Live scraping failed ({e}), using curated fallback data")
            return FALLBACK_GRANTS

    def _parse_programs(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse grant programs from the SERB page HTML."""
        programs = []

        # Try multiple selectors to find program listings
        containers = (
            soup.select(".research-grant, .grant-program, .program-item") or
            soup.select(".content-area .card, .content-area .item") or
            soup.select("table tr") or
            soup.select(".accordion-item, .panel") or
            soup.select("article, .post, .entry")
        )

        for container in containers:
            try:
                title_el = container.select_one("h2, h3, h4, .title, a, strong, td:first-child")
                if not title_el:
                    continue

                name = title_el.get_text(strip=True)
                if len(name) < 3 or len(name) > 200:
                    continue

                desc_el = container.select_one("p, .description, .content, td:nth-child(2)")
                description = desc_el.get_text(strip=True) if desc_el else ""

                link_el = container.select_one("a[href]")
                detail_url = link_el["href"] if link_el else None

                program = {
                    "program_name": name,
                    "description": description,
                    "eligibility": "",
                    "evaluation_criteria": "",
                    "funding_limit": "",
                    "proposal_requirements": "",
                    "application_guidelines": "",
                    "deadlines": "",
                }

                if detail_url:
                    detail_data = self._scrape_detail_page(detail_url)
                    program.update(detail_data)

                programs.append(program)
            except Exception as e:
                logger.debug(f"Skipping element: {e}")
                continue

        return programs

    def _scrape_detail_page(self, url: str) -> Dict[str, str]:
        """Scrape a detail page for additional program info."""
        try:
            if not url.startswith("http"):
                url = f"https://serb.gov.in{url}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            content = soup.select_one(".content-area, .main-content, article, .entry-content")
            if not content:
                content = soup.select_one("body")

            text = content.get_text(separator="\n", strip=True) if content else ""

            data = {}
            sections = {
                "eligibility": ["eligib", "who can apply", "qualif"],
                "evaluation_criteria": ["evaluat", "criteria", "review", "scoring", "rubric"],
                "funding_limit": ["fund", "budget", "amount", "financial", "grant size"],
                "proposal_requirements": ["requirement", "document", "format", "component"],
                "application_guidelines": ["guideline", "procedure", "how to apply", "submission"],
                "deadlines": ["deadline", "last date", "due date", "timeline"],
            }

            lines = text.split("\n")
            for key, keywords in sections.items():
                for i, line in enumerate(lines):
                    if any(kw in line.lower() for kw in keywords):
                        relevant_lines = lines[i:i+5]
                        data[key] = "\n".join(relevant_lines)
                        break

            return data
        except Exception as e:
            logger.debug(f"Failed to scrape detail page {url}: {e}")
            return {}

    def save_to_db(self, programs: List[Dict[str, Any]]) -> List[int]:
        """Save scraped programs to SQLite, return list of IDs."""
        conn = get_connection()
        cursor = conn.cursor()
        ids = []

        # Clear existing data for fresh scrape
        cursor.execute("DELETE FROM grant_programs")

        for program in programs:
            cursor.execute("""
                INSERT INTO grant_programs
                (program_name, description, eligibility, evaluation_criteria,
                 funding_limit, proposal_requirements, application_guidelines,
                 deadlines, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                program.get("program_name", ""),
                program.get("description", ""),
                program.get("eligibility", ""),
                program.get("evaluation_criteria", ""),
                program.get("funding_limit", ""),
                program.get("proposal_requirements", ""),
                program.get("application_guidelines", ""),
                program.get("deadlines", ""),
                json.dumps(program),
            ))
            ids.append(cursor.lastrowid)

        conn.commit()
        conn.close()
        logger.info(f"Saved {len(ids)} grant programs to database")
        return ids

    def save_to_json(self, programs: List[Dict[str, Any]], filepath: str = None):
        """Save scraped programs to a JSON file."""
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..", "data", "scraped_grants.json"
            )
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(programs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved grant data to {filepath}")

    def scrape_and_store(self) -> List[Dict[str, Any]]:
        """Full pipeline: scrape, save to DB and JSON, return programs."""
        programs = self.scrape_programs()
        self.save_to_db(programs)
        self.save_to_json(programs)
        return programs


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = SERBScraper()
    programs = scraper.scrape_and_store()
    for p in programs:
        print(f"  - {p['program_name']}")
