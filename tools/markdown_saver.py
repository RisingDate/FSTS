import json
import os
from datetime import datetime

from tools.logger import log_with_tag


# 保存剧本到markdown文件
def save_scripts_to_markdown(scripts, script_ratings, start_time, end_time, req):
    """
    保存剧本和评分到markdown文件

    Args:
        scripts: 生成的剧本列表
        script_ratings: 剧本评分列表
        start_time: 实验开始时间
        end_time: 实验结束时间
        req: 实验需求
    """
    # 确保日志目录存在
    log_dir = "log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 生成文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"experiment_scripts_{timestamp}.md"
    filepath = os.path.join(log_dir, filename)

    # 计算实验持续时间
    duration = end_time - start_time
    duration_str = f"{duration.total_seconds():.2f}秒"

    # 生成markdown内容
    markdown_content = f"""# 实验剧本生成报告

## 实验信息
- **实验时间**: {start_time.strftime("%Y-%m-%d %H:%M:%S")} - {end_time.strftime("%Y-%m-%d %H:%M:%S")}
- **实验持续时间**: {duration_str}
- **生成剧本数量**: {len(scripts)}
- **实验需求**: {req}

## 剧本详情

"""

    # 添加每个剧本的详细信息
    for i, (script, rating) in enumerate(zip(scripts, script_ratings)):
        markdown_content += f"### 剧本 {i + 1}\n\n#### 基本信息\n"
        markdown_content += f"- **研究目标**: {script.get('goal', {}).get('explain', 'N/A')}\n"
        markdown_content += f"- **目标类型**: {script.get('goal', {}).get('category', 'N/A')}\n\n"

        markdown_content += "#### 影响因素\n"
        markdown_content += chr(10).join([f"- {factor}" for factor in script.get('influence_factor', [])]) + "\n\n"

        markdown_content += "#### 响应变量\n"
        markdown_content += chr(10).join([f"- {var}" for var in script.get('response_var', [])]) + "\n\n"

        markdown_content += "#### 数学公式\n"
        for var, formula in script.get('formula', {}).items():
            markdown_content += f"- **{var}**: `{formula}`\n"

        markdown_content += f"\n#### 实验参数\n"
        markdown_content += f"- **实验方法**: {script.get('exp_params', {}).get('exp_method', 'N/A')}\n"
        markdown_content += "- **参数设置**: \n"

        params = script.get('exp_params', {}).get('params', {})
        for param, values in params.items():
            markdown_content += f"  - **{param}**: {values}\n"

        # 添加评分信息
        if rating:
            scientific = rating.get('scientific', 0)
            difficulty = rating.get('difficulty', 0)
            quality = rating.get('quality', 0)
            risk = rating.get('risk', 0)
            fitness = rating.get('fitness', 0)
            ethics = rating.get('ethics', 0)

            total_score = (scientific * 0.15 + difficulty * 0.05 + quality * 0.1 +
                           risk * 0.05 + fitness * 0.15 + ethics * 0.5)

            markdown_content += f"""
#### 剧本评分
- **核心科学性**: {scientific}/100
- **实验实施难度**: {difficulty}/100
- **实验条件与可控性**: {quality}/100
- **风险与稳健性**: {risk}/100
- **需求贴合度**: {fitness}/100
- **伦理与合规**: {ethics}/100
- **综合得分**: {total_score:.2f}/100

"""
        else:
            markdown_content += "\n#### 剧本评分\n- 评分信息不可用\n\n"

        markdown_content += "---\n\n"

    # 添加实验总结
    if script_ratings:
        best_script_idx = max(range(len(script_ratings)),
                              key=lambda i: (script_ratings[i].get('scientific', 0) * 0.15 +
                                             script_ratings[i].get('difficulty', 0) * 0.05 +
                                             script_ratings[i].get('quality', 0) * 0.1 +
                                             script_ratings[i].get('risk', 0) * 0.05 +
                                             script_ratings[i].get('fitness', 0) * 0.15 +
                                             script_ratings[i].get('ethics', 0) * 0.5))

        markdown_content += f"## 实验总结\n\n- **最佳剧本**: 剧本 {best_script_idx + 1}\n"
        avg_score = sum(rating.get('scientific', 0) * 0.15 + rating.get('difficulty', 0) * 0.05 +
                        rating.get('quality', 0) * 0.1 + rating.get('risk', 0) * 0.05 +
                        rating.get('fitness', 0) * 0.15 + rating.get('ethics', 0) * 0.5
                        for rating in script_ratings) / len(script_ratings)
        markdown_content += f"- **平均评分**: {avg_score:.2f}/100\n\n"

    markdown_content += f"## 生成时间\n- **文件生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"✓ 剧本已保存到: {filepath}")
        log_with_tag(message=f"剧本保存成功: {filepath}", tag='Script Save', level='info')
    except Exception as e:
        print(f"✗ 保存剧本文件失败: {e}")
        log_with_tag(message=f"剧本保存失败: {e}", tag='Script Save Error', level='error')


# 保存智能体信息到markdown文件
def save_agents_to_markdown(agents_info, start_time, end_time, req):
    """
    保存智能体信息到markdown文件
    """
    # 确保日志目录存在
    log_dir = "log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"experiment_agents_{timestamp}.md"
    filepath = os.path.join(log_dir, filename)

    duration = end_time - start_time
    duration_str = f"{duration.total_seconds():.2f}秒"

    markdown_content = f"""# 智能体信息生成报告

## 实验信息
- **生成时间段**: {start_time.strftime("%Y-%m-%d %H:%M:%S")} - {end_time.strftime("%Y-%m-%d %H:%M:%S")}
- **生成耗时**: {duration_str}
- **实验需求**: {req}

## 智能体详情
"""

    try:
        if isinstance(agents_info, dict):
            if 'attribute' in agents_info:
                markdown_content += "\n### 属性列表\n"
                try:
                    for idx, item in enumerate(agents_info.get('attribute', []), start=1):
                        markdown_content += f"- 条目 {idx}: {json.dumps(item, ensure_ascii=False)}\n"
                except Exception:
                    markdown_content += f"\n```json\n{json.dumps(agents_info.get('attribute', []), ensure_ascii=False, indent=2)}\n```\n"

            if 'attribute_explain' in agents_info:
                markdown_content += "\n### 属性说明\n"
                try:
                    for idx, item in enumerate(agents_info.get('attribute_explain', []), start=1):
                        markdown_content += f"- 条目 {idx}: {json.dumps(item, ensure_ascii=False)}\n"
                except Exception:
                    markdown_content += f"\n```json\n{json.dumps(agents_info.get('attribute_explain', []), ensure_ascii=False, indent=2)}\n```\n"

            if 'relationship_net' in agents_info:
                markdown_content += "\n### 关系网络\n"
                try:
                    for idx, item in enumerate(agents_info.get('relationship_net', []), start=1):
                        markdown_content += f"- 关系 {idx}: {json.dumps(item, ensure_ascii=False)}\n"
                except Exception:
                    markdown_content += f"\n```json\n{json.dumps(agents_info.get('relationship_net', []), ensure_ascii=False, indent=2)}\n```\n"

            remaining = {k: v for k, v in agents_info.items() if
                         k not in ['attribute', 'attribute_explain', 'relationship_net']}
            if remaining:
                markdown_content += "\n### 其他信息\n"
                markdown_content += f"\n```json\n{json.dumps(remaining, ensure_ascii=False, indent=2)}\n```\n"
        else:
            markdown_content += f"\n```json\n{json.dumps(agents_info, ensure_ascii=False, indent=2)}\n```\n"
    except Exception:
        markdown_content += f"\n````\n{str(agents_info)}\n````\n"

    markdown_content += f"\n## 生成时间\n- **文件生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"✓ 智能体信息已保存到: {filepath}")
        log_with_tag(message=f"智能体信息保存成功: {filepath}", tag='Agent Save', level='info')
    except Exception as e:
        print(f"✗ 保存智能体文件失败: {e}")
        log_with_tag(message=f"智能体信息保存失败: {e}", tag='Agent Save Error', level='error')
