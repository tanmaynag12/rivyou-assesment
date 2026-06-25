from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
def issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "token": str(refresh.access_token),
        "refresh": str(refresh),
    }
def blacklist_refresh_token(user, refresh_token):
    token = RefreshToken(refresh_token)

    if str(token.get(api_settings.USER_ID_CLAIM)) != str(user.pk):
        raise PermissionError(
            "Refresh token does not belong to this user."
        )

    token.blacklist()