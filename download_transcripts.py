#!/usr/bin/env python3
"""
YouTube Transcript Downloader using TranscriptAPI.com

This script reads YouTube URLs from a text file and downloads transcripts
using the TranscriptAPI.com API.
"""

import os
import sys
import time
import re
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class TranscriptDownloader:
    """Handles downloading YouTube transcripts via TranscriptAPI.com"""
    
    BASE_URL = "https://transcriptapi.com/api/v2/youtube/transcript"
    
    def __init__(self, api_key: str):
        """
        Initialize the downloader with an API key.
        
        Args:
            api_key: Your TranscriptAPI.com API key
        """
        if not api_key:
            raise ValueError("API key is required. Set TRANSCRIPT_API_KEY environment variable.")
        
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL or video ID
            
        Returns:
            Video ID or None if not found
        """
        # If it's already just a video ID (11 characters)
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        # Try to extract from URL
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11})',  # Standard YouTube URLs
            r'youtu\.be\/([0-9A-Za-z_-]{11})',  # Short URLs
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def fetch_transcript(
        self,
        video_url: str,
        format: str = "json",
        include_timestamp: bool = True,
        send_metadata: bool = False,
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch transcript from TranscriptAPI.com with retry logic.
        
        Args:
            video_url: YouTube URL or video ID
            format: Output format ('json' or 'text')
            include_timestamp: Whether to include timestamps
            send_metadata: Whether to include video metadata
            max_retries: Maximum number of retry attempts
            
        Returns:
            API response as dictionary or None if failed
        """
        params = {
            "video_url": video_url,
            "format": format,
            "include_timestamp": str(include_timestamp).lower(),
            "send_metadata": str(send_metadata).lower()
        }
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                
                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                    print(f"  ⏳ Rate limit exceeded. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                # Handle successful response
                if response.status_code == 200:
                    return response.json()
                
                # Handle errors
                self._handle_error(response, video_url)
                return None
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  ⚠️  Request failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ Request failed after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def _handle_error(self, response: requests.Response, video_url: str):
        """Handle API error responses."""
        status_code = response.status_code
        
        try:
            error_data = response.json()
            error_msg = error_data.get("detail", "Unknown error")
        except:
            error_msg = response.text or "Unknown error"
        
        error_messages = {
            400: f"Bad Request: {error_msg}",
            401: "Unauthorized: Invalid or missing API key. Check your TRANSCRIPT_API_KEY.",
            402: f"Payment Required: {error_msg}",
            404: f"Not Found: Video not found or transcript unavailable for {video_url}",
            422: f"Validation Error: Invalid YouTube URL or ID - {video_url}",
            429: "Too Many Requests: Rate limit exceeded",
            500: f"Server Error: {error_msg}"
        }
        
        message = error_messages.get(status_code, f"Error {status_code}: {error_msg}")
        print(f"  ❌ {message}")
    
    def format_transcript_text(self, transcript_data: Dict[str, Any]) -> str:
        """
        Format transcript data as readable text.
        
        Args:
            transcript_data: Transcript data from API
            
        Returns:
            Formatted text string
        """
        transcript = transcript_data.get("transcript", [])
        
        if not transcript:
            return ""
        
        # If transcript is a list of segments
        if isinstance(transcript, list):
            lines = []
            for segment in transcript:
                if isinstance(segment, dict):
                    text = segment.get("text", "")
                    start = segment.get("start", 0)
                    
                    if start is not None:
                        lines.append(f"[{start:.2f}s] {text}")
                    else:
                        lines.append(text)
                else:
                    lines.append(str(segment))
            
            return "\n".join(lines)
        
        # If transcript is already a string
        return str(transcript)
    
    def save_transcript(
        self,
        video_url: str,
        transcript_data: Dict[str, Any],
        output_dir: str = "."
    ) -> Optional[str]:
        """
        Save transcript to a markdown file.
        
        Args:
            video_url: Original video URL
            transcript_data: Transcript data from API
            output_dir: Directory to save the file
            
        Returns:
            Path to saved file or None if failed
        """
        # Extract video ID for filename
        video_id = self.extract_video_id(video_url) or "unknown"
        
        # Get metadata if available
        metadata = transcript_data.get("metadata", {})
        title = metadata.get("title", f"Transcript {video_id}")
        
        # Clean filename
        filename = self._clean_filename(title)
        if not filename or filename == "unknown":
            filename = f"transcript_{video_id}"
        
        # Get language info
        language = transcript_data.get("language", "unknown")
        
        # Format transcript text
        transcript_text = self.format_transcript_text(transcript_data)
        
        # Create markdown content
        content = f"""# {title}

**Link Original:** {video_url}
**Video ID:** {video_id}
**Idioma detectado:** {language}

---

## Transcrição

{transcript_text}
"""
        
        # Add metadata section if available
        if metadata:
            author_name = metadata.get("author_name")
            author_url = metadata.get("author_url")
            if author_name:
                content += f"\n\n**Canal:** {author_name}"
                if author_url:
                    content += f" ({author_url})"
        
        # Save file
        filepath = os.path.join(output_dir, f"{filename}.md")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return filepath
        except Exception as e:
            print(f"  ❌ Erro ao salvar arquivo: {e}")
            return None
    
    def _clean_filename(self, title: str) -> str:
        """Remove invalid characters from filename."""
        # Remove YouTube suffix if present
        title = title.replace(" - YouTube", "").strip()
        
        # Remove invalid characters
        title = re.sub(r'[\\/*?:"<>|]', "", title)
        
        # Limit length
        if len(title) > 200:
            title = title[:200]
        
        return title.strip()


def read_urls_from_file(filepath: str) -> list:
    """
    Read URLs from a text file (one per line).
    
    Args:
        filepath: Path to the text file
        
    Returns:
        List of URLs
    """
    urls = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                # Skip empty lines and comments
                if url and not url.startswith('#'):
                    urls.append(url)
        
        return urls
    except FileNotFoundError:
        print(f"❌ Arquivo '{filepath}' não encontrado.")
        return []
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return []


def main():
    """Main function to process all videos from list.txt"""
    
    # Get API key from environment variable (loaded from .env file if present)
    api_key = os.getenv("TRANSCRIPT_API_KEY")
    if not api_key:
        print("❌ Erro: Variável de ambiente TRANSCRIPT_API_KEY não encontrada.")
        print("   Opções:")
        print("   1. Crie um arquivo .env na raiz do projeto com:")
        print("      TRANSCRIPT_API_KEY=sua_chave_aqui")
        print("   2. Ou configure manualmente:")
        print("      export TRANSCRIPT_API_KEY='sua_chave_aqui'")
        sys.exit(1)
    
    # Initialize downloader
    try:
        downloader = TranscriptDownloader(api_key)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Read URLs from file
    input_file = "list.txt"
    print(f"\n📂 Lendo links do arquivo: {input_file}")
    urls = read_urls_from_file(input_file)
    
    if not urls:
        print("❌ Nenhum link válido encontrado no arquivo.")
        sys.exit(1)
    
    print(f"✅ Encontrados {len(urls)} links para processar.\n")
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f"transcripts_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Pasta de saída criada: {output_dir}\n")
    
    # Counters
    successes = 0
    failures = 0
    
    # Process each video
    for idx, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"📹 Processando vídeo {idx}/{len(urls)}")
        print(f"🔗 {url}")
        print(f"{'='*60}")
        
        # Fetch transcript with metadata
        transcript_data = downloader.fetch_transcript(
            video_url=url,
            format="json",
            include_timestamp=True,
            send_metadata=True
        )
        
        if transcript_data:
            # Save transcript in the timestamped folder
            filepath = downloader.save_transcript(url, transcript_data, output_dir=output_dir)
            if filepath:
                print(f"  ✅ Transcrição salva: {filepath}")
                successes += 1
            else:
                print(f"  ❌ Falha ao salvar transcrição")
                failures += 1
        else:
            failures += 1
        
        # Rate limiting: respect 2 concurrent requests max
        # Add small delay between requests to avoid hitting limits
        if idx < len(urls):
            time.sleep(0.5)  # Small delay between requests
    
    # Final summary
    print(f"\n{'='*60}")
    print("📊 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"✅ Sucessos: {successes}")
    print(f"❌ Falhas: {failures}")
    print(f"📁 Total processado: {len(urls)}")
    print(f"📂 Pasta de saída: {output_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

