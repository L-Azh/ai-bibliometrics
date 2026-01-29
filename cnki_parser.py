"""
cnki_parser.py
知网EndNote格式解析器 - 支持 %+ 机构字段
"""

import re
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict
import os


@dataclass
class CnkiPaper:
    """知网文献数据结构"""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    institution: str = ""
    all_institutions: List[str] = field(default_factory=list)
    journal: str = ""
    year: int = 0
    volume: str = ""
    issue: str = ""
    pages: str = ""
    keywords: List[str] = field(default_factory=list)
    abstract: str = ""
    doi: str = ""
    url: str = ""
    issn: str = ""
    cn_code: str = ""
    citations: int = 0
    downloads: int = 0


class CnkiEndNoteParser:
    """知网EndNote解析器"""
    
    def parse(self, file_path: str) -> List[CnkiPaper]:
        """解析.enw或.txt文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割记录（以%0开头）
        records = re.split(r'(?=%0\s)', content)
        papers = []
        
        for record in records:
            record = record.strip()
            if not record or len(record) < 50:
                continue
            
            paper = self._parse_record(record)
            if paper.title:
                papers.append(paper)
        
        print(f"✅ 成功解析 {len(papers)} 篇文献")
        return papers
    
    def _parse_record(self, record: str) -> CnkiPaper:
        """解析单条记录"""
        paper = CnkiPaper()
        lines = record.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('%'):
                continue
            
            if len(line) < 2:
                continue
            
            marker = line[:2]
            value = line[2:].strip()
            
            # 字段解析
            if marker == '%T':
                paper.title = value
            elif marker == '%A':
                if value:
                    paper.authors.append(value)
            elif marker == '%+':
                if value:
                    institutions = [i.strip() for i in value.split(';') if i.strip()]
                    paper.all_institutions = institutions
                    paper.institution = institutions[0] if institutions else ""
            elif marker == '%J':
                paper.journal = value
            elif marker == '%D':
                year_match = re.search(r'(19|20)\d{2}', value)
                if year_match:
                    paper.year = int(year_match.group())
            elif marker == '%V':
                paper.volume = value
            elif marker == '%N':
                paper.issue = value
            elif marker == '%P':
                paper.pages = value
            elif marker == '%K':
                if value:
                    keywords = re.split(r'[;；,，]', value)
                    paper.keywords = [k.strip() for k in keywords if k.strip()]
            elif marker == '%X':
                paper.abstract = value
            elif marker == '%R':
                paper.doi = value
            elif marker == '%@':
                paper.issn = value
            elif marker == '%L':
                paper.cn_code = value
            elif marker == '%U':
                paper.url = value
            elif marker == '%W':
                paper.cnki_id = value
            elif marker == '%Z':
                cite_match = re.search(r'被引[:：]?\s*(\d+)', value)
                if cite_match:
                    paper.citations = int(cite_match.group(1))
                download_match = re.search(r'下载[:：]?\s*(\d+)', value)
                if download_match:
                    paper.downloads = int(download_match.group(1))
        
        return paper
    
    def to_dataframe(self, papers: List[CnkiPaper]) -> pd.DataFrame:
        """转DataFrame"""
        data = []
        for p in papers:
            data.append({
                'title': p.title,
                'authors': '; '.join(p.authors),
                'institution': p.institution,
                'all_institutions': '; '.join(p.all_institutions),
                'journal': p.journal,
                'year': p.year,
                'volume': p.volume,
                'issue': p.issue,
                'pages': p.pages,
                'keywords': '; '.join(p.keywords),
                'abstract': p.abstract,
                'doi': p.doi,
                'issn': p.issn,
                'citations': p.citations,
                'downloads': p.downloads,
            })
        return pd.DataFrame(data)


def quick_parse(file_path: str):
    """快速解析入口"""
    parser = CnkiEndNoteParser()
    papers = parser.parse(file_path)
    df = parser.to_dataframe(papers)
    
    # 基础统计
    stats = {
        'total': len(papers),
        'years': sorted(set(p.year for p in papers if p.year > 2000)),
        'authors': len(set(a for p in papers for a in p.authors)),
        'journals': len(set(p.journal for p in papers if p.journal)),
        'institutions': len(set(p.institution for p in papers if p.institution)),
    }
    
    return papers, df, stats


# 测试代码
if __name__ == "__main__":
    # 创建测试数据
    test_data = """%0 Journal Article
%T 企业数字化技术对审计质量的影响机制研究——基于新质生产力背景
%A 汪立元
%A 彭静文
%+ 上海政法学院经济管理学院;辽宁财贸学院工商管理学院;上海开放大学金山分校;
%J 会计之友
%D 2025
%N S2
%K 新质生产力;数字化技术;审计质量
%X 在新质生产力加快形成的背景下，企业数字化转型已成为提升审计质量的重要途径...
%P 33-41
%@ 1004-5937
%L 14-1063/F
%U https://link.cnki.net/urlid/14.1063.F.20251215.1446.008
%W CNKI

%0 Journal Article
%T 基于机器学习的财务风险预警研究
%A 张三
%A 李四
%+ 清华大学经济管理学院;北京大学光华管理学院;
%J 管理世界
%D 2024
%N 5
%K 机器学习;财务风险;预警模型
%X 本文研究了机器学习在企业财务风险预警中的应用...
%P 120-135
%@ 1002-5502
%W CNKI
"""
    
    # 保存测试文件
    with open("test.enw", "w", encoding="utf-8") as f:
        f.write(test_data)
    
    print("🧪 测试解析器...")
    papers, df, stats = quick_parse("test.enw")
    
    print(f"\n📊 统计: {stats}")
    print(f"\n📄 第一篇文献:")
    print(f"  标题: {papers[0].title}")
    print(f"  作者: {papers[0].authors}")
    print(f"  机构: {papers[0].all_institutions}")
    print(f"  关键词: {papers[0].keywords}")
    
    # 保存Excel
    df.to_excel("test_output.xlsx", index=False)
    print(f"\n💾 已保存 test_output.xlsx")