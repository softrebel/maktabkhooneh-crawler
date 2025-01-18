from pydantic import BaseModel

from datetime import datetime

# JobPlatform


class LoginResponse(BaseModel):
    status: str
    message: str


class UserInfo(BaseModel):
    is_staff: bool
    user_id: int
    email: str
    phone: str
    business_admin: bool
    team_admin: bool
    business_student: bool
