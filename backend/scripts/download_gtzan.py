"""
GTZAN Dataset Download and Processing Script

This script:
1. Downloads GTZAN dataset
2. Extracts audio features using Librosa
3. Maps genres to emotion tags
4. Generates music database for the recommendation system

GTZAN Genres: blues, classical, country, disco, hiphop, jazz, metal, pop, reggae, rock
"""

import os
import requests
import zipfile
import shutil
import json
from pathlib import Path

try:
    import numpy as np
    import librosa
except ImportError:
    print("Installing required packages...")
    os.system("pip install numpy librosa scipy")
    import numpy as np
    import librosa

# Genre to Emotion mapping
GENRE_TO_EMOTIONS = {
    "blues": ["sad", "calm"],
    "classical": ["calm", "relaxed"],
    "country": ["happy", "relaxed"],
    "disco": ["happy", "excited", "danceable"],
    "hiphop": ["excited", "energetic"],
    "jazz": ["calm", "relaxed"],
    "metal": ["angry", "excited"],
    "pop": ["happy", "excited"],
    "reggae": ["happy", "relaxed"],
    "rock": ["angry", "excited"],
}

# Extended genre to mood mapping
GENRE_TO_MOOD = {
    "blues": "sad",
    "classical": "calm",
    "country": "happy",
    "disco": "excited",
    "hiphop": "excited",
    "jazz": "calm",
    "metal": "angry",
    "pop": "happy",
    "reggae": "happy",
    "rock": "angry",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
GTZAN_DIR = os.path.join(DATA_DIR, 'gtzan', 'Data', 'genres_original')
OUTPUT_FILE = os.path.join(DATA_DIR, 'music_gtzan.json')


def download_gtzan():
    """Download GTZAN dataset"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(GTZAN_DIR, exist_ok=True)

    print("\n[*] GTZAN Download Instructions")
    print("="*60)
    print("Due to dataset size (~\1GB), please download manually:")
    print()
    print("Option 1: Kaggle")
    print("  1. Go to: https://www.kaggle.com/datasets/andradaolteanu/gtzan-dataset-music-genre-classification")
    print("  2. Download the ZIP file")
    print("  3. Extract to: " + GTZAN_DIR)
    print()
    print("Option 2: Internet Archive")
    print("  1. Go to: https://archive.org/details/gtzan-dataset-music-genre-classification")
    print("  2. Download 'gtzan-dataset-music-genre-classification.zip'")
    print("  3. Extract to: " + GTZAN_DIR)
    print()
    print("Expected folder structure:")
    print("  gtzan/")
    print("    blues/       (100 files)")
    print("    classical/   (100 files)")
    print("    country/     (100 files)")
    print("    disco/      (100 files)")
    print("    hiphop/      (100 files)")
    print("    jazz/        (100 files)")
    print("    metal/       (100 files)")
    print("    pop/         (100 files)")
    print("    reggae/      (100 files)")
    print("    rock/        (100 files)")
    print("="*60)
    return False


def check_gtzan_exists():
    """Check if GTZAN is already downloaded"""
    genres = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
    for genre in genres:
        genre_path = os.path.join(GTZAN_DIR, genre)
        if not os.path.exists(genre_path):
            return False
        if not os.listdir(genre_path):
            return False
    return True


def extract_features(audio_path):
    """Extract audio features from a file"""
    try:
        y, sr = librosa.load(audio_path, duration=30)

        # Extract features
        features = {
            "tempo": float(librosa.beat.tempo(y=y, sr=sr)[0]),
            "duration": float(librosa.get_duration(y=y, sr=sr)),
            "rms_energy": float(np.mean(librosa.feature.rms(y=y))),
            "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
            "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
            "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
            "spectral_bandwidth": float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))),
            "mfcc": {f"mfcc_{i}": float(np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)[i-1])) for i in range(1, 14)},
            "chroma": {note: float(np.mean(librosa.feature.chroma_stft(y=y, sr=sr)[i])) for i, note in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])},
        }

        # Calculate derived features
        features["energy"] = min(features["rms_energy"] * 10, 1.0)
        features["mood"] = GENRE_TO_MOOD.get(os.path.basename(os.path.dirname(audio_path)), "neutral")

        # Danceability based on tempo
        if 60 <= features["tempo"] <= 200:
            features["danceability"] = 0.5 + (features["tempo"] - 60) / 200
        else:
            features["danceability"] = 0.5
        features["danceability"] = min(max(features["danceability"], 0.3), 0.9)

        # Add emotion tags
        genre = os.path.basename(os.path.dirname(audio_path))
        features["tags"] = GENRE_TO_EMOTIONS.get(genre, ["neutral"])

        return features
    except Exception as e:
        print(f"[!] Error processing {audio_path}: {e}")
        return None


def process_gtzan():
    """Process all GTZAN files and generate music database"""
    print("\n" + "="*60)
    print("Processing GTZAN Dataset")
    print("="*60)

    genres = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
    music_db = {}
    music_id = 0

    # Count total files
    total_files = 0
    for genre in genres:
        genre_path = os.path.join(GTZAN_DIR, genre)
        if os.path.exists(genre_path):
            files = [f for f in os.listdir(genre_path) if f.endswith(('.wav', '.mp3', '.au', '.flac'))]
            total_files += len(files)
            print(f"[*] {genre}: {len(files)} files")

    if total_files == 0:
        print("[!] No audio files found!")
        return None

    print(f"\n[*] Total: {total_files} files to process")
    print("[*] This may take a while...\n")

    processed = 0
    for genre in genres:
        genre_path = os.path.join(GTZAN_DIR, genre)
        if not os.path.exists(genre_path):
            continue

        files = [f for f in os.listdir(genre_path) if f.endswith(('.wav', '.mp3', '.au', '.flac'))]

        for filename in files:
            audio_path = os.path.join(genre_path, filename)

            features = extract_features(audio_path)
            if features is None:
                continue

            music_id += 1
            music_db[music_id] = {
                "id": music_id,
                "title": filename.rsplit('.', 1)[0].replace('.', ' ').title()[:50],
                "artist": f"GTZAN {genre.title()}",
                "album": genre.title(),
                "duration": 30,
                "audio_url": audio_path,
                "cover_url": f"https://picsum.photos/seed/{genre}_{music_id}/300/300",
                "lyrics": f"Genre: {genre}",
                "emotion_tags": features.get("tags", []),
                "audio_features": features,
                "genre": genre,
                "source": "GTZAN",
            }

            processed += 1
            if processed % 50 == 0:
                print(f"=== Progress: {processed}/{total_files} ===")

    print(f"\n[+] Processed {processed} songs")
    return music_db


def save_music_data(music_db):
    """Save music database to JSON file"""
    print(f"\n[*] Saving to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(music_db, f, indent=2)

    print(f"[+] Saved {len(music_db)} songs to {OUTPUT_FILE}")
    return OUTPUT_FILE


def main():
    """Main function"""
    print("="*60)
    print("GTZAN Dataset Download & Processing")
    print("="*60)

    # Check if already exists
    if check_gtzan_exists():
        print("[+] GTZAN dataset found!")
    else:
        download_gtzan()
        return

    # Process
    music_db = process_gtzan()

    if music_db:
        save_music_data(music_db)

        # Print summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Total songs: {len(music_db)}")

        genre_count = {}
        for music in music_db.values():
            genre = music.get('genre', 'unknown')
            genre_count[genre] = genre_count.get(genre, 0) + 1

        print("\nSongs by genre:")
        for genre, count in sorted(genre_count.items()):
            emotions = GENRE_TO_EMOTIONS.get(genre, [])
            print(f"  {genre:12s}: {count:3d}  -> {emotions}")

        print(f"\n[+] Output: {OUTPUT_FILE}")
    else:
        print("[!] No music processed")


if __name__ == "__main__":
    main()
