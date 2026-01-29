"""
用真实数据测试
"""

from cnki_parser import quick_parse
from network_builder import NetworkBuilder
from visualizer import Visualizer

# ========== 修改这里：填入你的文件名 ==========
FILE_NAME = "大数据审计.enw"  # ← 改成真实的，如 "审计研究.enw"
# =============================================

print(f"📂 正在分析: {FILE_NAME}")
print("=" * 60)

# 1. 解析数据
papers, df, stats = quick_parse(FILE_NAME)

print(f"\n📊 数据概览:")
print(f"  文献总数: {stats['total']} 篇")
print(f"  时间范围: {stats['years'][0] if stats['years'] else 'N/A'} - {stats['years'][-1] if stats['years'] else 'N/A'}")
print(f"  独立作者: {stats['authors']} 人")
print(f"  来源期刊: {stats['journals']} 种")
print(f"  涉及机构: {stats['institutions']} 个")

# 2. 显示前5篇文献
print(f"\n📄 前5篇文献:")
for i, p in enumerate(papers[:5], 1):
    print(f"\n  {i}. {p.title[:50]}...")
    print(f"     作者: {', '.join(p.authors[:3])}")
    print(f"     年份: {p.year} | 期刊: {p.journal[:20]}")

# 3. 构建网络
print(f"\n🕸️ 构建网络...")
builder = NetworkBuilder(papers)
coauth = builder.build_coauthorship(top_n=50)
inst = builder.build_institution()
keyword = builder.build_keywords(min_freq=2)

# 4. 生成可视化
print(f"\n🎨 生成图谱...")
output_dir = f"output_{FILE_NAME.replace('.enw', '')}"
viz = Visualizer(output_dir)

viz.plot_coauthorship(coauth)
viz.plot_institution(inst)
viz.plot_keywords(keyword)
viz.plot_trend(papers)
viz.plot_wordcloud(papers)
viz.plot_top_authors(papers, top_n=15)

# 5. 保存Excel
excel_path = f"{output_dir}/data.xlsx"
df.to_excel(excel_path, index=False)

print(f"\n" + "=" * 60)
print(f"✅ 分析完成！")
print(f"📁 结果保存在: {output_dir}/")
print(f"💾 Excel数据: {excel_path}")