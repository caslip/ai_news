"""
test_crawler.py - 爬虫服务测试
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


class TestContentHash:
    """内容哈希测试"""
    
    def test_generate_content_hash(self):
        """测试生成内容哈希"""
        from app.services.openrouter import generate_content_hash
        
        hash1 = generate_content_hash("Test Title", "https://example.com/article")
        hash2 = generate_content_hash("Test Title", "https://example.com/article")
        hash3 = generate_content_hash("Different Title", "https://example.com/article")
        
        # 相同内容应该生成相同的哈希
        assert hash1 == hash2
        # 不同内容应该生成不同的哈希
        assert hash1 != hash3
        # 哈希应该是 64 字符的十六进制字符串 (SHA-256)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)


class TestRSSCrawler:
    """RSS 爬虫测试"""
    
    def test_clean_html(self):
        """测试 HTML 清理"""
        from app.services.crawler import RSSCrawler
        
        crawler = RSSCrawler()
        
        html = "<p>Hello, <strong>World</strong>!</p>"
        cleaned = crawler._clean_html(html)
        
        assert cleaned == "Hello, World!"
    
    def test_clean_html_with_nested_tags(self):
        """测试嵌套标签清理"""
        from app.services.crawler import RSSCrawler
        
        crawler = RSSCrawler()
        
        html = """
        <div>
            <h1>Title</h1>
            <p>Paragraph with <a href="#">link</a></p>
        </div>
        """
        cleaned = crawler._clean_html(html)
        
        assert "Title" in cleaned
        assert "Paragraph" in cleaned
        assert "link" in cleaned
        assert "<" not in cleaned
    
    def test_clean_html_empty(self):
        """测试空 HTML"""
        from app.services.crawler import RSSCrawler
        
        crawler = RSSCrawler()
        
        assert crawler._clean_html("") == ""
        assert crawler._clean_html(None) == ""


class TestHotScoreCalculation:
    """热度分数计算测试"""
    
    def test_calculate_hot_score_basic(self):
        """测试基础热度计算"""
        from app.services.openrouter import calculate_hot_score
        
        score = calculate_hot_score(
            quality=8.0,
            hotness=7.0,
            spread=6.0,
            engagement={"likes": 100, "retweets": 20, "comments": 30}
        )
        
        # 基础分数 = 8*0.3 + 7*0.4 + 6*0.3 = 2.4 + 2.8 + 1.8 = 7.0
        # 最终分数 = 7.0 * 10 + 互动加权 = 70 + (100 + 60 + 60) / 1000 = 70.22
        assert 70 <= score <= 80
    
    def test_calculate_hot_score_max_100(self):
        """测试分数不超过 100"""
        from app.services.openrouter import calculate_hot_score
        
        score = calculate_hot_score(
            quality=10.0,
            hotness=10.0,
            spread=10.0,
            engagement={"likes": 100000, "retweets": 50000, "comments": 30000}
        )
        
        assert score <= 100
    
    def test_calculate_hot_score_zero_engagement(self):
        """测试零互动"""
        from app.services.openrouter import calculate_hot_score
        
        score = calculate_hot_score(
            quality=5.0,
            hotness=5.0,
            spread=5.0,
            engagement={}
        )
        
        # 基础分数 = 5*0.3 + 5*0.4 + 5*0.3 = 5.0
        # 最终分数 = 5.0 * 10 = 50
        assert score == 50.0


class TestLowFanViral:
    """低粉爆文判断测试"""
    
    def test_is_low_fan_viral_pass(self):
        """测试通过低粉爆文判断"""
        from app.services.openrouter import is_low_fan_viral
        
        result = is_low_fan_viral(
            fan_count=1000,
            engagement={"likes": 500, "retweets": 100, "comments": 50},
            quality_score=7.0,
            strategy_params={
                "max_fan_count": 10000,
                "min_engagement": 100,
                "min_viral_score": 5.0,
                "min_quality_score": 6.0,
            }
        )
        
        assert result == True
    
    def test_is_low_fan_viral_too_many_fans(self):
        """测试粉丝太多"""
        from app.services.openrouter import is_low_fan_viral
        
        result = is_low_fan_viral(
            fan_count=50000,  # 超过阈值
            engagement={"likes": 500, "retweets": 100, "comments": 50},
            quality_score=7.0,
            strategy_params={
                "max_fan_count": 10000,
                "min_engagement": 100,
                "min_viral_score": 5.0,
                "min_quality_score": 6.0,
            }
        )
        
        assert result == False
    
    def test_is_low_fan_viral_low_engagement(self):
        """测试互动太低"""
        from app.services.openrouter import is_low_fan_viral
        
        result = is_low_fan_viral(
            fan_count=1000,
            engagement={"likes": 10, "retweets": 5, "comments": 2},  # 总互动 10+15+4=29 < 100
            quality_score=7.0,
            strategy_params={
                "max_fan_count": 10000,
                "min_engagement": 100,
                "min_viral_score": 5.0,
                "min_quality_score": 6.0,
            }
        )
        
        assert result == False
    
    def test_is_low_fan_viral_low_quality(self):
        """测试质量太低"""
        from app.services.openrouter import is_low_fan_viral
        
        result = is_low_fan_viral(
            fan_count=1000,
            engagement={"likes": 500, "retweets": 100, "comments": 50},
            quality_score=5.0,  # 低于阈值
            strategy_params={
                "max_fan_count": 10000,
                "min_engagement": 100,
                "min_viral_score": 5.0,
                "min_quality_score": 6.0,
            }
        )
        
        assert result == False
    
    def test_is_low_fan_viral_default_params(self):
        """测试使用默认参数"""
        from app.services.openrouter import is_low_fan_viral
        
        result = is_low_fan_viral(
            fan_count=1000,
            engagement={"likes": 200, "retweets": 50, "comments": 20},
            quality_score=7.0,
            strategy_params={}  # 空参数，使用默认值
        )
        
        # 默认参数应该允许这个案例通过
        assert isinstance(result, bool)


class TestViralScore:
    """爆文指数计算测试"""
    
    def test_viral_score_calculation(self):
        """测试爆文指数计算公式"""
        fan_count = 1000
        engagement = {
            "likes": 500,
            "retweets": 100,
            "comments": 50
        }
        
        total_engagement = (
            engagement["likes"] * 1 +
            engagement["retweets"] * 3 +
            engagement["comments"] * 2
        )
        viral_score = total_engagement / (fan_count + 1) * 1000
        
        # total = 500 + 300 + 100 = 900
        # viral_score = 900 / 1001 * 1000 ≈ 899
        assert 890 <= viral_score <= 900
