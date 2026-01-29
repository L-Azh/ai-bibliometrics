"""
network_builder.py
网络构建模块 - 合作网络、机构网络、关键词网络
"""

import networkx as nx
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import community as community_louvain
from typing import List
from cnki_parser import CnkiPaper


class NetworkBuilder:
    """网络构建器"""
    
    def __init__(self, papers: List[CnkiPaper]):
        self.papers = papers
    
    def build_coauthorship(self, top_n=50):
        """作者合作网络"""
        G = nx.Graph()
        author_papers = defaultdict(list)
        
        # 统计每位作者的论文
        for paper in self.papers:
            for author in paper.authors:
                if author:
                    author_papers[author].append(paper)
        
        # 只保留高产作者 Top N
        top_authors = sorted(author_papers.items(), 
                           key=lambda x: len(x[1]), 
                           reverse=True)[:top_n]
        top_names = {name for name, _ in top_authors}
        
        # 构建合作边
        for paper in self.papers:
            authors = [a for a in paper.authors if a in top_names]
            for i, a1 in enumerate(authors):
                for a2 in authors[i+1:]:
                    if G.has_edge(a1, a2):
                        G[a1][a2]['weight'] += 1
                    else:
                        G.add_edge(a1, a2, weight=1)
        
        # 添加节点属性
        for node in G.nodes():
            G.nodes[node]['paper_count'] = len(author_papers[node])
            G.nodes[node]['citations'] = sum(p.citations for p in author_papers[node])
        
        print(f"✅ 合作网络: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
        return G
    
    def build_institution(self):
        """机构合作网络（支持多机构 %+）"""
        G = nx.Graph()
        
        for paper in self.papers:
            institutions = paper.all_institutions
            if len(institutions) < 2:
                continue
            
            # 为所有机构对添加边
            for i, inst1 in enumerate(institutions):
                for inst2 in institutions[i+1:]:
                    if G.has_edge(inst1, inst2):
                        G[inst1][inst2]['weight'] += 1
                    else:
                        G.add_edge(inst1, inst2, weight=1)
        
        # 添加节点属性
        for node in G.nodes():
            G.nodes[node]['paper_count'] = sum(
                1 for p in self.papers if node in p.all_institutions
            )
        
        print(f"✅ 机构网络: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
        return G
    
    def build_keywords(self, min_freq=2):
        """关键词共现网络"""
        G = nx.Graph()
        
        # 统计词频
        keyword_freq = Counter()
        for paper in self.papers:
            for kw in paper.keywords:
                if kw:
                    keyword_freq[kw] += 1
        
        # 只保留高频词
        valid_keywords = {kw for kw, freq in keyword_freq.items() 
                         if freq >= min_freq}
        
        # 统计共现
        cooccurrence = Counter()
        for paper in self.papers:
            keywords = [kw for kw in paper.keywords if kw in valid_keywords]
            for i, kw1 in enumerate(keywords):
                for kw2 in keywords[i+1:]:
                    if kw1 != kw2:
                        pair = tuple(sorted([kw1, kw2]))
                        cooccurrence[pair] += 1
        
        # 构建网络（只保留共现≥2次）
        for (kw1, kw2), weight in cooccurrence.items():
            if weight >= 2:
                G.add_edge(kw1, kw2, weight=weight)
                G.nodes[kw1]['freq'] = keyword_freq[kw1]
                G.nodes[kw2]['freq'] = keyword_freq[kw2]
        
        print(f"✅ 关键词网络: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
        return G


# 测试代码
if __name__ == "__main__":
    from cnki_parser import quick_parse
    
    print("🧪 测试网络构建...")
    papers, df, stats = quick_parse("test.enw")
    
    builder = NetworkBuilder(papers)
    
    # 构建三种网络
    coauth = builder.build_coauthorship(top_n=10)
    inst = builder.build_institution()
    keyword = builder.build_keywords(min_freq=1)
    
    print(f"\n📊 网络统计:")
    print(f"  合作网络密度: {nx.density(coauth):.3f}")
    print(f"  机构网络密度: {nx.density(inst):.3f}")
    print(f"  关键词网络密度: {nx.density(keyword):.3f}")