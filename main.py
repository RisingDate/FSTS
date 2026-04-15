import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from tools.logger import log_with_tag
from tools.markdown_saver import save_agents_to_markdown
from tools.pipeline import script_generate, script_finalized, actor_generate

MODEL_LIST = ['deepseek-r1:32b', 'deepseek-r1:32b-qwen-distill-q8_0', 'gpt-4o', 'gpt-5-mini']
REQUIREMENT_LIST = [
    '我想要复现古巴导弹危机中美国和古巴在各个时间段的行为，分析什么因素对战争的走势影响最大',

    '我想要分析一个由业务员组成的数字政务系统中，对业务员工作效率影响的最大因素。在此系统中，业务员需要不断处理来自客户的订单，每一份订单的难度有不同的水平，员工的薪资可能也不相同',

    '我想探究在古巴导弹危机中，若美国一直采用强硬的态度，最终战争的走向',

    '我想复现古巴导弹危机的结果，只需要做两三组实验即可',

    '我想要复现古巴导弹危机事件，探究相关国家主要领导人的决策风格等因素对战争关键事件和最终结果的影响。你设计的实验组数不要超过5，我只是想要复现历史上的古巴导弹危机，探究在经历历史事件时Agent的决策与史实是否相同或接近。在设计Agent时，你只需要设计美国和苏联两个Agent即可',

    '我想要复现古巴导弹危机事件，探究国家实力、经济形势、科技水平、军事武装以及国家领导人的决策风格等因素对战争关键事件和最终结果的影响。'
    '在设计实验时，你需要额外设置一个能够反应世界态势的响应变量，反映当前时刻国际关系的紧张程度。'
    '同时，你需要设置多组实验，第一组实验需要根据历史上的实际情况还原战争事件，其余实验探究 在经历相同历史事件时，不同的影响因素水平对Agent的决策与史实是否相同或接近。在设计Agent时，你只需要设计美国和苏联两个国家Agent即可',

    '我想要复现古巴导弹危机事件，国家实力、经济形势、科技水平、军事武装以及国家领导人的决策风格等因素对战争关键事件和最终结果的影响。'
    '在本次实验中，我想要探究当美国一直采取强硬态度时，战争的走向情况以及事件最终是否会导致战争的爆发'
    '在设计实验时，你需要额外设置一个能够反应世界态势的响应变量，衡量当前时刻国际关系的紧张程度。'
    '你需要设置多组实验。在设计Agent时，你只需要设计美国和苏联两个国家Agent即可',

    '我想要分析一个由外卖员和城市居民组成的智慧城市场景中影响外卖员工作积极性的主要因素。在此系统中，业务员可以主动接取客户的订单，从对应的商户取单后送到客户手中'
    '我的实验场景是一个为期7天的模拟环境，你需要设计外卖员、城市居民和商户三类Agent'
]

MAX_RE_NUM = 15
MODEL1 = MODEL_LIST[2]
MODEL2 = MODEL_LIST[3]

if __name__ == '__main__':
    # 开始一次新的实验
    print("=== 开始执行主程序 ===")

    # 记录实验开始时间
    script_start_time = datetime.now()
    print(f"实验开始时间: {script_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("正在初始化日志...")
    log_with_tag(message=' ', tag='---New Exp---', level='critical')
    print("日志初始化完成")
    req = REQUIREMENT_LIST[-1]
    print(f"需求: {req}")

    # *********** Step1-剧本生成 **********
    print("开始剧本生成...")
    script_list = script_generate(req, MODEL1, MODEL2, MAX_RE_NUM)
    if script_list is None:
        print("用户需求不合理")
        sys.exit(0)
    print("剧本生成完成")

    # *********** Step2-剧本敲定 **********
    print("开始剧本敲定...")
    determined_script = script_finalized(req, script_list, script_start_time, MODEL2)
    print(f"剧本敲定完成：{determined_script}")

    # *********** Step3-演员生成 **********
    print("开始演员生成...")
    agent_start_time = datetime.now()
    actor_list = actor_generate(req, determined_script, MODEL2, MAX_RE_NUM)
    print("演员生成完成")
    print(actor_list)
    agent_end_time = datetime.now()

    # 保存Agent信息到markdown（与剧本保存一致，scripts -> agents）
    save_agents_to_markdown(actor_list, start_time=agent_start_time, end_time=agent_end_time, req=req)
