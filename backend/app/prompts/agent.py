"""Chinese prompt builders for agent workflows."""


def build_chat_prompt(message: str, history: str) -> str:
    if not history:
        return message
    return f"以下是当前会话的历史消息：\n{history}\n\n请回答用户最新问题：{message}"


def build_checkin_recommendation_prompt(
    elder_name: str,
    health_summary: str | None,
    available_bed_count: int,
    nursing_project_count: int,
) -> str:
    return (
        f"老人姓名：{elder_name}\n"
        f"健康摘要：{health_summary or '无'}\n"
        f"可用床位数：{available_bed_count}\n"
        f"护理项目数：{nursing_project_count}\n"
        "请给出简短入住建议，包含床位匹配、护理关注点和下一步动作。"
    )


def build_care_plan_prompt(
    elder_name: str,
    health_summary: str | None,
    care_goal: str,
    project_lines: str,
) -> str:
    return (
        f"老人姓名：{elder_name}\n"
        f"健康摘要：{health_summary or '无'}\n"
        f"护理目标：{care_goal or '维持日常照护安全和舒适'}\n"
        f"可选护理项目：\n{project_lines}\n"
        "请生成一份简短护理计划草案，包含护理重点、建议项目、执行频次和风险提醒。"
    )


def build_alert_analysis_prompt(
    device_name: str,
    severity: str,
    content: str,
    elder_name: str | None,
    health_summary: str | None,
) -> str:
    return (
        f"告警设备：{device_name}\n"
        f"告警级别：{severity}\n"
        f"告警内容：{content}\n"
        f"老人姓名：{elder_name or '未关联'}\n"
        f"健康摘要：{health_summary or '无'}\n"
        "请生成告警分析，包含可能原因、风险判断、护理处置建议和是否需要升级处理。"
    )
