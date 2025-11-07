"""
内容分类器
基于关键词规则的简单分类
"""

from typing import List
import re


class ContentClassifier:
    """内容分类器"""
    
    # 分类关键词库
    KEYWORDS = {
        '工作': [
            '会议', '项目', '任务', '客户', '业务', '方案', '汇报', '计划',
            '需求', '产品', '设计', '开发', '测试', '上线', '运营', '销售',
            '合同', '预算', '绩效', '团队', '领导', '同事', '部门', '公司',
            '办公', '邮件', '文档', '报告', 'PPT', '数据', '分析', '策略'
        ],
        '生活': [
            '吃饭', '美食', '做饭', '菜', '餐厅', '超市', '购物', '买',
            '家', '打扫', '洗衣', '收拾', '装修', '家具', '家电',
            '运动', '健身', '跑步', '游泳', '爬山', '散步', '锻炼',
            '休息', '睡觉', '放松', '娱乐', '电影', '音乐', '旅游',
            '朋友', '家人', '父母', '孩子', '宠物', '约会', '聚会'
        ],
        '学习': [
            '学习', '课程', '教程', '书', '阅读', '笔记', '复习', '预习',
            '考试', '考证', '培训', '讲座', '研究', '论文', '资料',
            '知识', '技能', '专业', '学校', '老师', '同学', '作业',
            '英语', '编程', '算法', '数据库', '框架', '工具', '方法'
        ],
        '创意': [
            '想法', '灵感', '创意', '点子', '主意', '思考', '构思',
            '设计', '创作', '写作', '画画', '摄影', '视频', '音乐',
            '发明', '改进', '优化', '创新', '尝试', '实验', '探索',
            '梦想', '计划', '未来', '目标', '愿望', '希望', '憧憬'
        ]
    }
    
    @classmethod
    def classify(cls, text: str) -> str:
        """
        根据文本内容分类
        
        Args:
            text: 要分类的文本
        
        Returns:
            分类标签：工作/生活/学习/创意
        """
        if not text:
            return '生活'  # 默认分类
        
        # 统计各分类的关键词匹配数
        scores = {
            '工作': 0,
            '生活': 0,
            '学习': 0,
            '创意': 0
        }
        
        # 转换为小写便于匹配
        text_lower = text.lower()
        
        # 统计每个分类的关键词出现次数
        for category, keywords in cls.KEYWORDS.items():
            for keyword in keywords:
                # 统计关键词出现次数（权重）
                count = text_lower.count(keyword.lower())
                scores[category] += count
        
        # 如果有关键词匹配，返回得分最高的分类
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # 如果没有任何匹配，返回默认分类
        return '生活'
    
    @classmethod
    def extract_keywords(cls, text: str, summary: str = None, key_sentences: List[str] = None) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 转写文本
            summary: 摘要（可选）
            key_sentences: 关键句列表（可选）
        
        Returns:
            关键词列表（3-5个）
        """
        keywords = []
        
        # 优先从通义听悟的关键句提取
        if key_sentences:
            for sentence in key_sentences[:3]:
                # 提取短句作为关键词
                words = sentence.split('，')
                if words:
                    keywords.append(words[0][:10])  # 限制长度
        
        # 如果关键词不够，从摘要提取
        if len(keywords) < 3 and summary:
            words = re.findall(r'[\u4e00-\u9fa5]{2,6}', summary)
            keywords.extend(words[:3])
        
        # 如果还不够，从原文提取高频词
        if len(keywords) < 3:
            words = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
            # 简单统计词频
            word_count = {}
            for word in words:
                if len(word) >= 2:  # 至少2个字
                    word_count[word] = word_count.get(word, 0) + 1
            
            # 取出现频率最高的词
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            keywords.extend([w[0] for w in sorted_words[:5-len(keywords)]])
        
        # 去重并限制数量
        unique_keywords = []
        for kw in keywords:
            if kw not in unique_keywords and len(kw) >= 2:
                unique_keywords.append(kw)
        
        return unique_keywords[:5]  # 最多5个


# 创建全局实例
classifier = ContentClassifier()

