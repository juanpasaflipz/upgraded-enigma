import io
import json
import os
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from yt_dlp import YoutubeDL
import requests
import xml.etree.ElementTree as ET
import html


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", name).strip("-")


def captions_or_transcribe(youtube_url: str, work_dir: Optional[Path] = None) -> str:
    """Try to fetch real YouTube captions; if unavailable, fallback to Whisper if OPENAI_API_KEY is set; otherwise stub."""
    def log(msg: str):
        if work_dir:
            ensure_dir(work_dir)
            with open((work_dir / "pipeline.log"), "a", encoding="utf-8") as lf:
                lf.write(f"[{datetime.utcnow().isoformat()}Z] {msg}\n")

    vid = extract_youtube_id(youtube_url)
    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    cookies = os.getenv("YT_COOKIES_FILE")
    cookies_present = bool(cookies and Path(cookies).exists())
    log(f"Start pipeline for video_id={vid}")
    log(f"env: openai_key_present={api_key_present}, cookies_present={cookies_present}")
    if vid:
        text = fetch_youtube_captions(vid, log)
        if text:
            log("Used YouTube captions")
            return text
        else:
            log("No captions available; trying Whisper fallback")

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and vid:
        try:
            audio_path = download_audio(youtube_url, dest_dir=work_dir)
            log(f"Downloaded audio: {audio_path}")
            if audio_path:
                wt = whisper_transcribe(audio_path, api_key=api_key, log=log)
                if wt.strip():
                    log("Whisper transcription succeeded")
                    return wt
                else:
                    log("Whisper returned empty transcript")
        except Exception as e:
            log(f"Whisper/download failed: {e}")

    # Fallback stub
    vid = vid or "unknown"
    log("Falling back to stub transcript")
    return (
        f"Transcript for video {vid}.\n"
        "This is a mocked transcript generated for local testing.\n"
        "The video discusses building an MVP, focusing on goals, features, and a landing page.\n"
        "Key points: simplicity, Tailwind styling, and clear CTAs.\n"
    )


def fetch_youtube_captions(video_id: str, log=lambda *_: None) -> Optional[str]:
    """Fetch captions preferring English, manually-created first, then generated, else any."""
    try:
        # Check if the method exists (for version compatibility)
        if not hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            log(f"Caption API error: youtube-transcript-api version too old (need >= 2021.6.6)")
            return None
        
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        avail = []
        try:
            for t in transcripts:
                lang = getattr(t, 'language_code', None) or getattr(t, 'language', 'unknown')
                avail.append(lang)
        except Exception:
            pass
        if avail:
            log(f"Available transcript languages: {','.join(avail)}")
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        log(f"Caption list error: {type(e).__name__}")
        return None
    except AttributeError as e:
        log(f"Caption API error: {e}. Make sure youtube-transcript-api>=2021.6.6 is installed.")
        return None
    except Exception as e:
        log(f"Caption list error: {e}")
        return None

    # Prefer manually created English
    for langs in (['en', 'en-US', 'en-GB'], ['en'], ['en-US'], ['en-GB']):
        try:
            t = transcripts.find_manually_created_transcript(langs)
            parts = t.fetch()
            log(f"Using manually-created transcript: langs={langs}")
            return "\n".join(p.get("text", "").strip() for p in parts if p.get("text"))
        except Exception:
            pass
    # Prefer generated English
    for langs in (['en', 'en-US', 'en-GB'], ['en'], ['en-US'], ['en-GB']):
        try:
            t = transcripts.find_generated_transcript(langs)
            parts = t.fetch()
            log(f"Using generated transcript: langs={langs}")
            return "\n".join(p.get("text", "").strip() for p in parts if p.get("text"))
        except Exception:
            pass

    # Fallback to first available transcript
    for t in transcripts:
        try:
            parts = t.fetch()
            log("Using first available transcript")
            return "\n".join(p.get("text", "").strip() for p in parts if p.get("text"))
        except Exception:
            continue
    # HTTP fallback to timedtext endpoint
    http_text = fetch_youtube_captions_http(video_id, log)
    if http_text:
        log("Using timedtext HTTP captions fallback")
        return http_text
    return None


def fetch_youtube_captions_http(video_id: str, log=lambda *_: None) -> Optional[str]:
    """Fetch captions via public timedtext endpoint (manual or auto-generated)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    }
    langs = ["en", "en-US", "en-GB", "en-CA", "en-AU"]
    kinds = [None, "asr"]  # asr = auto-generated
    for lang in langs:
        for kind in kinds:
            params = {"v": video_id, "lang": lang}
            if kind:
                params["kind"] = kind
            try:
                r = requests.get("https://www.youtube.com/api/timedtext", params=params, headers=headers, timeout=10)
                if r.status_code == 200 and r.text and "<text" in r.text:
                    try:
                        root = ET.fromstring(r.text)
                        lines: list[str] = []
                        for node in root.findall("text"):
                            t = node.text or ""
                            t = html.unescape(t).replace("\n", " ").strip()
                            if t:
                                lines.append(t)
                        if lines:
                            log(f"Timedtext captions found lang={lang} kind={kind}")
                            return "\n".join(lines)
                    except Exception as e:
                        log(f"Timedtext parse error: {e}")
                        continue
            except Exception as e:
                log(f"Timedtext HTTP error: {e}")
                continue
    return None


def download_audio(youtube_url: str, dest_dir: Optional[Path] = None) -> Optional[Path]:
    """Download best audio without requiring ffmpeg; return the resulting file path (webm/m4a/…)
    """
    out_dir = dest_dir or Path.cwd()
    ensure_dir(out_dir)
    out_tmpl = str(out_dir / "audio.%(ext)s")
    cookies = os.getenv("YT_COOKIES_FILE")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_tmpl,
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "extractor_retries": 3,
        "concurrent_fragment_downloads": 1,
        # Avoid ffmpeg postprocessing; Whisper accepts m4a/webm
        # Provide a generic UA to reduce 403 chances
        "http_headers": {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"},
        # Emulate android client to bypass restrictions sometimes
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    if cookies and Path(cookies).exists():
        ydl_opts["cookiefile"] = cookies
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(youtube_url, download=True)
    # Find the downloaded file (audio.*)
    candidates = sorted(out_dir.glob("audio.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def whisper_transcribe(audio_path: Path, api_key: Optional[str] = None, log=lambda *_: None) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    primary_model = os.getenv("OPENAI_WHISPER_MODEL", "gpt-4o-transcribe")
    fallback_model = "whisper-1"
    try:
        with open(audio_path, "rb") as f:
            tr = client.audio.transcriptions.create(model=primary_model, file=f)
        return getattr(tr, "text", "") or ""
    except Exception as e:
        log(f"Primary transcribe failed ({primary_model}): {e}")
        try:
            with open(audio_path, "rb") as f:
                tr = client.audio.transcriptions.create(model=fallback_model, file=f)
            return getattr(tr, "text", "") or ""
        except Exception as e2:
            log(f"Fallback transcribe failed ({fallback_model}): {e2}")
            return ""


def extract_youtube_id(url: str) -> str | None:
    patterns = [
        r"(?:v=|/v/|/embed/|youtu.be/)([A-Za-z0-9_-]{6,})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def analyze_to_spec(transcript: str, title_hint: str | None = None) -> Dict:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL_GPT", "gpt-4o-mini")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            sys = (
                "You convert an app idea described in a transcript into a concise, strictly-typed JSON spec. "
                "Limit to a landing page MVP with hero, features, how-it-works, pricing, and CTA."
            )
            user = (
                "Transcript:\n" + transcript + "\n\nRespond ONLY with JSON matching: "
                "{title, description, features[], cta{label,href}, branding{primary,neutral}, sections[], generated_at}"
            )
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = resp.choices[0].message.content or "{}"
            data = json.loads(content)
            # Fill required fields if missing
            data.setdefault("title", title_hint or "Prototype Landing Page")
            data.setdefault("generated_at", datetime.utcnow().isoformat() + "Z")
            return data
        except Exception:
            pass

    # Fallback deterministic spec
    title = title_hint or "Prototype Landing Page"
    features = [
        "Hero section with headline and CTA",
        "Features grid with 3-4 items",
        "How it works steps",
        "Pricing section with tiers",
        "Footer with minimal links",
    ]
    return {
        "title": title,
        "description": "An auto-generated landing page prototype based on a YouTube video.",
        "features": features,
        "cta": {"label": "Get Started", "href": "/"},
        "branding": {
            "primary": "#22c55e",
            "neutral": "#18181b",
        },
        "sections": [
            {"id": "hero", "headline": f"{title}", "subtext": "Built from your video"},
            {"id": "features", "items": features},
            {"id": "how", "steps": ["Paste URL", "Analyze", "Generate Prototype"]},
            {"id": "pricing", "tiers": ["Free", "Pro", "Team"]},
        ],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def generate_prototype_zip(project_id: int, spec: Dict, artifacts_dir: Path) -> Path:
    # Create a minimal Next.js + Tailwind app with spec.json
    proj_dir = artifacts_dir / str(project_id)
    ensure_dir(proj_dir)
    template_dir = proj_dir / "template"
    if template_dir.exists():
        shutil.rmtree(template_dir)
    ensure_dir(template_dir)

    # Files
    (template_dir / "public").mkdir(parents=True, exist_ok=True)
    (template_dir / "app").mkdir(parents=True, exist_ok=True)
    (template_dir / "styles").mkdir(parents=True, exist_ok=True)

    (template_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "generated-prototype",
                "private": True,
                "version": "0.1.0",
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                },
                "dependencies": {
                    "next": "14.1.0",
                    "react": "18.2.0",
                    "react-dom": "18.2.0",
                    "tailwindcss": "^3.4.0",
                    "autoprefixer": "^10.4.17",
                    "postcss": "^8.4.35"
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (template_dir / "next.config.mjs").write_text(
        "export default { reactStrictMode: true }\n",
        encoding="utf-8",
    )

    (template_dir / "postcss.config.js").write_text(
        "module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }\n",
        encoding="utf-8",
    )

    (template_dir / "tailwind.config.js").write_text(
        (
            "module.exports = { content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './pages/**/*.{ts,tsx}', './public/**/*.html'], theme: { extend: {} }, plugins: [] }\n"
        ),
        encoding="utf-8",
    )

    (template_dir / "styles" / "globals.css").write_text(
        "@tailwind base;\n@tailwind components;\n@tailwind utilities;\nbody{ @apply bg-zinc-900 text-zinc-100;}\n",
        encoding="utf-8",
    )

    (template_dir / "app" / "layout.tsx").write_text(
        (
            "export default function RootLayout({ children }: { children: React.ReactNode }) {\n"
            "  return (<html lang=\"en\"><body className=\"min-h-screen bg-zinc-900 text-zinc-100\">{children}</body></html>);}\n"
        ),
        encoding="utf-8",
    )

    (template_dir / "app" / "page.tsx").write_text(
        (
            "'use client'\n\n"
            "import { useEffect, useState } from 'react'\n\n"
            "export default function Page(){\n"
            "  const [spec, setSpec] = useState<any>(null)\n"
            "  useEffect(()=>{ fetch('/spec.json').then(r=>r.json()).then(setSpec) },[])\n"
            "  if(!spec) return <div className='p-8'>Loading…</div>\n"
            "  return (\n"
            "    <main className='max-w-3xl mx-auto p-8 space-y-6'>\n"
            "      <h1 className='text-4xl font-bold'>{spec.title}</h1>\n"
            "      <p className='text-zinc-300'>{spec.description}</p>\n"
            "      <a href={spec.cta?.href || '#'} className='inline-block px-4 py-2 bg-emerald-500 text-black rounded-md'>\n"
            "        {spec.cta?.label || 'Get Started'}\n"
            "      </a>\n"
            "      <section>\n"
            "        <h2 className='text-2xl font-semibold mb-2'>Features</h2>\n"
            "        <ul className='list-disc pl-6 space-y-1'>\n"
            "          {(spec.features||[]).map((f:string,i:number)=>(<li key={i}>{f}</li>))}\n"
            "        </ul>\n"
            "      </section>\n"
            "    </main>\n"
            "  )\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    # Spec file
    (template_dir / "public" / "spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")

    # Zip it
    zip_path = proj_dir / "prototype.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(template_dir):
            for f in files:
                abs_path = Path(root) / f
                rel = abs_path.relative_to(template_dir)
                zf.write(abs_path, arcname=str(rel))

    # cleanup template_dir
    shutil.rmtree(template_dir, ignore_errors=True)
    return zip_path
