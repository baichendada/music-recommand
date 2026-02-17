"""
Lyrics Sentiment Analysis Module
Analyzes Chinese lyrics to extract sentiment and emotion
"""

import jieba
import re
from typing import Dict, List, Any
from collections import Counter

# Chinese sentiment lexicon (simplified)
POSITIVE_WORDS = {
    # Happy/Positive
    '爱', '喜欢', '快乐', '幸福', '开心', '欢笑', '美好', '甜蜜', '温暖',
    '希望', '梦想', '阳光', '春天', '花朵', '微笑', '拥抱', '亲爱的',
    '永远', '相伴', '珍惜', '感动', '感激', '美丽', '漂亮', '可爱',
    '心动', '激情', '热烈', '浪漫', '温柔', '柔软', '柔软', '关怀',
    '快乐', '欢快', '愉悦', '舒畅', '舒畅', '得意', '满足', '安慰',
    '甜蜜', '幸福', '美满', '如意', '顺畅', '爽', '酷', '帅', '靓',
}

NEGATIVE_WORDS = {
    # Sad/Negative
    '哭', '流泪', '悲伤', '难过', '伤心', '痛苦', '难受', '心碎',
    '离别', '分手', '失去', '孤单', '寂寞', '孤独', '无助', '绝望',
    '无奈', '遗憾', '后悔', '痛苦', '煎敖', '折腾', '挣扎', '困惑',
    '迷茫', '迷失', '堕落', '沉沦', '放弃', '失望', '绝望', '怨恨',
    '愤怒', '生气', '恼火', '烦躁', '郁闷', '压抑', '沉重', '阴暗',
    '冷漠', '无情', '残酷', '狠心', '绝情', '残忍', '恐怖', '害怕',
}

# Emotion-specific keywords
EMOTION_KEYWORDS = {
    'happy': ['快乐', '开心', '幸福', '欢笑', '甜蜜', '美好', '爱', '喜欢'],
    'sad': ['悲伤', '难过', '伤心', '眼泪', '哭', '心碎', '离别', '分手'],
    'angry': ['愤怒', '生气', '恼火', '怨恨', '讨厌', '恨', '可恶'],
    'calm': ['平静', '安宁', '静心', '放松', '舒缓', '温柔', '柔软'],
    'excited': ['激动', '兴奋', '热情', '热烈', '狂欢', '沸腾', '澎湃'],
    'relaxed': ['悠闲', '舒适', '自在', '轻松', '惬意', '舒缓', '放松'],
}

# Stopwords for Chinese text processing
STOPWORDS = {
    '的', '了', '是', '在', '有', '我', '你', '他', '她', '它', '们',
    '这', '那', '就', '也', '都', '而', '及', '与', '或', '但', '如果',
    '因为', '所以', '虽然', '但是', '可以', '没有', '什么', '怎么',
    '一个', '一些', '这个', '那个', '这样', '那样', '如何', '为什',
    '还', '又', '再', '已经', '曾经', '正在', '将要', '会', '能', '要',
}


def preprocess_lyrics(lyrics: str) -> List[str]:
    """
    Preprocess lyrics: tokenize and remove stopwords

    Args:
        lyrics: Raw lyrics text

    Returns:
        List of meaningful words
    """
    if not lyrics:
        return []

    # Remove punctuation and numbers
    cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', ' ', lyrics)

    # Tokenize using jieba
    words = jieba.cut(cleaned)

    # Filter stopwords and short words
    filtered = [w.strip() for w in words if w.strip() and len(w.strip()) > 1]

    return filtered


def analyze_sentiment(lyrics: str) -> Dict[str, Any]:
    """
    Analyze sentiment of lyrics

    Args:
        lyrics: Chinese lyrics text

    Returns:
        Dictionary with sentiment analysis results
    """
    if not lyrics:
        return {
            "sentiment_score": 0.5,
            "sentiment_label": "neutral",
            "positive_words": [],
            "negative_words": [],
            "word_count": 0
        }

    words = preprocess_lyrics(lyrics)

    # Count positive and negative words
    positive_found = [w for w in words if w in POSITIVE_WORDS]
    negative_found = [w for w in words if w in NEGATIVE_WORDS]

    # Calculate sentiment score (-1 to 1)
    total_words = len(words) if words else 1
    pos_ratio = len(positive_found) / total_words
    neg_ratio = len(negative_found) / total_words

    sentiment_score = pos_ratio - neg_ratio
    sentiment_score = max(-1, min(1, sentiment_score))  # Clamp to [-1, 1]

    # Determine sentiment label
    if sentiment_score > 0.2:
        label = "positive"
    elif sentiment_score < -0.2:
        label = "negative"
    else:
        label = "neutral"

    return {
        "sentiment_score": round(sentiment_score, 3),
        "sentiment_label": label,
        "positive_words": positive_found,
        "negative_words": negative_found,
        "word_count": total_words
    }


def analyze_emotions(lyrics: str) -> Dict[str, Any]:
    """
    Analyze emotions in lyrics

    Args:
        lyrics: Chinese lyrics text

    Returns:
        Dictionary with emotion analysis results
    """
    if not lyrics:
        return {
            "primary_emotion": "neutral",
            "emotion_scores": {},
            "emotion_tags": ["neutral"]
        }

    words = preprocess_lyrics(lyrics)
    word_count = len(words) if words else 1

    # Calculate emotion scores
    emotion_scores = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        count = sum(1 for w in words if w in keywords)
        emotion_scores[emotion] = round(count / word_count, 4)

    # Find primary emotion
    if emotion_scores:
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        if emotion_scores[primary_emotion] == 0:
            primary_emotion = "neutral"
    else:
        primary_emotion = "neutral"

    # Generate emotion tags
    emotion_tags = generate_emotion_tags(emotion_scores, primary_emotion)

    return {
        "primary_emotion": primary_emotion,
        "emotion_scores": emotion_scores,
        "emotion_tags": emotion_tags
    }


def generate_emotion_tags(emotion_scores: Dict[str, float], primary_emotion: str) -> List[str]:
    """
    Generate emotion tags based on analysis
    """
    tags = []

    # Add primary emotion
    if primary_emotion != "neutral" and emotion_scores.get(primary_emotion, 0) > 0:
        tags.append(primary_emotion)

    # Add secondary emotions with significant scores
    for emotion, score in emotion_scores.items():
        if emotion != primary_emotion and score > 0.005:
            tags.append(emotion)

    # If no strong emotions, return neutral
    return list(set(tags)) if tags else ["neutral"]


def analyze_lyrics(lyrics: str) -> Dict[str, Any]:
    """
    Full lyrics analysis combining sentiment and emotion analysis

    Args:
        lyrics: Chinese lyrics text

    Returns:
        Comprehensive analysis results
    """
    sentiment = analyze_sentiment(lyrics)
    emotions = analyze_emotions(lyrics)

    # Combine results
    return {
        "sentiment": sentiment,
        "emotions": emotions,
        "overall_tags": list(set(sentiment.get("positive_words", [])[:3] +
                               sentiment.get("negative_words", [])[:3] +
                               emotions.get("emotion_tags", [])))
    }


def get_emotion_tags_from_lyrics(lyrics: str) -> List[str]:
    """
    Convenience function to get emotion tags from lyrics

    Args:
        lyrics: Chinese lyrics text

    Returns:
        List of emotion tags
    """
    if not lyrics:
        return ["neutral"]

    emotions = analyze_emotions(lyrics)
    return emotions.get("emotion_tags", ["neutral"])


# Demo function for testing
def demo_analysis():
    """Demo with sample Chinese lyrics"""
    sample_lyrics = """
    从前有个人爱你很久 但偏偏风渐渐把距离吹得好远
    我想就这样把你带走 一个人不孤单 想念不难过
    亲爱的 你会不会忽然的想到我 会不会觉得心里很柔软
    """

    result = analyze_lyrics(sample_lyrics)
    print("=== Lyrics Analysis Result ===")
    print(f"Sentiment: {result['sentiment']['sentiment_label']}")
    print(f"Score: {result['sentiment']['sentiment_score']}")
    print(f"Primary Emotion: {result['emotions']['primary_emotion']}")
    print(f"Emotion Tags: {result['emotions']['emotion_tags']}")
    print(f"Emotion Scores: {result['emotions']['emotion_scores']}")


if __name__ == "__main__":
    demo_analysis()
