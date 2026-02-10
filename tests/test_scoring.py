"""Unit tests for scoring components."""

import pytest
from phaethon.core.schemas import (
    ContentItem,
    ContentType,
    UserProfile,
    ValueProfile,
)
from phaethon.scoring.content_features import ContentFeatureExtractor
from phaethon.scoring.scorer import ContentScorer


class TestContentFeatureExtractor:
    """Test feature extraction."""
    
    def setup_method(self):
        """Setup for each test."""
        self.extractor = ContentFeatureExtractor()
    
    def test_extract_features_from_article(self):
        """Test extracting features from an article."""
        content = ContentItem(
            content_id="article-1",
            source="https://arxiv.org/paper",
            title="Deep Learning and Neural Networks: A Comprehensive Guide",
            content_type=ContentType.ARTICLE,
            domain="arxiv.org",
        )
        
        features = self.extractor.extract_features(content)
        
        assert features.title == "Deep Learning and Neural Networks: A Comprehensive Guide"
        assert "technology" in features.main_topics
        assert features.tone == "educational"
    
    def test_detect_clickbait(self):
        """Test clickbait detection."""
        content = ContentItem(
            content_id="clickbait-1",
            source="https://buzzfeed.com",
            title="You won't BELIEVE what happened next!!!",
            content_type=ContentType.ARTICLE,
            domain="buzzfeed.com",
        )
        
        features = self.extractor.extract_features(content)
        
        assert features.is_clickbait
    
    def test_domain_reputation(self):
        """Test domain reputation scoring."""
        # High reputation
        high_rep = self.extractor._get_domain_reputation("arxiv.org")
        assert high_rep > 0.9
        
        # Low reputation
        low_rep = self.extractor._get_domain_reputation("twitter.com")
        assert low_rep < 0.5


class TestContentScorer:
    """Test content scoring."""
    
    def setup_method(self):
        """Setup for each test."""
        self.scorer = ContentScorer()
    
    def test_score_learning_content(self):
        """Test scoring learning-aligned content."""
        content = ContentItem(
            content_id="article-1",
            source="https://arxiv.org/paper",
            title="Machine Learning Research Paper",
            content_type=ContentType.ARTICLE,
            domain="arxiv.org",
        )
        
        profile = UserProfile(
            user_id="user-1",
            values=ValueProfile(
                values={
                    "productivity": {
                        "learning": 0.95,
                        "focus": 0.90,
                    }
                },
                confidence=0.85,
            )
        )
        
        result = self.scorer.score_content(content, profile)
        
        assert result.alignment_score > 0.6
        assert result.confidence > 0.5
    
    def test_score_distraction_content(self):
        """Test scoring distraction-heavy content."""
        content = ContentItem(
            content_id="post-1",
            source="https://twitter.com/post",
            title="Check out this SHOCKING celebrity news!!!",
            content_type=ContentType.SOCIAL_POST,
            domain="twitter.com",
        )
        
        profile = UserProfile(
            user_id="user-1",
            values=ValueProfile(
                values={
                    "productivity": {
                        "focus": 0.95,
                    }
                },
                confidence=0.85,
            )
        )
        
        result = self.scorer.score_content(content, profile)
        
        # Should have low alignment for someone who values focus
        assert result.alignment_score < 0.6


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
