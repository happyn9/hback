from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ---------------- WORKSPACE ----------------
class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceOut(WorkspaceBase):
    id: int
    creator_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ---------------- WORKSPACE MEMBER ----------------
class WorkspaceMemberBase(BaseModel):
    user_id: int
    role: Optional[str] = "member"

class WorkspaceMemberCreate(WorkspaceMemberBase):
    pass

class WorkspaceMemberOut(WorkspaceMemberBase):
    id: int
    workspace_id: int
    joined_at: datetime

    class Config:
        orm_mode = True

# ---------------- WORKSPACE MESSAGE ----------------
class WorkspaceMessage(BaseModel):
    message: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    voice_url: Optional[str] = None
    is_ai: Optional[bool] = False

class WorkspaceMessageCreate(WorkspaceMessage):
    pass  # user_id et workspace_id seront passés dans la route

class WorkspaceMessageOut(WorkspaceMessage):
    id: int
    workspace_id: int
    sender_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ---------------- WORKSPACE ACTIVITY ----------------
class WorkspaceActivityBase(BaseModel):
    action: str

class WorkspaceActivityCreate(WorkspaceActivityBase):
    user_id: int

class WorkspaceActivityOut(WorkspaceActivityBase):
    id: int
    workspace_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---- Invitation par email ou username ----
class InviteByIdentifierIn(BaseModel):
    identifier: str          # email OU username
    role: Optional[str] = "member"


# ---- Membre enrichi (avec infos user) ----
class WorkspaceMemberDetail(BaseModel):
    id: int
    user_id: int
    role: str
    joined_at: datetime
    name: str
    email: str
    avatar: Optional[str] = None

    model_config = {"from_attributes": True}  


# ---- Liste membres ----
class WorkspaceMembersListOut(BaseModel):
    members: List[WorkspaceMemberDetail]
    total: int