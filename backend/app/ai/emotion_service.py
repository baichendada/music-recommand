"""
Emotion Tagging Service
Combines audio features and lyrics sentiment to generate emotion tags
"""

from typing import Dict, List, Any, Optional
from .audio_extractor import extract_audio_features, get_emotion_tags_from_audio
from .lyrics_analyzer import analyze_lyrics, get_emotion_tags_from_lyrics


def analyze_music_emotion(
    audio_url: Optional[str] = None,
    lyrics: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze music emotion by combining audio features and lyrics sentiment

    Args:
        audio_url: URL or path to audio file
        lyrics: Lyrics text

    Returns:
        Comprehensive emotion analysis results
    """
    result = {
        "audio_analysis": None,
        "lyrics_analysis": None,
        "combined_tags": [],
        "primary_emotion": "neutral",
        "confidence": 0.0
    }

    # Audio analysis
    if audio_url:
        try:
            audio_features = extract_audio_features(audio_url)
            audio_tags = get_emotion_tags_from_audio(audio_features)
            result["audio_analysis"] = {
                "features": audio_features,
                "tags": audio_tags
            }
        except Exception as e:
            result["audio_analysis"] = {"error": str(e)}

    # Lyrics analysis
    if lyrics:
        try:
            lyrics_result = analyze_lyrics(lyrics)
            lyrics_tags = lyrics_result.get("emotions", {}).get("emotion_tags", [])
            result["lyrics_analysis"] = {
                "sentiment": lyrics_result.get("sentiment", {}),
                "emotions": lyrics_result.get("emotions", {}),
                "tags": lyrics_tags
            }
        except Exception as e:
            result["lyrics_analysis"] = {"error": str(e)}

    # Combine tags from both sources
    audio_tags = []
    lyrics_tags = []

    if result.get("audio_analysis") and "tags" in result.get("audio_analysis", {}):
        audio_tags = result.get("audio_analysis", {}).get("tags", [])

    if result.get("lyrics_analysis") and "tags" in result.get("lyrics_analysis", {}):
        lyrics_tags = result.get("lyrics_analysis", {}).get("tags", [])

    combined_tags = combine_emotion_tags(audio_tags, lyrics_tags)

    result["combined_tags"] = combined_tags

    # Determine primary emotion
    primary_emotion, confidence = determine_primary_emotion(combined_tags)
    result["primary_emotion"] = primary_emotion
    result["confidence"] = confidence

    return result


def combine_emotion_tags(audio_tags: List[str], lyrics_tags: List[str]) -> List[str]:
    """
    Combine emotion tags from audio and lyrics

    Audio tags get higher weight for physical music characteristics
    Lyrics tags provide semantic context
    """
    all_tags = []

    # Priority: lyrics for emotional meaning, audio for music characteristics
    # But we prioritize tags that appear in both or have strong signal

    # Weight audio tags
    weighted_audio = []
    for tag in audio_tags:
        if tag in ["energetic", "danceable", "gentle"]:
            weighted_audio.append(tag)
        else:
            weighted_audio.append(tag)

    # Weight lyrics tags (higher priority for emotional meaning)
    weighted_lyrics = []
    for tag in lyrics_tags:
        if tag != "neutral":
            weighted_lyrics.append(tag)

    # Combine and deduplicate
    # Prioritize lyrics tags (emotional meaning)
    all_tags = weighted_lyrics + weighted_audio

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in all_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags[:5]  # Max 5 tags


def determine_primary_emotion(tags: List[str]) -> tuple:
    """
    Determine primary emotion from combined tags

    Returns:
        (primary_emotion, confidence)
    """
    if not tags:
        return ("neutral", 0.0)

    # Priority order for emotions
    emotion_priority = {
        'happy': 1,
        'excited': 2,
        'sad': 3,
        'angry': 4,
        'calm': 5,
        'relaxed': 6,
    }

    # Find highest priority emotion
    primary = None
    min_priority = float('inf')

    for tag in tags:
        if tag in emotion_priority:
            if emotion_priority[tag] < min_priority:
                primary = tag
                min_priority = emotion_priority[tag]

    if primary is None:
        return ("neutral", 0.5)

    # Confidence based on tag count
    confidence = min(0.9, 0.4 + (len(tags) * 0.1))

    return (primary, round(confidence, 2))


def get_recommended_emotions(emotion: str) -> List[str]:
    """
    Get related emotions for recommendation

    Args:
        emotion: Primary emotion

    Returns:
        List of related emotions
    """
    emotion_map = {
        'happy': ['happy', 'excited', 'relaxed'],
        'sad': ['sad', 'calm', 'relaxed'],
        'angry': ['angry', 'excited'],
        'calm': ['calm', 'relaxed', 'sad'],
        'excited': ['excited', 'happy'],
        'relaxed': ['relaxed', 'calm', 'happy'],
        'neutral': ['happy', 'calm', 'relaxed']
    }

    return emotion_map.get(emotion, ['happy', 'calm'])


# Map emotion to music特征 for recommendation
EMOTION_MUSIC_FEATURES = {
    'happy': {
        'min_energy': 0.6,
        'min_tempo': 110,
        'max_tempo': 160,
        'tags': ['happy', 'excited', 'danceable']
    },
    'sad': {
        'max_energy': 0.4,
        'max_tempo': 100,
        'tags': ['sad', 'calm', 'gentle']
    },
    'angry': {
        'min_energy': 0.7,
        'min_tempo': 130,
        'tags': ['angry', 'energetic']
    },
    'calm': {
        'max_energy': 0.4,
        'max_tempo': 90,
        'tags': ['calm', 'relaxed', 'gentle']
    },
    'excited': {
        'min_energy': 0.7,
        'min_tempo': 140,
        'tags': ['excited', 'happy', 'energetic', 'danceable']
    },
    'relaxed': {
        'max_energy': 0.5,
        'min_tempo': 70,
        'max_tempo': 110,
        'tags': ['relaxed', 'calm']
    }
}


def match_music_to_emotion(emotion: str, audio_features: Dict[str, Any]) -> float:
    """
    Calculate how well music matches an emotion

    Args:
        emotion: Target emotion
        audio_features: Audio features of the music

    Returns:
        Match score (0-1)
    """
    if emotion not in EMOTION_MUSIC_FEATURES:
        return 0.5

    target = EMOTION_MUSIC_FEATURES[emotion]
    score = 0.5

    # Check energy
    energy = audio_features.get("energy", 0.5)
    if 'min_energy' in target:
        if energy >= target['min_energy']:
            score += 0.2
    if 'max_energy' in target:
        if energy <= target['max_energy']:
            score += 0.2

    # Check tempo
    tempo = audio_features.get("tempo", 120)
    if 'min_tempo' in target:
        if tempo >= target['min_tempo']:
            score += 0.15
    if 'max_tempo' in target:
        if tempo <= target['max_tempo']:
            score += 0.15

    # Check tags
    music_tags = audio_features.get("tags", [])
    target_tags = target.get("tags", [])
    if any(tag in music_tags for tag in target_tags):
        score += 0.3

    return min(1.0, max(0.0, score))
