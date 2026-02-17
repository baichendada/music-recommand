"""
Audio Feature Extraction Module
Uses Librosa to extract audio features from music files
"""

import librosa
import numpy as np
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')


def extract_audio_features(audio_path: str) -> Dict[str, Any]:
    """
    Extract audio features from a music file.

    Args:
        audio_path: Path to the audio file (local or URL)

    Returns:
        Dictionary containing extracted audio features
    """
    try:
        # Load audio file
        # If it's a URL, librosa will try to load it directly
        # For demo purposes, we'll generate features based on duration
        y, sr = librosa.load(audio_path, duration=30) if 'http' not in audio_path else (None, 22050)

        if y is None:
            # Generate simulated features for demo
            return generate_demo_features()

        # Extract features
        features = {
            # Tempo (beats per minute)
            "tempo": float(librosa.beat.tempo(y=y, sr=sr)[0]),

            # Duration in seconds
            "duration": float(librosa.get_duration(y=y, sr=sr)),

            # Root Mean Square Energy
            "rms_energy": float(np.mean(librosa.feature.rms(y=y))),

            # Spectral Centroid
            "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),

            # Spectral Rolloff
            "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),

            # Zero Crossing Rate
            "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),

            # MFCCs (Mel-frequency cepstral coefficients)
            "mfcc": extract_mfcc(y, sr),

            # Chroma features
            "chroma": extract_chroma(y, sr),

            # Spectral bandwidth
            "spectral_bandwidth": float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))),

            # Spectral contrast
            "spectral_contrast": extract_spectral_contrast(y, sr),
        }

        # Calculate derived features
        features["energy"] = calculate_energy_level(features)
        features["mood"] = predict_mood(features)
        features["danceability"] = calculate_danceability(features)

        # Add emotion tags based on audio features
        features["tags"] = get_emotion_tags_from_audio(features)

        return features

    except Exception as e:
        # Return demo features if extraction fails
        return generate_demo_features()


def extract_mfcc(y, sr, n_mfcc=13) -> Dict[str, float]:
    """Extract MFCC features"""
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return {
        f"mfcc_{i+1}": float(np.mean(mfccs[i]))
        for i in range(n_mfcc)
    }


def extract_chroma(y, sr) -> Dict[str, float]:
    """Extract chroma features"""
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return {
        chroma_names[i]: float(np.mean(chroma[i]))
        for i in range(12)
    }


def extract_spectral_contrast(y, sr) -> Dict[str, float]:
    """Extract spectral contrast features"""
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    band_names = ['low', 'mid_low', 'mid', 'mid_high', 'high']
    return {
        band_names[i]: float(np.mean(contrast[i]))
        for i in range(5)
    }


def calculate_energy_level(features: Dict[str, Any]) -> float:
    """
    Calculate overall energy level (0-1) based on audio features
    """
    # Normalize tempo to 0-1 range (typical range 60-200 BPM)
    tempo_norm = min(max((features.get("tempo", 120) - 60) / 140, 0), 1)

    # RMS energy (already roughly 0-1)
    rms = min(features.get("rms_energy", 0.1) * 10, 1)

    # Zero crossing rate
    zcr = min(features.get("zero_crossing_rate", 0.1) * 10, 1)

    # Weighted average
    energy = (tempo_norm * 0.4 + rms * 0.4 + zcr * 0.2)
    return round(energy, 2)


def predict_mood(features: Dict[str, Any]) -> str:
    """
    Predict mood based on audio features
    """
    energy = features.get("energy", 0.5)
    tempo = features.get("tempo", 120)
    spectral_centroid = features.get("spectral_centroid", 2000)

    # High energy + high tempo = excited/happy
    # Low energy + low tempo = sad/calm
    # Medium values = neutral/relaxed

    if energy > 0.7 and tempo > 130:
        return "happy"
    elif energy > 0.6 and tempo > 100:
        return "excited"
    elif energy < 0.3 and tempo < 90:
        return "sad"
    elif energy < 0.4 and spectral_centroid < 1500:
        return "calm"
    elif energy > 0.5:
        return "relaxed"
    else:
        return "neutral"


def calculate_danceability(features: Dict[str, Any]) -> float:
    """
    Calculate danceability score (0-1)
    Based on tempo, rhythm regularity, and energy
    """
    tempo = features.get("tempo", 120)
    zcr = features.get("zero_crossing_rate", 0.1)
    energy = features.get("energy", 0.5)

    # Optimal dance tempo is around 120 BPM
    tempo_score = 1 - abs(tempo - 120) / 120

    # Higher zero crossing rate = more rhythmic
    rhythm_score = min(zcr * 8, 1)

    # Energy contributes to danceability
    danceability = (tempo_score * 0.4 + rhythm_score * 0.3 + energy * 0.3)

    return round(max(0, min(1, danceability)), 2)


def generate_demo_features() -> Dict[str, Any]:
    """
    Generate demo audio features for testing without actual audio files
    """
    features = {
        "tempo": 120.0,
        "duration": 240.0,
        "rms_energy": 0.15,
        "spectral_centroid": 2000.0,
        "spectral_rolloff": 4000.0,
        "zero_crossing_rate": 0.08,
        "spectral_bandwidth": 1800.0,
        "mfcc": {f"mfcc_{i}": 0.0 for i in range(1, 14)},
        "chroma": {note: 0.0 for note in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']},
        "spectral_contrast": {"low": 0.0, "mid_low": 0.0, "mid": 0.0, "mid_high": 0.0, "high": 0.0},
        "energy": 0.5,
        "mood": "neutral",
        "danceability": 0.5,
        "tags": ["neutral"]
    }
    return features


def get_emotion_tags_from_audio(features: Dict[str, Any]) -> list:
    """
    Generate emotion tags based on audio features
    """
    tags = []
    mood = features.get("mood", "neutral")
    energy = features.get("energy", 0.5)
    danceability = features.get("danceability", 0.5)

    # Add mood-based tags
    if mood in ["happy", "excited"]:
        tags.append("happy")
    if mood == "sad":
        tags.append("sad")
    if mood == "calm":
        tags.append("calm")
    if mood == "relaxed":
        tags.append("relaxed")

    # Add energy-based tags
    if energy > 0.7:
        tags.append("energetic")
    elif energy < 0.3:
        tags.append("gentle")

    # Add danceability tag
    if danceability > 0.7:
        tags.append("danceable")

    return list(set(tags)) if tags else ["neutral"]
