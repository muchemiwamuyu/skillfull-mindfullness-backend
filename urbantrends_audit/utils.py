# urbantrends_audit/utils.py
from .models import AuditLog


def log_action(
    action,
    resource_type,
    resource_id="",
    description="",
    user=None,
    ip_address=None,
    user_agent="",
    extra_data=None,
):
    """
    Create an AuditLog entry. Safe to call from signal handlers — all failures
    are swallowed so that a logging error never breaks a real user operation.
    """
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data,
        )
    except Exception as exc:
        print(f"[urbantrends_audit] Failed to write audit log: {exc}")
