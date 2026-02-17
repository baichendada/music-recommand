"""
Hybrid Recommendation with Matrix Factorization and Cosine Similarity

Core Features:
1. User-Item Matrix Construction
2. Cosine Similarity Calculation
3. Hybrid Recommendation (Content-Based + Collaborative Filtering)
"""

import numpy as np
from scipy import sparse
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from typing import Dict, List, Set, Tuple, Optional
import pickle
import os

from app.models.schemas import EmotionType, InteractionType
from app.services import data_store


class UserItemMatrix:
    """User-Item Interaction Matrix with SVD for collaborative filtering"""

    def __init__(self):
        self.user_item_matrix: csr_matrix = None
        self.user_ids: Dict[int, int] = {}  # original user_id -> matrix index
        self.music_ids: Dict[int, int] = {}  # original music_id -> matrix index
        self.reverse_user_ids: Dict[int, int] = {}  # matrix index -> original user_id
        self.reverse_music_ids: Dict[int, int] = {}  # matrix index -> original music_id
        self.item_similarity: csr_matrix = None  # item-item similarity matrix
        self.user_similarity: csr_matrix = None  # user-user similarity matrix

    def build_matrix(self) -> None:
        """Build user-item matrix from interaction data"""
        # Collect all unique users and music
        users = set()
        music = set()

        for interaction in data_store.interactions_db.values():
            users.add(interaction['user_id'])
            music.add(interaction['music_id'])

        if not users or not music:
            print("[!] No interactions to build matrix")
            return

        # Create id mappings
        self.user_ids = {uid: idx for idx, uid in enumerate(sorted(users))}
        self.music_ids = {mid: idx for idx, mid in enumerate(sorted(music))}
        self.reverse_user_ids = {idx: uid for uid, idx in self.user_ids.items()}
        self.reverse_music_ids = {idx: mid for mid, idx in self.music_ids.items()}

        # Build interaction matrix
        rows, cols, data = [], [], []

        for interaction in data_store.interactions_db.values():
            user_idx = self.user_ids.get(interaction['user_id'])
            music_idx = self.music_ids.get(interaction['music_id'])

            if user_idx is None or music_idx is None:
                continue

            # Weight based on interaction type
            weight = 0
            if interaction['interaction_type'] == InteractionType.LIKE:
                weight = 3.0
            elif interaction['interaction_type'] == InteractionType.PLAY:
                # Use play duration as weight (normalized)
                weight = min(interaction.get('play_duration', 0) / 60.0, 2.0) + 0.5

            if weight > 0:
                rows.append(user_idx)
                cols.append(music_idx)
                data.append(weight)

        n_users = len(self.user_ids)
        n_music = len(self.music_ids)

        self.user_item_matrix = csr_matrix(
            (data, (rows, cols)),
            shape=(n_users, n_music)
        )

        print(f"[+] Built user-item matrix: {n_users} users x {n_music} music")
        print(f"[+] Total interactions: {len(data)}")

    def compute_similarity(self) -> None:
        """Compute user-user and item-item cosine similarity"""
        if self.user_item_matrix is None:
            return

        # Item-item similarity (transpose: items as rows)
        # Use SVD to reduce dimensionality first for efficiency
        n_components = min(50, min(self.user_item_matrix.shape) - 1)
        if n_components > 0:
            svd = TruncatedSVD(n_components=n_components, random_state=42)
            matrix_reduced = svd.fit_transform(self.user_item_matrix)
            self.item_similarity = cosine_similarity(matrix_reduced)
            self.user_similarity = cosine_similarity(matrix_reduced.T)
        else:
            self.item_similarity = cosine_similarity(self.user_item_matrix.T.toarray())
            self.user_similarity = cosine_similarity(self.user_item_matrix.toarray())

        print(f"[+] Computed similarity matrices")

    def recommend_items(
        self,
        user_id: int,
        n_items: int = 10,
        exclude_items: Set[int] = None
    ) -> List[int]:
        """Get collaborative filtering recommendations for a user"""
        if self.user_item_matrix is None or user_id not in self.user_ids:
            return []

        if exclude_items is None:
            exclude_items = set()

        user_idx = self.user_ids[user_id]
        user_vector = self.user_item_matrix[user_idx].toarray().flatten()

        # Get items user hasn't interacted with
        candidate_items = []
        for music_id, music_idx in self.music_ids.items():
            if music_id not in exclude_items and user_vector[music_idx] == 0:
                candidate_items.append((music_id, music_idx))

        if not candidate_items:
            return []

        # Score using item-item similarity with user's liked items
        user_liked_indices = np.where(user_vector > 0)[0]
        if len(user_liked_indices) == 0:
            return []

        scores = []
        for music_id, music_idx in candidate_items:
            # Calculate score based on similarity to liked items
            if self.item_similarity is not None:
                sim_scores = self.item_similarity[music_idx, user_liked_indices]
                score = np.sum(sim_scores * user_vector[user_liked_indices])
            else:
                score = 0
            scores.append((music_id, score))

        # Sort by score and return top N
        scores.sort(key=lambda x: x[1], reverse=True)
        return [music_id for music_id, score in scores[:n_items]]

    def find_similar_users(
        self,
        user_id: int,
        n_users: int = 5
    ) -> List[Tuple[int, float]]:
        """Find similar users based on interaction patterns"""
        if self.user_similarity is None or user_id not in self.user_ids:
            return []

        user_idx = self.user_ids[user_id]
        similarities = self.user_similarity[user_idx]

        # Get top similar users (excluding self)
        similar = []
        for idx, sim in enumerate(similarities):
            if idx != user_idx:
                similar.append((self.reverse_user_ids[idx], sim))

        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:n_users]

    def save(self, filepath: str) -> None:
        """Save matrix to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'user_item_matrix': self.user_item_matrix,
                'user_ids': self.user_ids,
                'music_ids': self.music_ids,
                'reverse_user_ids': self.reverse_user_ids,
                'reverse_music_ids': self.reverse_music_ids,
                'item_similarity': self.item_similarity,
                'user_similarity': self.user_similarity
            }, f)

    def load(self, filepath: str) -> bool:
        """Load matrix from file"""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.user_item_matrix = data['user_item_matrix']
                self.user_ids = data['user_ids']
                self.music_ids = data['music_ids']
                self.reverse_user_ids = data['reverse_user_ids']
                self.reverse_music_ids = data['reverse_music_ids']
                self.item_similarity = data['item_similarity']
                self.user_similarity = data['user_similarity']
            return True
        except Exception as e:
            print(f"[!] Failed to load matrix: {e}")
            return False


class HybridRecommender:
    """
    Hybrid Recommender combining:
    1. Content-Based: Emotion tag matching
    2. Collaborative Filtering: User-item matrix with cosine similarity
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data'
        )
        self.matrix_file = os.path.join(self.data_dir, 'user_item_matrix.pkl')
        self.user_item_matrix = UserItemMatrix()

    def rebuild_matrix(self) -> None:
        """Rebuild user-item matrix from current interactions"""
        self.user_item_matrix.build_matrix()
        self.user_item_matrix.compute_similarity()
        self.user_item_matrix.save(self.matrix_file)

    def load_matrix(self) -> bool:
        """Load existing matrix or rebuild if not exists"""
        if self.user_item_matrix.load(self.matrix_file):
            print("[+] Loaded existing user-item matrix")
            return True
        else:
            print("[!] No existing matrix, building new one...")
            self.rebuild_matrix()
            return False

    def get_recommendations(
        self,
        user_id: int,
        emotion: Optional[EmotionType] = None,
        limit: int = 10,
        content_weight: float = 0.5
    ) -> Tuple[List[Dict], str]:
        """
        Get hybrid recommendations combining content-based and CF

        Args:
            user_id: User ID
            emotion: Optional emotion filter (content-based)
            limit: Number of recommendations
            content_weight: Weight for content-based (0-1), rest for CF

        Returns:
            (recommendations, algorithm_used)
        """
        recommendations = []
        algorithm = "hybrid"

        # Get content-based recommendations
        content_recs = self._get_content_recommendations(emotion, limit * 2) if emotion else []

        # Get collaborative filtering recommendations
        cf_recs = self._get_cf_recommendations(user_id, limit * 2)

        # Combine with weights
        if emotion and content_recs and cf_recs:
            recommendations = self._combine_recommendations(
                content_recs, cf_recs, content_weight
            )
            algorithm = f"hybrid (content:{content_weight:.1f}, cf:{1-content_weight:.1f})"
        elif content_recs:
            recommendations = content_recs
            algorithm = "content-based"
        elif cf_recs:
            recommendations = cf_recs
            algorithm = "collaborative"
        else:
            # Fallback to random
            recommendations = self._get_random_recommendations(limit)
            algorithm = "random"

        return recommendations[:limit], algorithm

    def _get_content_recommendations(
        self,
        emotion: EmotionType,
        limit: int
    ) -> List[Dict]:
        """Content-based recommendations based on emotion tags"""
        emotion_str = emotion.value.lower()
        matched = []

        for music in data_store.music_db.values():
            emotion_tags = [tag.lower() for tag in music.get('emotion_tags', [])]
            if emotion_str in emotion_tags:
                # Score by number of matching tags
                score = emotion_tags.count(emotion_str)
                matched.append({
                    'music': music,
                    'score': score,
                    'reason': f"matches emotion: {emotion_str}"
                })

        # Sort by score
        matched.sort(key=lambda x: x['score'], reverse=True)
        return matched[:limit]

    def _get_cf_recommendations(
        self,
        user_id: int,
        limit: int
    ) -> List[Dict]:
        """Collaborative filtering recommendations"""
        # Get user's interaction history
        user_items = set()
        for interaction in data_store.interactions_db.values():
            if interaction['user_id'] == user_id:
                user_items.add(interaction['music_id'])

        # Get CF recommendations
        rec_music_ids = self.user_item_matrix.recommend_items(
            user_id, limit, exclude_items=user_items
        )

        recommendations = []
        for music_id in rec_music_ids:
            music = data_store.music_db.get(music_id)
            if music:
                recommendations.append({
                    'music': music,
                    'score': 1.0,
                    'reason': "similar users liked this"
                })

        return recommendations

    def _combine_recommendations(
        self,
        content_recs: List[Dict],
        cf_recs: List[Dict],
        content_weight: float
    ) -> List[Dict]:
        """Combine content-based and CF recommendations"""
        # Normalize scores
        max_content_score = max(r['score'] for r in content_recs) if content_recs else 1
        max_cf_score = max(r['score'] for r in cf_recs) if cf_recs else 1

        # Create score map
        combined = {}

        for rec in content_recs:
            music_id = rec['music']['id']
            normalized_score = rec['score'] / max_content_score if max_content_score > 0 else 0
            combined[music_id] = {
                'music': rec['music'],
                'score': normalized_score * content_weight,
                'reason': rec['reason']
            }

        for rec in cf_recs:
            music_id = rec['music']['id']
            normalized_score = rec['score'] / max_cf_score if max_cf_score > 0 else 0
            if music_id in combined:
                combined[music_id]['score'] += normalized_score * (1 - content_weight)
                combined[music_id]['reason'] += f", {rec['reason']}"
            else:
                combined[music_id] = {
                    'music': rec['music'],
                    'score': normalized_score * (1 - content_weight),
                    'reason': rec['reason']
                }

        # Sort by combined score
        result = list(combined.values())
        result.sort(key=lambda x: x['score'], reverse=True)
        return result

    def _get_random_recommendations(self, limit: int) -> List[Dict]:
        """Fallback random recommendations"""
        import random
        all_music = list(data_store.music_db.values())
        random.shuffle(all_music)
        return [{'music': m, 'score': 1.0, 'reason': 'popular'} for m in all_music[:limit]]


# Global recommender instance
_recommender: Optional[HybridRecommender] = None


def get_recommender() -> HybridRecommender:
    """Get or create global recommender instance"""
    global _recommender
    if _recommender is None:
        _recommender = HybridRecommender()
        _recommender.load_matrix()
    return _recommender


def rebuild_recommender() -> None:
    """Rebuild the recommender matrix"""
    global _recommender
    _recommender = HybridRecommender()
    _recommender.rebuild_matrix()
