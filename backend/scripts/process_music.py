"""
Music Data Processing Script

This script processes the music in the database:
1. Downloads audio files (if URL provided)
2. Extracts real audio features using librosa
3. Analyzes lyrics sentiment using NLP
4. Generates emotion tags automatically
5. Updates the music database with real data

Run this script to populate the database with real AI-analyzed data.
"""

import requests
import os
import tempfile
from app.services.data_store import music_db, save_music_data
from app.ai.audio_extractor import extract_audio_features
from app.ai.lyrics_analyzer import analyze_lyrics, get_emotion_tags_from_lyrics
from app.ai.emotion_service import analyze_music_emotion, combine_emotion_tags

# Download audio file to temporary location
def download_audio(url: str) -> str:
    """Download audio file to temp and return path"""
    if not url.startswith('http'):
        return None

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Determine file extension
            ext = url.split('.')[-1] if '.' in url else 'mp3'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return None

def process_music(music_id: int, music_data: dict):
    """Process a single music item"""
    print(f"\n{'='*50}")
    print(f"Processing: {music_data['title']} - {music_data['artist']}")
    print(f"{'='*50}")

    results = {
        "audio_features": {},
        "lyrics_analysis": {},
        "emotion_tags": [],
        "primary_emotion": "neutral"
    }

    # 1. Try to download and analyze audio
    audio_path = None
    if music_data.get('audio_url'):
        print(f"[-] Attempting to download audio...")
        audio_path = download_audio(music_data['audio_url'])

        if audio_path and os.path.exists(audio_path):
            print(f"[-] Extracting audio features...")
            try:
                audio_features = extract_audio_features(audio_path)
                results["audio_features"] = audio_features
                print(f"    Tempo: {audio_features.get('tempo', 'N/A')}")
                print(f"    Energy: {audio_features.get('energy', 'N/A')}")
                print(f"    Mood: {audio_features.get('mood', 'N/A')}")
            except Exception as e:
                print(f"    Audio extraction failed: {e}")
        else:
            # Use demo features if download fails
            print(f"    Using demo features (download failed)")
            results["audio_features"] = {
                "tempo": 120,
                "energy": 0.5,
                "mood": "neutral",
                "note": "Demo - could not download audio"
            }

        # Clean up temp file
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
    else:
        print(f"[-] No audio URL provided, using defaults")

    # 2. Analyze lyrics
    lyrics = music_data.get('lyrics', '')
    if lyrics:
        print(f"[-] Analyzing lyrics...")
        try:
            lyrics_analysis = analyze_lyrics(lyrics)
            results["lyrics_analysis"] = lyrics_analysis

            sentiment = lyrics_analysis.get('sentiment', {})
            emotions = lyrics_analysis.get('emotions', {})

            print(f"    Sentiment: {sentiment.get('sentiment_label', 'N/A')} ({sentiment.get('sentiment_score', 0)})")
            print(f"    Primary Emotion: {emotions.get('primary_emotion', 'N/A')}")
            print(f"    Emotion Tags: {emotions.get('emotion_tags', [])}")
        except Exception as e:
            print(f"    Lyrics analysis failed: {e}")
    else:
        print(f"[-] No lyrics provided")

    # 3. Combine audio and lyrics to generate emotion tags
    print(f"[-] Generating combined emotion tags...")
    audio_tags = results["audio_features"].get("tags", [])
    lyrics_tags = results["lyrics_analysis"].get("emotions", {}).get("emotion_tags", [])

    combined_tags = combine_emotion_tags(audio_tags, lyrics_tags)
    results["emotion_tags"] = combined_tags

    # Determine primary emotion
    if lyrics_tags:
        results["primary_emotion"] = lyrics_tags[0]
    elif audio_tags:
        results["primary_emotion"] = audio_tags[0]

    print(f"    Combined Tags: {combined_tags}")
    print(f"    Primary Emotion: {results['primary_emotion']}")

    return results

def main():
    """Main processing function"""
    print("="*60)
    print("Music Data Processing Script")
    print("="*60)
    print(f"Found {len(music_db)} music items in database")

    # Process all music in database
    for music_id, music_data in list(music_db.items()):
        try:
            results = process_music(music_id, music_data)

            # Update music data with real analysis
            music_db[music_id].update({
                "audio_features": results["audio_features"],
                "emotion_tags": results["emotion_tags"],
                "_primary_emotion": results["primary_emotion"],
                "_lyrics_analysis": results["lyrics_analysis"]
            })

            print(f"[✓] Updated music ID {music_id}")

        except Exception as e:
            print(f"[✗] Failed to process music ID {music_id}: {e}")

    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)

    # Save processed data to file
    print("\n[+] Saving processed data to file...")
    save_music_data()
    print("[✓] Data saved successfully!")

    # Print summary
    print("\nDatabase Summary:")
    for music_id, music_data in music_db.items():
        print(f"  {music_id}. {music_data['title']} - {music_data.get('emotion_tags', [])}")

if __name__ == "__main__":
    main()
