#!/usr/bin/env python3
"""
简化版测试脚本 - 测试arXiv数据抓取
不需要OpenAI API密钥，只测试论文获取功能
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json

def test_arxiv_fetch():
    """测试arXiv API抓取"""
    print("=" * 60)
    print("🧪 测试 arXiv 论文抓取")
    print("=" * 60)
    print()

    # 配置
    categories = ["cs.CL", "cs.AI"]  # LLM相关类别
    max_results = 5  # 每个类别取5篇
    days_lookback = 7

    all_papers = []

    for category in categories:
        print(f"📚 正在抓取类别: {category}")

        # 构建arXiv API查询
        base_url = "http://export.arxiv.org/api/query"
        query = f"cat:{category}"
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()

            # 解析XML
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'arxiv': 'http://arxiv.org/schemas/atom'}

            entries = root.findall('atom:entry', ns)

            print(f"  ✓ 找到 {len(entries)} 篇论文")

            for entry in entries:
                # 提取信息
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')

                # 作者
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns).text
                    authors.append(name)

                # 摘要
                abstract = entry.find('atom:summary', ns).text.strip()

                # 链接
                pdf_url = None
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        pdf_url = link.get('href')

                # arXiv ID
                arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]

                # 日期
                published = entry.find('atom:published', ns).text

                paper = {
                    'title': title[:80] + '...' if len(title) > 80 else title,
                    'authors': authors[:3],  # 只显示前3个作者
                    'arxiv_id': arxiv_id,
                    'category': category,
                    'published': published.split('T')[0],
                    'pdf_url': pdf_url,
                    'abstract_preview': abstract[:150] + '...'
                }

                all_papers.append(paper)

        except Exception as e:
            print(f"  ✗ 错误: {e}")
            continue

    print()
    print("=" * 60)
    print(f"📊 抓取结果汇总")
    print("=" * 60)
    print(f"总共抓取: {len(all_papers)} 篇论文")
    print()

    # 显示论文列表
    for i, paper in enumerate(all_papers, 1):
        print(f"\n[{i}] {paper['title']}")
        print(f"    作者: {', '.join(paper['authors'])}")
        print(f"    ID: {paper['arxiv_id']} | 类别: {paper['category']}")
        print(f"    发表日期: {paper['published']}")
        print(f"    PDF: {paper['pdf_url']}")
        print(f"    摘要: {paper['abstract_preview']}")

    # 保存到JSON
    output_file = "test_papers.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"✅ 测试完成！")
    print(f"📄 结果已保存到: {output_file}")
    print("=" * 60)

def test_huggingface_fetch():
    """测试HuggingFace抓取（简化版）"""
    print()
    print("=" * 60)
    print("🤗 测试 HuggingFace Papers 抓取")
    print("=" * 60)

    url = "https://huggingface.co/papers"

    try:
        print(f"正在访问: {url}")
        response = requests.get(
            url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0 (Test Agent)'}
        )
        response.raise_for_status()

        print(f"✓ 成功获取页面 (长度: {len(response.content)} 字节)")
        print("✓ HuggingFace API连接正常")

        # 保存HTML用于调试
        with open('huggingface_test.html', 'w', encoding='utf-8') as f:
            f.write(response.text[:5000])  # 只保存前5000字符
        print("📄 页面样本已保存到: huggingface_test.html")

    except Exception as e:
        print(f"✗ 错误: {e}")

if __name__ == "__main__":
    # 测试arXiv
    test_arxiv_fetch()

    # 测试HuggingFace
    test_huggingface_fetch()

    print()
    print("🎉 所有测试完成！")
    print()
    print("💡 提示:")
    print("  - 查看 test_papers.json 了解抓取的论文")
    print("  - 这个测试不需要任何API密钥")
    print("  - 在你的本地Mac上运行完整版本会获得更多功能")
