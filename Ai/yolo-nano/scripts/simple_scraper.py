"""
Bulk Argan Image Scraper — 1000+ images
Covers: argan trees, argan oil production, argan nuts/fruit, women cooperatives,
        Moroccan argan market, cosmetic argan products, argania spinosa botany.
Sources: Flickr (paginated) + Wikimedia (paginated) + OpenVerse (paginated)
         + Bing (multi-page) + Europeana
No paid API keys required.
"""

import os
import re
import sys
import time
import json
import hashlib
import argparse
import requests
from pathlib import Path
from urllib.parse import urlencode, quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# ── Config ────────────────────────────────────────────────────────────────────
MIN_SIZE_BYTES   = 15_000    # skip images < 15 KB
MAX_WORKERS      = 8         # parallel download threads
REQUEST_TIMEOUT  = 20
DELAY_BETWEEN_API = 0.5      # seconds between API calls (be polite)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── Search queries (diverse for variety) ─────────────────────────────────────
DEFAULT_QUERIES = [
    "argan tree morocco",
    "argan oil production morocco",
    "argania spinosa",
    "argan nuts harvesting",
    "moroccan argan cooperative women",
    "argan oil extraction traditional",
    "argan fruit morocco",
    "argan tree souss valley",
    "argan oil bottle cosmetic",
    "argan kernel cracking women",
    "argan forest morocco",
    "huile argan maroc",
    "argan tree goats climbing",
    "argan oil market morocco",
    "pure argan oil organic",
    "argan seed pressing morocco",
    "moroccan women argan oil",
    "argan tree agroforestry",
    "argan oil beauty cosmetic",
    "anti atlas argan morocco",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def url_ext(url: str) -> str:
    url_lower = url.lower().split("?")[0]
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        if url_lower.endswith(ext):
            return ext
    return ".jpg"


def url_to_filename(url: str, counter: int) -> str:
    digest = hashlib.md5(url.encode()).hexdigest()[:10]
    ext = url_ext(url)
    return f"{counter:05d}_{digest}{ext}"


def try_download(session: requests.Session, url: str, dest: Path) -> str:
    """Returns 'ok', 'skip' (exists), 'small', or 'error'."""
    if dest.exists():
        return "skip"
    try:
        r = session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
        r.raise_for_status()
        content = b"".join(r.iter_content(8192))
        if len(content) < MIN_SIZE_BYTES:
            return "small"
        dest.write_bytes(content)
        return "ok"
    except Exception:
        return "error"


# ── Source 1: Flickr public feed (keyless, paginated via tag search) ──────────

def flickr_urls(session: requests.Session, query: str, max_results: int = 200) -> list[str]:
    """Flickr keyless public feed — fetch multiple tag pages."""
    urls = []
    tags = quote_plus(query.replace(" ", ","))
    # Flickr public feed returns up to 20 per request, no pagination param
    # but we can vary tags slightly to get different results
    variations = [
        query,
        query + " harvesting",
        query + " traditional",
        query + " morocco",
        query + " women cooperative",
        query + " organic",
        query + " souss",
        query + " forest",
        query + " production",
        query + " fruit nuts",
    ]
    for var in variations:
        if len(urls) >= max_results:
            break
        feed_url = (
            "https://api.flickr.com/services/feeds/photos_public.gne?"
            + urlencode({
                "tags": var.replace(" ", ","),
                "format": "json",
                "nojsoncallback": 1,
                "lang": "en-us",
            })
        )
        try:
            r = session.get(feed_url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            for item in data.get("items", []):
                img = item.get("media", {}).get("m", "")
                if img:
                    urls.append(img.replace("_m.", "_b."))  # upgrade to large
        except Exception:
            pass
        time.sleep(DELAY_BETWEEN_API)

    return list(dict.fromkeys(urls))  # dedupe


# ── Source 2: Wikimedia Commons (paginated with continue tokens) ──────────────

def wikimedia_urls(session: requests.Session, query: str, max_results: int = 300) -> list[str]:
    """Full Wikimedia Commons search with pagination."""
    urls = []
    api = "https://commons.wikimedia.org/w/api.php"
    gsroffset = 0

    while len(urls) < max_results:
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": 6,
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrlimit": 50,
            "gsroffset": gsroffset,
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": 1000,
            "format": "json",
        }
        try:
            r = session.get(api, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                break
            for page in pages.values():
                info = page.get("imageinfo", [{}])[0]
                if info.get("mime", "").startswith("image/"):
                    url = info.get("thumburl") or info.get("url", "")
                    if url:
                        urls.append(url)
            # Check if more pages exist
            if "continue" not in data:
                break
            gsroffset += 50
        except Exception:
            break
        time.sleep(DELAY_BETWEEN_API)

    return list(dict.fromkeys(urls))


# ── Source 3: OpenVerse (paginated) ──────────────────────────────────────────

def openverse_urls(session: requests.Session, query: str, max_results: int = 300) -> list[str]:
    """OpenVerse paginated search — completely free."""
    urls = []
    api = "https://api.openverse.org/v1/images/"
    page = 1

    while len(urls) < max_results:
        params = {
            "q": query,
            "page_size": 50,
            "page": page,
            "format": "json",
        }
        try:
            r = session.get(api, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            if not results:
                break
            for item in results:
                url = item.get("url") or item.get("thumbnail", "")
                if url:
                    urls.append(url)
            # Check total pages
            total_pages = data.get("page_count", 1)
            if page >= total_pages:
                break
            page += 1
        except Exception:
            break
        time.sleep(DELAY_BETWEEN_API)

    return list(dict.fromkeys(urls))


# ── Source 4: Bing Images (multi-page scrape) ─────────────────────────────────

def bing_urls(session: requests.Session, query: str, max_results: int = 300) -> list[str]:
    """Scrape Bing image search across multiple pages."""
    urls = []
    first = 1

    while len(urls) < max_results:
        search_url = (
            "https://www.bing.com/images/search?"
            + urlencode({
                "q": query,
                "count": 35,
                "first": first,
                "tsc": "ImageBasicHover",
                "form": "IRBTSC",
            })
        )
        try:
            r = session.get(search_url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            html = r.text
            # Extract actual image URLs from Bing's embedded JSON
            found = re.findall(r'"murl":"(https?://[^"]+)"', html)
            if not found:
                break
            for u in found:
                try:
                    u_clean = u.encode().decode("unicode_escape")
                except Exception:
                    u_clean = u
                if any(u_clean.lower().split("?")[0].endswith(e)
                       for e in [".jpg", ".jpeg", ".png", ".webp"]):
                    urls.append(u_clean)
            first += 35
            if first > 200:  # Bing stops showing new results after ~200
                break
        except Exception:
            break
        time.sleep(1.0)  # Bing needs a longer delay

    return list(dict.fromkeys(urls))


# ── Source 5: Europeana (European cultural heritage, great for crafts) ────────

def europeana_urls(session: requests.Session, query: str, max_results: int = 200) -> list[str]:
    """
    Europeana API — free, no key required for basic search.
    Great source for traditional craft images.
    """
    urls = []
    api = "https://api.europeana.eu/record/v2/search.json"
    cursor = "*"

    while len(urls) < max_results:
        params = {
            "query": query,
            "qf": "TYPE:IMAGE",
            "rows": 100,
            "cursor": cursor,
            "profile": "rich",
            "wskey": "api2demo",  # Europeana's public demo key
        }
        try:
            r = session.get(api, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            items = data.get("items", [])
            if not items:
                break
            for item in items:
                # Try edmIsShownBy first (full image), then edmPreview (thumb)
                for field in ["edmIsShownBy", "edmPreview"]:
                    val = item.get(field)
                    if val:
                        url = val[0] if isinstance(val, list) else val
                        if url.startswith("http"):
                            urls.append(url)
                            break
            cursor = data.get("nextCursor", "")
            if not cursor:
                break
        except Exception:
            break
        time.sleep(DELAY_BETWEEN_API)

    return list(dict.fromkeys(urls))


# ── Source 6: iNaturalist (open science, good for real-world photos) ──────────

def inaturalist_urls(session: requests.Session, query: str, max_results: int = 100) -> list[str]:
    """iNaturalist observations API — open, no key needed."""
    # More relevant for natural subjects, skip if query not nature-related
    # Still useful for street/market scenes tagged with plants/environments
    urls = []
    api = "https://api.inaturalist.org/v1/observations"
    page = 1

    while len(urls) < max_results:
        params = {
            "q": query,
            "per_page": 200,
            "page": page,
            "photos": True,
            "quality_grade": "research",
        }
        try:
            r = session.get(api, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            if not results:
                break
            for obs in results:
                for photo in obs.get("photos", []):
                    url = photo.get("url", "").replace("/square.", "/large.")
                    if url:
                        urls.append(url)
            page += 1
            if page > 5:
                break
        except Exception:
            break
        time.sleep(DELAY_BETWEEN_API)

    return list(dict.fromkeys(urls))


# ── URL collector: run all sources for one query ──────────────────────────────

def collect_urls_for_query(session: requests.Session, query: str, verbose: bool = True) -> list[str]:
    all_urls = []

    sources = [
        ("Flickr",       flickr_urls,       250),
        ("Wikimedia",    wikimedia_urls,     300),
        ("OpenVerse",    openverse_urls,     300),
        ("Bing",         bing_urls,          300),
        ("Europeana",    europeana_urls,     200),
    ]

    for name, fn, limit in sources:
        if verbose:
            print(f"    📡 {name}...", end=" ", flush=True)
        try:
            result = fn(session, query, max_results=limit)
            if verbose:
                print(f"{len(result)} URLs")
            all_urls.extend(result)
        except Exception as e:
            if verbose:
                print(f"ERROR: {e}")

    # Deduplicate
    seen, unique = set(), []
    for u in all_urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)

    return unique


# ── Parallel download ─────────────────────────────────────────────────────────

class DownloadStats:
    def __init__(self):
        self.saved = 0
        self.skipped = 0
        self.small = 0
        self.errors = 0
        self._lock = Lock()

    def record(self, result: str):
        with self._lock:
            if result == "ok":      self.saved   += 1
            elif result == "skip":  self.skipped += 1
            elif result == "small": self.small   += 1
            else:                   self.errors  += 1

    def total(self):
        return self.saved + self.skipped + self.small + self.errors

    def __str__(self):
        return (f"✅ {self.saved} saved | ⏭ {self.skipped} skipped | "
                f"🔸 {self.small} too small | ❌ {self.errors} errors")


def download_batch(urls: list[str], out_dir: Path, start_counter: int,
                   stats: DownloadStats, target: int, verbose: bool = True) -> int:
    """Download URLs in parallel, stop once `target` new images are saved."""
    saved_this_batch = 0
    counter = start_counter

    def worker(args):
        idx, url = args
        session = make_session()
        fname = url_to_filename(url, idx)
        dest = out_dir / fname
        result = try_download(session, url, dest)
        return result, fname

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(worker, (counter + i, url)): url
            for i, url in enumerate(urls)
        }
        for future in as_completed(futures):
            result, fname = future.result()
            stats.record(result)
            if result == "ok":
                saved_this_batch += 1
                if verbose:
                    print(f"    ✅ [{stats.saved:>5}] {fname}")
                if stats.saved >= target:
                    # Cancel remaining
                    for f in futures:
                        f.cancel()
                    break
            elif result == "small" and verbose:
                print(f"    🔸 Too small, skipped")
            elif result == "error" and verbose:
                print(f"    ❌ Download failed")

    return saved_this_batch


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Bulk image scraper — 1000+ images, no API keys needed"
    )
    parser.add_argument("--output",  "-o", default="argan_bulk",
                        help="Output directory (default: argan_bulk)")
    parser.add_argument("--target",  "-n", type=int, default=1000,
                        help="Total images to download (default: 1000)")
    parser.add_argument("--queries", "-q", nargs="+", default=None,
                        help="Custom queries (space-separated, quoted)")
    parser.add_argument("--quiet",   action="store_true",
                        help="Less verbose output")
    args = parser.parse_args()

    queries  = args.queries or DEFAULT_QUERIES
    out_dir  = Path(args.output)
    target   = args.target
    verbose  = not args.quiet

    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 65)
    print("🌿  Bulk Argan Image Scraper — 1000+ Mode")
    print("=" * 65)
    print(f"  🎯 Target      : {target} images")
    print(f"  📋 Queries     : {len(queries)}")
    print(f"  📁 Output dir  : {out_dir.resolve()}")
    print(f"  ⚡ Threads     : {MAX_WORKERS}")
    print(f"  🌐 Sources     : Flickr + Wikimedia + OpenVerse + Bing + Europeana")
    print("=" * 65 + "\n")

    session = make_session()
    stats   = DownloadStats()
    counter = 0
    all_collected_urls: list[str] = []
    seen_urls: set[str] = set()

    # ── Phase 1: collect ALL URLs across all queries ──────────────────────────
    print("📥 PHASE 1 — Collecting image URLs from all sources...\n")

    for qi, query in enumerate(queries, 1):
        print(f"  🔍 [{qi}/{len(queries)}] '{query}'")
        urls = collect_urls_for_query(session, query, verbose=verbose)
        new_urls = [u for u in urls if u not in seen_urls]
        seen_urls.update(new_urls)
        all_collected_urls.extend(new_urls)
        print(f"       → {len(new_urls)} new unique URLs (total pool: {len(all_collected_urls)})\n")

        if len(all_collected_urls) >= target * 3:
            print("  ✋ URL pool large enough, stopping collection early.\n")
            break

    print(f"📊 Total URL pool: {len(all_collected_urls)} unique URLs")
    print(f"🎯 Need to save: {target} images\n")

    # ── Phase 2: download ─────────────────────────────────────────────────────
    print("⬇️  PHASE 2 — Downloading images...\n")

    download_batch(
        urls=all_collected_urls,
        out_dir=out_dir,
        start_counter=counter,
        stats=stats,
        target=target,
        verbose=verbose,
    )

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("🏁  FINAL SUMMARY")
    print("=" * 65)
    print(f"  {stats}")
    print(f"  📁 Images saved to: {out_dir.resolve()}")
    print(f"  🗂️  Files in dir   : {len(list(out_dir.glob('*')))}")
    if stats.saved < target:
        shortfall = target - stats.saved
        print(f"\n  ⚠️  {shortfall} images short of target.")
        print(f"     Try adding more --queries or increasing source page limits.")
    else:
        print(f"\n  🎉 Target of {target} images reached!")
    print("=" * 65)


if __name__ == "__main__":
    main()