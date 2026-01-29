"""
ai_modules.py
DeepSeek AI分析模块 - 使用官方 OpenAI SDK
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from collections import Counter
from openai import OpenAI

load_dotenv()


@dataclass
class AIResult:
    """AI分析结果"""
    content: str
    cost_rmb: float = 0.0


class DeepSeekAnalyzer:
    """DeepSeek AI分析器 - 官方SDK版本"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        
        if not api_key:
            raise ValueError("未设置 DEEPSEEK_API_KEY")
        
        # 官方推荐方式：使用 OpenAI SDK
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        self.model = "deepseek-chat"
        self.price_per_1k = 0.001  # 约0.001元/1K tokens
    
    def _call(self, prompt: str, system: str = "") -> AIResult:
        """调用 DeepSeek API"""
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                stream=False
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            cost = (tokens / 1000) * self.price_per_1k
            
            return AIResult(content=content, cost_rmb=cost)
            
        except Exception as e:
            raise Exception(f"API调用失败: {e}")
    
    def analyze_themes(self, keywords: List[str], titles: List[str]) -> AIResult:
        """AI主题分析"""
        keyword_freq = Counter(keywords).most_common(20)
        
        prompt = f"""作为文献计量学专家，分析以下研究主题：

高频关键词：{keyword_freq}
代表性标题（前15个）：{titles[:15]}

请完成：
1. 归纳3-5个核心研究主题（给出主题名称）
2. 分析研究热点和发展趋势
3. 识别跨学科特征
4. 指出研究空白和机会

用中文回答，300-500字，学术化表达。"""

        return self._call(prompt, "你是科学知识图谱和文献计量学专家")
    
    def generate_summary(self, stats: Dict, top_papers: List[Dict]) -> AIResult:
        """生成文献综述"""
        prompt = f"""基于以下数据撰写文献综述摘要（300-400字）：

数据概览：
- 文献总数：{stats.get('total')}篇
- 时间跨度：{stats.get('years')[0] if stats.get('years') else 'N/A'} - {stats.get('years')[-1] if stats.get('years') else 'N/A'}
- 核心作者：{stats.get('authors')}人
- 主要期刊：{stats.get('journals')}种

高影响力文献：
{[p['title'][:50] for p in top_papers[:5]]}

要求：
1. 总结该领域的研究特征和主要方向
2. 指出研究演进脉络
3. 分析当前热点和未来趋势
4. 学术化中文表达"""

        return self._call(prompt, "你是学术写作专家，擅长撰写高质量文献综述")