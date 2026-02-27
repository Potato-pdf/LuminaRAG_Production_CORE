"""
Authentication module.
"""
from src.auth.security import (
    hash_password,
    verify_password,
    generate_api_key,
    hash_api_key,
    verify_api_key
)
from src.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    create_tokens_for_user,
    TokenFactory
)
from src.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    verify_api_key as verify_api_key_dep,
    get_user_or_api_key,
    check_company_access
)
from src.auth.permissions import (
    PermissionChecker,
    CompanyAccessChecker,
    DocumentAccessChecker,
    DocumentEditChecker,
    AdminPermissionChecker,
    company_access,
    document_access,
    document_edit,
    admin_permission
)
from src.auth.rate_limiter import RateLimiter, rate_limit

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "generate_api_key",
    "hash_api_key",
    "verify_api_key",
    # JWT
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "create_tokens_for_user",
    "TokenFactory",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "verify_api_key_dep",
    "get_user_or_api_key",
    "check_company_access",
    # Permissions
    "PermissionChecker",
    "CompanyAccessChecker",
    "DocumentAccessChecker",
    "DocumentEditChecker",
    "AdminPermissionChecker",
    "company_access",
    "document_access",
    "document_edit",
    "admin_permission",
    # Rate Limiting
    "RateLimiter",
    "rate_limit"
]
