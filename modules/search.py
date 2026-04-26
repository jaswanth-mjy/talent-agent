import json
import numpy as np
from llm.embeddings import candidate_to_text, embed_text, jd_to_text

try:
    import faiss  # type: ignore[import-not-found]
except ImportError:
    faiss = None

class CandidateSearch:
    def __init__(
        self,
        data_path="data/candidates.json",
        embedding_model="nomic-embed-text",
        strict_embeddings=False,
    ):
        with open(data_path, "r", encoding="utf-8") as f:
            self.candidates = json.load(f)

        self.embedding_model = embedding_model
        self.strict_embeddings = strict_embeddings
        self.index = None
        self.vectors = np.array([], dtype="float32")
        self.vector_to_candidate_idx = []
        self._build_index()

    def _build_index(self):
        if not self.candidates:
            return

        vectors = []
        target_dim = None

        for candidate_idx, c in enumerate(self.candidates):
            text = candidate_to_text(c)
            vec = embed_text(
                text,
                model=self.embedding_model,
                strict=self.strict_embeddings,
            )
            if vec.size == 0:
                continue
            if target_dim is None:
                target_dim = int(vec.size)
            vec = self._align_vector_dim(vec, target_dim)
            vectors.append(vec)
            self.vector_to_candidate_idx.append(candidate_idx)

        if not vectors:
            return

        self.vectors = np.array(vectors).astype("float32")

        if faiss is not None:
            dim = self.vectors.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(self.vectors)
        else:
            self.index = None

    @staticmethod
    def _align_vector_dim(vec, target_dim):
        if target_dim is None:
            return vec

        current_dim = int(vec.size)
        if current_dim == target_dim:
            return vec
        if current_dim > target_dim:
            return vec[:target_dim]

        padded = np.zeros(target_dim, dtype="float32")
        padded[:current_dim] = vec
        return padded

    def search(self, jd_data, top_k=3):
        if self.vectors.size == 0:
            return []

        jd_text = jd_to_text(jd_data)
        query_vector = embed_text(
            jd_text,
            model=self.embedding_model,
            strict=self.strict_embeddings,
        )
        if query_vector.size == 0:
            return []
        query_vector = self._align_vector_dim(query_vector, self.vectors.shape[1])

        query_vec = np.array([query_vector]).astype("float32")
        safe_top_k = max(1, min(top_k, len(self.vector_to_candidate_idx)))

        if self.index is not None:
            scores, indices = self.index.search(query_vec, safe_top_k)
            top_indices = indices[0]
            top_scores = scores[0]
        else:
            all_scores = np.dot(self.vectors, query_vec[0])
            top_indices = np.argsort(all_scores)[::-1][:safe_top_k]
            top_scores = all_scores[top_indices]

        results = []
        for idx, score in zip(top_indices, top_scores):
            if idx < 0 or idx >= len(self.vector_to_candidate_idx):
                continue
            candidate_index = self.vector_to_candidate_idx[idx]
            candidate = dict(self.candidates[candidate_index])
            normalized_score = (float(score) + 1.0) / 2.0
            candidate["similarity_score"] = round(max(0.0, min(1.0, normalized_score)), 4)
            results.append(candidate)

        return results