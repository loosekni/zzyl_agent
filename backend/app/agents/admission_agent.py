"""入住办理 Agent。

迁移自原项目 AdmissionAgent，用 SQLite + AdmissionRun 表持久化替代原项目的 Redis checkpoint。
状态机：preview → WAITING_APPROVAL（持 reservation_token + expires_at）→ confirm/cancel → COMPLETED/CANCELLED。
confirm 时标记床位 occupied；过期或非法状态转换被拒绝。version 字段记录乐观锁版本
（生产环境应像原项目那样用 Redis Lua CAS 做严格原子乐观锁，这里用 ORM 读-改-写简化）。
"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models.nursing import (
    AdmissionRun,
    AdmissionStatus,
    Bed,
    BedStatus,
    Elder,
    NursingProject,
)

RESERVATION_TTL_MINUTES = 15


class AdmissionError(Exception):
    """入住办理流程中的业务错误。"""

    def __init__(self, code: str, message: str, status: AdmissionStatus = AdmissionStatus.failed):
        self.code = code
        self.status = status
        super().__init__(message)


class AdmissionAgent:
    """有状态入住办理 Agent：preview → 人工确认 → confirm/cancel。"""

    def __init__(self, session: Session):
        self.session = session

    async def preview(self, elder_id: int, preferred_bed_id: int | None = None) -> dict:
        elder = self.session.get(Elder, elder_id)
        if elder is None:
            raise AdmissionError("ELDER_NOT_FOUND", f"未找到老人 id={elder_id}")

        available_beds = list(
            self.session.exec(select(Bed).where(Bed.status == BedStatus.available)).all()
        )
        if not available_beds:
            raise AdmissionError("NO_AVAILABLE_BED", "当前没有可用床位")

        bed = next((b for b in available_beds if b.id == preferred_bed_id), None) if preferred_bed_id else None
        if bed is None:
            bed = available_beds[0]

        projects = list(self.session.exec(select(NursingProject)).all())
        project_lines = "、".join(project.name for project in projects[:6]) or "暂无"

        token = secrets.token_urlsafe(24)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESERVATION_TTL_MINUTES)

        summary = (
            f"老人 {elder.name} 拟入住床位 {bed.bed_no}；"
            f"健康摘要：{elder.health_summary or '无'}；"
            f"建议护理项目：{project_lines}。"
        )

        run = AdmissionRun(
            elder_id=elder_id,
            status=AdmissionStatus.waiting_approval,
            reservation_token=token,
            expires_at=expires_at,
            bed_id=bed.id,
            preview_summary=summary,
            version=1,
        )
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)

        return {
            "run_id": run.id,
            "status": run.status.value,
            "elder_name": elder.name,
            "bed_id": bed.id,
            "bed_no": bed.bed_no,
            "preview_summary": summary,
            "reservation_token": token,
            "expires_at": expires_at.isoformat(),
        }

    async def confirm(self, run_id: int, reservation_token: str) -> dict:
        run = self._load_and_validate(run_id, reservation_token)

        if run.bed_id is not None:
            bed = self.session.get(Bed, run.bed_id)
            if bed is not None and bed.status == BedStatus.available:
                bed.status = BedStatus.occupied
                self.session.add(bed)

        run.status = AdmissionStatus.completed
        run.reservation_token = None
        run.expires_at = None
        run.version += 1
        run.updated_at = datetime.now(timezone.utc)
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)

        return {
            "run_id": run.id,
            "status": run.status.value,
            "elder_id": run.elder_id,
            "bed_id": run.bed_id,
            "message": "入住已确认，床位已标记为已入住。",
        }

    async def cancel(self, run_id: int, reservation_token: str) -> dict:
        run = self._load_and_validate(run_id, reservation_token)

        run.status = AdmissionStatus.cancelled
        run.reservation_token = None
        run.expires_at = None
        run.version += 1
        run.updated_at = datetime.now(timezone.utc)
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)

        return {
            "run_id": run.id,
            "status": run.status.value,
            "elder_id": run.elder_id,
            "message": "入住预约已取消。",
        }

    def _load_and_validate(self, run_id: int, reservation_token: str) -> AdmissionRun:
        run = self.session.get(AdmissionRun, run_id)
        if run is None:
            raise AdmissionError("RUN_NOT_FOUND", f"未找到入住办理记录 id={run_id}")

        if run.status != AdmissionStatus.waiting_approval:
            raise AdmissionError(
                "INVALID_STATUS",
                f"当前状态 {run.status.value} 不允许确认/取消",
                status=run.status,
            )

        if not run.reservation_token or run.reservation_token != reservation_token:
            raise AdmissionError("TOKEN_INVALID", "reservation token 无效")

        if run.expires_at is None:
            raise AdmissionError("STATE_INVALID", "预览状态异常，缺少过期时间")
        expires = (
            run.expires_at.replace(tzinfo=timezone.utc)
            if run.expires_at.tzinfo is None
            else run.expires_at
        )
        if expires <= datetime.now(timezone.utc):
            run.status = AdmissionStatus.expired
            run.reservation_token = None
            run.expires_at = None
            self.session.add(run)
            self.session.commit()
            raise AdmissionError("EXPIRED", "预览已过期，请重新生成", status=AdmissionStatus.expired)

        return run
