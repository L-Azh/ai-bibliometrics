"""
app.py
Streamlit 网页版 - AI增强文献计量分析系统
用法: streamlit run app.py
"""

import streamlit as st
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import base64
from io import BytesIO

# 设置页面配置（必须在最前面）
st.set_page_config(
    page_title="AI文献计量分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入自定义模块
from cnki_parser import quick_parse
from network_builder import NetworkBuilder
from visualizer import Visualizer
from ai_modules import DeepSeekAnalyzer

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)


def get_image_download_link(img_path, text):
    """生成图片下载链接"""
    with open(img_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="{os.path.basename(img_path)}" class="btn btn-primary">{text}</a>'
    return href


def main():
    # 页面标题
    st.markdown('<div class="main-header">📊 AI增强文献计量分析系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by DeepSeek + Python + 知网数据</div>', unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")
        
        # API密钥设置
        api_key = st.text_input("DeepSeek API密钥", 
                               value=os.getenv("DEEPSEEK_API_KEY", ""),
                               type="password",
                               help="留空则跳过AI分析")
        
        if api_key:
            os.environ["DEEPSEEK_API_KEY"] = api_key
        
        st.divider()
        
        # 分析参数
        st.subheader("分析参数")
        top_n_authors = st.slider("显示Top N作者", 5, 30, 15)
        min_keyword_freq = st.slider("关键词最小频次", 1, 5, 2)
        
        st.divider()
        
        st.info("""
        **使用步骤：**
        1. 上传知网导出的.enw文件
        2. 点击"开始分析"
        3. 查看结果并下载
        """)
    
    # 主界面：文件上传
    st.header("📤 上传数据")
    
    uploaded_file = st.file_uploader(
        "选择知网EndNote格式文件（.enw或.txt）",
        type=["enw", "txt"],
        help="从知网导出时选择EndNote格式"
    )
    
    if uploaded_file is not None:
        # 保存上传的文件
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ 文件上传成功: {uploaded_file.name}")
        
        # 分析按钮
        if st.button("🚀 开始分析", type="primary", use_container_width=True):
            with st.spinner("正在分析，请稍候..."):
                run_analysis(file_path, top_n_authors, min_keyword_freq)


def run_analysis(file_path, top_n_authors, min_keyword_freq):
    """执行分析流程"""
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 步骤1: 解析数据
    status_text.text("步骤 1/5: 解析知网数据...")
    papers, df, stats = quick_parse(file_path)
    progress_bar.progress(20)
    
    if stats['total'] == 0:
        st.error("❌ 未解析到有效文献，请检查文件格式")
        return
    
    # 显示数据概览
    st.header("📊 数据概览")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total']}</div>
            <div class="metric-label">文献总数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        years_str = f"{stats['years'][0]}-{stats['years'][-1]}" if stats['years'] else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{years_str}</div>
            <div class="metric-label">时间跨度</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['authors']}</div>
            <div class="metric-label">独立作者</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['journals']}</div>
            <div class="metric-label">来源期刊</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['institutions']}</div>
            <div class="metric-label">涉及机构</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 步骤2: 构建网络
    status_text.text("步骤 2/5: 构建计量网络...")
    builder = NetworkBuilder(papers)
    coauth_net = builder.build_coauthorship(top_n=50)
    inst_net = builder.build_institution()
    keyword_net = builder.build_keywords(min_freq=min_keyword_freq)
    progress_bar.progress(40)
    
    # 步骤3: 生成可视化
    status_text.text("步骤 3/5: 生成可视化图谱...")
    
    # 创建输出目录
    output_dir = f"output_streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    viz = Visualizer(output_dir)
    
    # 生成图表
    viz.plot_coauthorship(coauth_net, "01_作者合作网络.png")
    viz.plot_institution(inst_net, "02_机构合作网络.png")
    viz.plot_keywords(keyword_net, "03_关键词共现网络.png")
    viz.plot_trend(papers, "04_年度发文趋势.png")
    viz.plot_wordcloud(papers, "05_关键词词云.png")
    viz.plot_top_authors(papers, top_n=top_n_authors, filename="06_高产作者排名.png")
    
    progress_bar.progress(60)
    
    # 保存Excel
    excel_path = os.path.join(output_dir, "00_原始数据.xlsx")
    df.to_excel(excel_path, index=False)
    
    # 步骤4: AI分析
    ai_report = None
    api_key = st.text_input("DeepSeek API密钥", type="password")
    
    if api_key and len(papers) >= 5:
        status_text.text("步骤 4/5: DeepSeek AI智能分析...")
        try:
            analyzer = DeepSeekAnalyzer(api_key)
            
            # AI主题分析
            all_keywords = [kw for p in papers for kw in p.keywords]
            all_titles = [p.title for p in papers]
            theme_result = analyzer.analyze_themes(all_keywords, all_titles)
            
            # AI综述
            top_papers_data = [{
                'title': p.title,
                'authors': p.authors,
                'year': p.year,
                'citations': p.citations
            } for p in sorted(papers, key=lambda x: x.citations, reverse=True)[:10]]
            
            review_result = analyzer.generate_summary(stats, top_papers_data)
            
            # 组合报告
            ai_report = f"""# 🤖 DeepSeek AI 智能分析报告

## 一、AI主题分析

{theme_result.content}

## 二、研究综述

{review_result.content}

---
*分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # 保存
            report_path = os.path.join(output_dir, "07_AI智能分析报告.md")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(ai_report)
            
            st.success(f"✅ AI分析完成，消耗 ¥{theme_result.cost_rmb + review_result.cost_rmb:.4f}")
            
        except Exception as e:
            st.warning(f"⚠️ AI分析失败: {e}")
    else:
        if not api_key:
            st.info("ℹ️ 未设置API密钥，跳过AI分析")
        else:
            st.info("ℹ️ 文献数不足5篇，跳过AI分析")
    
    progress_bar.progress(80)
    
    # 步骤5: 展示结果
    status_text.text("步骤 5/5: 展示分析结果...")
    
    # 显示图表
    st.header("🎨 可视化图谱")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 趋势", "🔗 关键词网络", "👥 作者合作", 
        "🏢 机构合作", "☁️ 词云", "📊 作者排名"
    ])
    
    with tab1:
        st.image(os.path.join(output_dir, "04_年度发文趋势.png"), use_column_width=True)
    
    with tab2:
        st.image(os.path.join(output_dir, "03_关键词共现网络.png"), use_column_width=True)
    
    with tab3:
        st.image(os.path.join(output_dir, "01_作者合作网络.png"), use_column_width=True)
    
    with tab4:
        st.image(os.path.join(output_dir, "02_机构合作网络.png"), use_column_width=True)
    
    with tab5:
        st.image(os.path.join(output_dir, "05_关键词词云.png"), use_column_width=True)
    
    with tab6:
        st.image(os.path.join(output_dir, "06_高产作者排名.png"), use_column_width=True)
    
    # AI报告
    if ai_report:
        st.header("🤖 AI智能分析")
        with st.expander("点击查看AI分析报告", expanded=True):
            st.markdown(ai_report)
    
    # 数据表格
    st.header("📋 文献数据")
    with st.expander("点击查看原始数据"):
        st.dataframe(df, use_container_width=True)
    
    # 下载区域
    st.header("💾 下载结果")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 打包所有图片
        import zipfile
        zip_path = os.path.join(output_dir, "所有图表.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for f in os.listdir(output_dir):
                if f.endswith('.png'):
                    zipf.write(os.path.join(output_dir, f), f)
        
        with open(zip_path, "rb") as f:
            st.download_button(
                label="📥 下载所有图表",
                data=f,
                file_name="所有图表.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    with col2:
        with open(excel_path, "rb") as f:
            st.download_button(
                label="📥 下载Excel数据",
                data=f,
                file_name="文献数据.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with col3:
        if ai_report and os.path.exists(os.path.join(output_dir, "07_AI智能分析报告.md")):
            with open(os.path.join(output_dir, "07_AI智能分析报告.md"), "rb") as f:
                st.download_button(
                    label="📥 下载AI报告",
                    data=f,
                    file_name="AI分析报告.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        else:
            st.button("📥 下载AI报告", disabled=True, use_container_width=True)
    
    progress_bar.progress(100)
    status_text.text("✅ 分析完成！")
    
    st.balloons()


if __name__ == "__main__":
    main()