"""
Recommendation System Evaluation Script

Evaluates recommendation algorithms using:
- Precision
- Recall
- F1 Score
- NDCG (Normalized Discounted Cumulative Gain)
- Coverage

Compares:
- Content-Based
- Collaborative Filtering
- Hybrid (Combined)
"""

import random
from typing import List, Dict, Set
from collections import defaultdict

# Simulated data for evaluation
class Music:
    def __init__(self, id: int, emotion_tags: List[str]):
        self.id = id
        self.emotion_tags = emotion_tags

class User:
    def __init__(self, id: int, preferred_emotions: List[str]):
        self.id = id
        self.preferred_emotions = preferred_emotions
        self.interactions = []  # (music_id, interaction_type)

# Generate test data
def generate_test_data() -> tuple:
    """Generate test data for evaluation"""

    # Define emotions
    emotions = ['happy', 'sad', 'calm', 'excited', 'angry', 'relaxed']

    # Generate music database with emotion tags
    music_db = []
    for i in range(1, 101):
        # Random 1-3 emotion tags per music
        tags = random.sample(emotions, random.randint(1, 3))
        music_db.append(Music(id=i, emotion_tags=tags))

    # Generate users with preferences
    users = []
    for i in range(1, 51):
        # Each user has 1-2 preferred emotions
        prefs = random.sample(emotions, random.randint(1, 2))
        users.append(User(id=i, preferred_emotions=prefs))

    # Generate interactions (simulate user behavior)
    for user in users:
        # Each user has interacted with 10-30 music items
        num_interactions = random.randint(10, 30)
        interacted_music = random.sample(music_db, num_interactions)

        for music in interacted_music:
            # Determine if user liked (based on emotion match)
            has_match = any(tag in user.preferred_emotions for tag in music.emotion_tags)
            interaction_type = 'like' if (has_match and random.random() > 0.3) or random.random() > 0.7 else 'play'
            user.interactions.append((music.id, interaction_type))

    return users, music_db, emotions

# Recommendation Algorithms
class ContentBasedRecommender:
    """Content-Based Recommendation"""

    def __init__(self, music_db: List[Music]):
        self.music_db = music_db

    def recommend(self, user: User, limit: int = 10) -> List[int]:
        # Score by emotion tag matching
        scored = []
        for music in self.music_db:
            score = sum(1 for tag in music.emotion_tags if tag in user.preferred_emotions)
            scored.append((music.id, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in scored[:limit]]

class CollaborativeFilter:
    """Collaborative Filtering (simplified)"""

    def __init__(self, users: List[User], music_db: List[Music]):
        self.users = users
        self.music_db = music_db
        self.user_item_matrix = self._build_matrix()

    def _build_matrix(self) -> Dict[int, Dict[int, float]]:
        matrix = defaultdict(dict)
        for user in self.users:
            for music_id, interaction_type in user.interactions:
                matrix[user.id][music_id] = 1.0 if interaction_type == 'like' else 0.5
        return matrix

    def recommend(self, user: User, limit: int = 10) -> List[int]:
        # Find similar users (simplified: users with overlapping interactions)
        similar_users = []
        user_items = set(m[0] for m in user.interactions)

        for other in self.users:
            if other.id != user.id:
                other_items = set(m[0] for m in other.interactions)
                overlap = len(user_items & other_items)
                if overlap > 0:
                    similar_users.append((other.id, overlap))

        similar_users.sort(key=lambda x: x[1], reverse=True)

        # Recommend items from similar users
        recommendations = defaultdict(float)
        for similar_id, score in similar_users[:10]:
            user_music_dict = self.user_item_matrix.get(similar_id, {})
            for music_id, interaction_type in user_music_dict.items():
                if music_id not in user_items:
                    recommendations[music_id] += score * (1.0 if interaction_type == 'like' else 0.5)

        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [m[0] for m in sorted_recs[:limit]]

class HybridRecommender:
    """Hybrid Recommender (Content + CF)"""

    def __init__(self, users: List[User], music_db: List[Music]):
        self.content = ContentBasedRecommender(music_db)
        self.cf = CollaborativeFilter(users, music_db)
        self.weights = {'content': 0.6, 'cf': 0.4}

    def recommend(self, user: User, limit: int = 10) -> List[int]:
        content_recs = self.content.recommend(user, limit * 2)
        cf_recs = self.cf.recommend(user, limit * 2)

        # Combine scores
        combined = defaultdict(float)

        for i, music_id in enumerate(content_recs):
            combined[music_id] += (len(content_recs) - i) * self.weights['content']

        for i, music_id in enumerate(cf_recs):
            combined[music_id] += (len(cf_recs) - i) * self.weights['cf']

        sorted_recs = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return [m[0] for m in sorted_recs[:limit]]

# Evaluation Metrics
def get_relevant_items(user: User, music_db: List[Music]) -> Set[int]:
    """Get items that are relevant to user (based on emotion match)"""
    relevant = set()
    for music in music_db:
        if any(tag in user.preferred_emotions for tag in music.emotion_tags):
            relevant.add(music.id)
    return relevant

def precision_at_k(recommendations: List[int], relevant: Set[int], k: int = 10) -> float:
    """Calculate Precision@K"""
    recs = set(recommendations[:k])
    if k == 0:
        return 0.0
    return len(recs & relevant) / k

def recall_at_k(recommendations: List[int], relevant: Set[int], k: int = 10) -> float:
    """Calculate Recall@K"""
    recs = set(recommendations[:k])
    if len(relevant) == 0:
        return 0.0
    return len(recs & relevant) / len(relevant)

def f1_score(precision: float, recall: float) -> float:
    """Calculate F1 Score"""
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def ndcg_at_k(recommendations: List[int], relevant: Set[int], k: int = 10) -> float:
    """Calculate NDCG@K"""
    recs = recommendations[:k]

    dcg = 0.0
    for i, music_id in enumerate(recs):
        if music_id in relevant:
            dcg += 1.0 / (i + 1)

    # Ideal DCG
    idcg = sum(1.0 / (i + 1) for i in range(min(k, len(relevant))))

    if idcg == 0:
        return 0.0
    return dcg / idcg

def coverage(recommendations: List[int], music_db: List[Music]) -> float:
    """Calculate catalog coverage"""
    all_music_ids = set(m.id for m in music_db)
    rec_music_ids = set(recommendations)

    if len(all_music_ids) == 0:
        return 0.0
    return len(rec_music_ids & all_music_ids) / len(all_music_ids)

# Main Evaluation
def evaluate_algorithm(recommender, users: List[User], music_db: List[Music], k: int = 10):
    """Evaluate a recommender algorithm"""
    precisions = []
    recalls = []
    f1s = []
    ndcgs = []

    for user in users:
        relevant = get_relevant_items(user, music_db)

        if len(relevant) == 0:
            continue

        recs = recommender.recommend(user, k)

        p = precision_at_k(recs, relevant, k)
        r = recall_at_k(recs, relevant, k)
        f = f1_score(p, r)
        n = ndcg_at_k(recs, relevant, k)

        precisions.append(p)
        recalls.append(r)
        f1s.append(f)
        ndcgs.append(n)

    return {
        'precision': sum(precisions) / len(precisions) if precisions else 0,
        'recall': sum(recalls) / len(recalls) if recalls else 0,
        'f1': sum(f1s) / len(f1s) if f1s else 0,
        'ndcg': sum(ndcgs) / len(ndcgs) if ndcgs else 0,
    }

def run_evaluation():
    """Run full evaluation"""
    print("=" * 60)
    print("Music Recommendation System - Algorithm Evaluation")
    print("=" * 60)

    # Generate test data
    print("\n[1] Generating test data...")
    users, music_db, emotions = generate_test_data()
    print(f"    - {len(users)} users")
    print(f"    - {len(music_db)} music items")
    print(f"    - {len(emotions)} emotion categories")

    # Create recommenders
    print("\n[2] Creating recommenders...")
    content_rec = ContentBasedRecommender(music_db)
    cf_rec = CollaborativeFilter(users, music_db)
    hybrid_rec = HybridRecommender(users, music_db)

    # Evaluate each algorithm
    print("\n[3] Evaluating algorithms (K=10)...")
    print("-" * 60)

    results = {}

    for name, rec in [("Content-Based", content_rec),
                      ("Collaborative Filter", cf_rec),
                      ("Hybrid", hybrid_rec)]:
        metrics = evaluate_algorithm(rec, users, music_db, k=10)
        results[name] = metrics

        print(f"\n{name}:")
        print(f"  Precision@10: {metrics['precision']:.4f}")
        print(f"  Recall@10:    {metrics['recall']:.4f}")
        print(f"  F1 Score:    {metrics['f1']:.4f}")
        print(f"  NDCG@10:     {metrics['ndcg']:.4f}")

    # Compare algorithms
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Algorithm':<25} {'Precision':<12} {'Recall':<12} {'F1':<12} {'NDCG':<12}")
    print("-" * 60)

    for name, metrics in results.items():
        print(f"{name:<25} {metrics['precision']:<12.4f} {metrics['recall']:<12.4f} {metrics['f1']:<12.4f} {metrics['ndcg']:<12.4f}")

    # Find best algorithm
    best = max(results.items(), key=lambda x: x[1]['f1'])
    print(f"\n✓ Best Algorithm: {best[0]} (F1={best[1]['f1']:.4f})")

    print("\n[4] Evaluation complete!")

    return results

if __name__ == "__main__":
    run_evaluation()
