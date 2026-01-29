"""
visualizer.py
可视化模块 - 生成高清 PNG 图谱
"""

import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager
import networkx as nx
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import os
import numpy as np
import community as community_louvain

# 全局强制设置
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
matplotlib.rcParams['axes.unicode_minus'] = False

# WordCloud 字体
FONT_PATH = 'C:/Windows/Fonts/simhei.ttf'


class Visualizer:
    """可视化生成器"""
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _new_figure(self, figsize=(14, 12)):
        """创建新图，确保字体设置生效"""
        plt.figure(figsize=figsize, dpi=300)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_coauthorship(self, G, filename="01_coauthorship.png"):
        """作者合作网络"""
        if len(G.nodes()) == 0:
            print("⚠️ 合作网络为空")
            return None
        
        self._new_figure((14, 12))
        
        pos = nx.spring_layout(G, k=3/np.sqrt(len(G.nodes())), iterations=50, seed=42)
        node_sizes = [G.nodes[n].get('paper_count', 1) * 150 for n in G.nodes()]
        node_colors = [G.nodes[n].get('citations', 0) for n in G.nodes()]
        
        nx.draw_networkx_edges(G, pos, alpha=0.4, width=1)
        nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                                      node_color=node_colors, cmap=plt.cm.viridis,
                                      alpha=0.9, edgecolors='black')
        
        plt.colorbar(nodes, shrink=0.5, label='被引次数')
        
        important = [n for n in G.nodes() if G.nodes[n].get('paper_count', 0) > 1]
        labels = {n: n[:10] for n in important}
        nx.draw_networkx_labels(G, pos, labels, font_size=9)
        
        plt.title("作者合作网络", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ {path}")
        return path
    
    def plot_institution(self, G, filename="02_institution.png"):
        """机构合作网络"""
        if len(G.nodes()) == 0:
            print("⚠️ 机构网络为空")
            return None
        
        self._new_figure((14, 12))
        
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        node_sizes = [G.nodes[n].get('paper_count', 1) * 300 for n in G.nodes()]
        
        nx.draw_networkx_edges(G, pos, alpha=0.4, width=1.5)
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                              node_color='lightblue', alpha=0.9,
                              edgecolors='darkblue', linewidths=2)
        
        labels = {n: n[:15] for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title("机构合作网络", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ {path}")
        return path
    
    def plot_keywords(self, G, filename="03_keywords.png"):
        """关键词共现网络"""
        if len(G.nodes()) == 0:
            print("⚠️ 关键词网络为空")
            return None
        
        self._new_figure((14, 14))
        
        communities = community_louvain.best_partition(G)
        pos = nx.spring_layout(G, k=2.5/np.sqrt(len(G.nodes())), iterations=100, seed=42)
        
        unique_coms = list(set(communities.values()))
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_coms)))
        node_colors = [colors[communities[n]] for n in G.nodes()]
        node_sizes = [G.nodes[n].get('freq', 1) * 80 for n in G.nodes()]
        
        nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5)
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                              node_color=node_colors, alpha=0.85,
                              edgecolors='black', linewidths=1.5)
        
        labels = {n: n for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
        
        plt.title("关键词共现网络", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ {path}")
        return path
    
    def plot_trend(self, papers, filename="04_trend.png"):
        """年度发文趋势"""
        year_data = {}
        for p in papers:
            if p.year > 2000:
                year_data[p.year] = year_data.get(p.year, 0) + 1
        
        if not year_data:
            print("⚠️ 无年份数据")
            return None
        
        years = sorted(year_data.keys())
        counts = [year_data[y] for y in years]
        
        self._new_figure((12, 6))
        plt.plot(years, counts, marker='o', linewidth=2.5, markersize=10, color='steelblue')
        plt.fill_between(years, counts, alpha=0.3, color='steelblue')
        
        for x, y in zip(years, counts):
            plt.annotate(str(y), (x, y), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')
        
        plt.xlabel('年份', fontsize=13, fontweight='bold')
        plt.ylabel('发文量（篇）', fontsize=13, fontweight='bold')
        plt.title('年度发文趋势', fontsize=16, fontweight='bold', pad=20)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ {path}")
        return path
    
    def plot_wordcloud(self, papers, filename="05_wordcloud.png"):
        """关键词词云 - 关键修复：传入字体路径"""
        keywords = [kw for p in papers for kw in p.keywords]
        if not keywords:
            print("⚠️ 无关键词数据")
            return None
        
        text = ' '.join(keywords)
        
        # 关键：传入 font_path 参数
        wc = WordCloud(
            width=1600,
            height=800,
            background_color='white',
            font_path=FONT_PATH,  # ← 关键修复
            max_words=100,
            colormap='viridis',
            prefer_horizontal=0.7
        ).generate(text)
        
        self._new_figure((16, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title('高频关键词词云', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ {path}")
        return path
    
    def plot_top_authors(self, papers, top_n=10, filename="06_top_authors.png"):
        """高产作者排名"""
        counter = Counter()
        for p in papers:
            counter.update(p.authors)
        
        top = counter.most_common(top_n)
        if not top:
            print("⚠️ 无作者数据")
            return None
        
        items, counts = zip(*top)
        
        self._new_figure((10, 8))
        colors = plt.cm.Spectral(np.linspace(0, 1, len(items)))
        bars = plt.barh(range(len(items)), counts, color=colors)
        
        plt.yticks(range(len(items)), items, fontsize=11)
        plt.xlabel('论文数量', fontsize=12, fontweight='bold')
        plt.title(f'高产作者Top {top_n}', fontsize=16, fontweight='bold', pad=20)
        plt.gca().invert_yaxis()
        
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2,
                    f' {int(width)}', va='center', fontsize=10)
        
        plt.tight_layout()
        
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ {path}")
        return path


# 测试代码
if __name__ == "__main__":
    from cnki_parser import quick_parse
    from network_builder import NetworkBuilder
    
    print("🧪 测试可视化模块...")
    papers, df, stats = quick_parse("test.enw")
    
    builder = NetworkBuilder(papers)
    coauth = builder.build_coauthorship(top_n=10)
    inst = builder.build_institution()
    keyword = builder.build_keywords(min_freq=1)
    
    viz = Visualizer(output_dir="test_output")
    
    print("\n🎨 生成可视化...")
    viz.plot_coauthorship(coauth)
    viz.plot_institution(inst)
    viz.plot_keywords(keyword)
    viz.plot_trend(papers)
    viz.plot_wordcloud(papers)
    viz.plot_top_authors(papers, top_n=10)
    
    print(f"\n✅ 所有图谱保存在: test_output/")