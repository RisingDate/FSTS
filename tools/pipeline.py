import json
from datetime import datetime

from models.agents.Generator.AD.ADAgent import AgentDesignAgent
from models.agents.Generator.ED.VRAgent import VariableRegenerateAgent
from models.agents.Generator.RA.RAAgent import RequirementAnalysisAgent
from models.agents.Generator.SS.SSAgent import ScriptSelectAgent
from models.agents.Observer.AD.ADObserver import AgentDesignObserver
from models.agents.Observer.ED.VarObserver import VariableObserver
from models.agents.Observer.RA.RAObserver import RequirementAnalysisObserver
from tools.api_utils import safe_agent_call
from tools.logger import log_with_tag
from tools.markdown_saver import save_scripts_to_markdown


# 剧本生成
def script_generate(req, model1, model2, max_re_num=15):
    # 剧本list
    scripts = []
    exp_param = {
        'goal': None,
        'influence_factor': None,
        'response_var': None,
        'formula': None,
        'exp_params': None,
        'var_explain': None,
    }

    raAgent = RequirementAnalysisAgent(llm_model=model1)
    raObserver = RequirementAnalysisObserver(llm_model=model2)

    # 判断用户需求是否合规
    try:
        req_examine = safe_agent_call(raObserver, 'requirement_observe', req=req)
    except Exception as e:
        req_examine = {
            "flag": 0
        }
        print(f"需求检测报错: {e}")
        log_with_tag(message=f"需求检测出错: {e}", tag='Req Examine Error', level='error')

    if req_examine['flag'] == 0:
        print("\033[31m------用户提出的需求不满足需求三要素，请重新设计需求------\033[0m")
        print("错误原因: ", req_examine.get("reason", "未知"))
        return None

    analysis_num = 0
    focus_list = ['研究目标', '变量设定', '操作流程', '预期结果']
    for focus in focus_list:
        # 需求解析
        while True:
            print(f"正在分析需求，焦点: {focus}")
            try:
                ra_res = safe_agent_call(raAgent, 'requirement_analysis', req=req, focus=focus)
                print(f"需求分析结果: {ra_res}")
                log_with_tag(message=json.dumps(ra_res), tag='RA Result', level='info')
            except Exception as e:
                print(f"需求分析出错: {e}")
                log_with_tag(message=f"需求分析失败: {e}", tag='RA Error', level='error')
                break
            # 检查需求分析结果格式是否正确
            is_analysis_format_true = raObserver.requirement_format_judge(ra_res)
            if is_analysis_format_true:
                log_with_tag(message='需求解析成功', tag='RA Success', level='warning')
                print(f'\033[31m------需求解析成功------\033[0m')
                # 更新本次的实验参数
                for key in ['goal', 'influence_factor', 'response_var', 'formula', 'exp_params']:
                    exp_param[key] = ra_res[key]
                break
            else:
                log_with_tag(message='需求解析失败', tag='RA Fail', level='error')
                print(f'\033[31m------需求解析错误({analysis_num})------\033[0m')
                analysis_num += 1

        # 影响因素和响应变量内容检查
        regenerate_num = 0
        while True:
            varObserver = VariableObserver(llm_model=model2)
            try:
                vo_res = safe_agent_call(varObserver, 'VarAnalysis', req=req,
                                         influence_factor=exp_param['influence_factor'],
                                         response_var=exp_param['response_var'],
                                         formula=exp_param['formula'])
            except Exception as e:
                print(f"变量分析出错: {e}")
                log_with_tag(message=f"变量分析失败: {e}", tag='VO Error', level='error')
                break
            print('VO Response: ', vo_res)
            if vo_res['is_reasonable'] == 1 or regenerate_num >= max_re_num:
                print('\033[32m------变量生成正确------\033[0m')
                log_with_tag(message='变量生成正确', tag='VO Success', level='warning')

                if 'var_explain' in vo_res:
                    exp_param['var_explain'] = vo_res['var_explain']
                log_with_tag(message=json.dumps(exp_param), tag='VO Result', level='info')
                break
            else:
                regenerate_num += 1
                print('\033[31m------变量生成不合理------\033[0m')
                log_with_tag(message='变量生成不合理', tag='VO Error', level='warning')

                log_with_tag(message='重新生成变量', tag='Var Regenerate', level='info')
                vrAgent = VariableRegenerateAgent(llm_model=model2)
                try:
                    vr_res = safe_agent_call(vrAgent, 'VarRegenerate', req=req,
                                             influence_factor=exp_param['influence_factor'],
                                             response_var=exp_param['response_var'],
                                             formula=exp_param['formula'],
                                             error_reason=vo_res['reason'])
                except Exception as e:
                    print(f"变量重新生成出错: {e}")
                    log_with_tag(message=f"变量重新生成失败: {e}", tag='VR Error', level='error')
                    break

                print('\033[34m------变量已重新生成------\033[0m')
                log_with_tag(message=json.dumps(vr_res), tag='Var Regenerate Result', level='info')
                for key in ['influence_factor', 'response_var', 'formula', 'var_explain']:
                    exp_param[key] = vr_res[key]

        # 实验参数检查
        regenerate_num = 0
        while True:
            varObserver = VariableObserver(llm_model=model2)
            try:
                vo_res = safe_agent_call(varObserver, 'VarExpParamAnalysis', req=req,
                                         influence_factor=exp_param['influence_factor'],
                                         response_var=exp_param['response_var'],
                                         formula=exp_param['formula'],
                                         exp_params=exp_param['exp_params'])
            except Exception as e:
                print(f"实验参数分析出错: {e}")
                log_with_tag(message=f"实验参数分析失败: {e}", tag='VO-Exp Param Error', level='error')
                break
            print(vo_res)
            if vo_res['is_reasonable'] == 1 or (regenerate_num >= max_re_num and vo_res['reason'][:4] != '格式错误'):
                print('\033[32m------实验参数设置合理------\033[0m')
                log_with_tag(message='实验参数设置合理', tag='VO-Exp Param Right', level='warning')
                log_with_tag(message=vo_res['reason'], tag='VO-Exp Param Right Reason', level='info')
                break
            else:
                regenerate_num += 1
                print('\033[31m------实验参数设置不合理------\033[0m')
                log_with_tag(message='实验参数设置不合理', tag='VO-Exp Param Error', level='warning')
                log_with_tag(message=vo_res['reason'], tag='VO-Exp Param Error Reason', level='info')
                vrAgent = VariableRegenerateAgent(llm_model=model2)
                try:
                    vr_res = safe_agent_call(vrAgent, 'VarExpParamRegenerate', req=req,
                                             influence_factor=exp_param['influence_factor'],
                                             response_var=exp_param['response_var'],
                                             formula=exp_param['formula'],
                                             exp_params=exp_param['exp_params'],
                                             error_reason=vo_res['reason'])
                except Exception as e:
                    print(f"实验参数重新生成出错: {e}")
                    log_with_tag(message=f"实验参数重新生成失败: {e}", tag='VR-Exp Param Error', level='error')
                    break

                print('\033[34m------实验设计点已重新生成------\033[0m')
                log_with_tag(message=json.dumps(vr_res), tag='New Exp Params', level='info')
                exp_param['exp_params'] = vr_res['exp_params']
        scripts.append(exp_param.copy())

    return scripts


# 剧本敲定
def script_finalized(req, scripts, script_start_time, model2):
    ssAgent = ScriptSelectAgent(llm_model=model2)
    selected_script_index = 0
    max_score = 0
    index = 1

    # 为每个剧本生成评分
    print("开始为剧本评分...")
    script_ratings = []

    for script in scripts:
        try:
            print(f"正在评分剧本 {index}/{len(scripts)}...")
            rating = safe_agent_call(ssAgent, 'script_rating', req=req, script=script)
        except Exception as e:
            print(f"剧本 {index} 评分出错: {e}")
            log_with_tag(message=f"剧本评分失败: {e}", tag='SS Error', level='error')
            # 使用默认评分
            rating = {
                'scientific': 50, 'difficulty': 50, 'quality': 50,
                'risk': 50, 'fitness': 50, 'ethics': 100
            }
        script_ratings.append(rating)
        tmp_score = (rating['scientific'] * 0.15 + rating['difficulty'] * 0.05
                     + rating['quality'] * 0.1 + rating['risk'] * 0.05
                     + rating['fitness'] * 0.15 + rating['ethics'] * 0.5)
        print(f'剧本 {index} 得分：{tmp_score}')
        if tmp_score > max_score and tmp_score > 50:
            max_score = tmp_score
            selected_script_index = index
        index += 1

    # 记录剧本敲定结束时间
    script_end_time = datetime.now()
    print(f"剧本敲定结束时间: {script_end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("保存剧本到markdown文件...")
    save_scripts_to_markdown(scripts, script_ratings, start_time=script_start_time, end_time=script_end_time, req=req)

    return scripts[selected_script_index - 1]


# 演员生成
def actor_generate(req, script, model2, max_re_num=15):
    regenerate_num = 0
    while True:
        adAgent = AgentDesignAgent(llm_model=model2)
        try:
            agents_info = safe_agent_call(adAgent, 'agent_design', req=req, exp_plan=script)
        except Exception as e:
            print(f"智能体设计出错: {e}")
            log_with_tag(message=f"智能体设计失败: {e}", tag='AD Error', level='error')
            agents_info = None
            break
        print('智能体设计结果: ', agents_info)
        log_with_tag(message=agents_info, tag='AD Result', level='info')

        adObserver = AgentDesignObserver(llm_model=model2)
        # 检查Agents是否存在格式问题
        agent_design_format_flag, info = adObserver.format_check(agents_info)
        adObserver_res = {
            'is_reasonable': True,
            'reason': ''
        }
        if not agent_design_format_flag:
            adObserver_res['is_reasonable'] = False
            adObserver_res['reason'] = info
        else:
            # 检查内容是否合理
            try:
                adObserver_res = safe_agent_call(adObserver, 'agent_observe', req=req,
                                                 exp_plan=script, agent_list=agents_info)
            except Exception as e:
                print(f"智能体观察出错: {e}")
                log_with_tag(message=f"智能体观察失败: {e}", tag='AD Observer Error', level='error')
                adObserver_res = {'is_reasonable': True, 'reason': '观察失败，默认通过'}

        if adObserver_res['is_reasonable'] or regenerate_num >= max_re_num:
            print('\033[32m------智能体设计方案合理------\033[0m')
            log_with_tag(message='智能体设计方案格式正确', tag='AD Accept', level='info')
            break
        else:
            print('\033[31m------智能体设计方案不合理------\033[0m')
            print('错误原因为： ', adObserver_res['reason'])
            log_with_tag(message=adObserver_res['reason'], tag='AD Error', level='error')
            regenerate_num += 1

    return agents_info
