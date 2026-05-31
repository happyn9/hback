from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceMessage
from app.models.user import User  # ✅ pour rechercher par email/username
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceOut,
    WorkspaceMemberCreate, WorkspaceMemberOut,
    WorkspaceMessageCreate, WorkspaceMessageOut,
    WorkspaceMembersListOut,
    InviteByIdentifierIn,
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


# ================================================================
# WORKSPACE
# ================================================================

@router.post("/", response_model=WorkspaceOut)
def create_workspace(
    data: WorkspaceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    workspace = Workspace(**data.dict(), creator_id=user.id)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Ajouter le créateur comme admin automatiquement
    _ensure_member(db, workspace.id, user.id, role="admin")

    return workspace


@router.get("/my-workspaces", response_model=List[WorkspaceOut])
def my_workspaces(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Workspace).filter(Workspace.creator_id == user.id).all()

# ── Workspaces où l'user est membre (invité ou créateur) ──────────
@router.get("/joined", response_model=List[WorkspaceOut])
def joined_workspaces(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Retourne tous les workspaces où l'user est membre (créés + invités)."""
    member_rows = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == user.id
    ).all()
    workspace_ids = [m.workspace_id for m in member_rows]
    if not workspace_ids:
        return []
    return db.query(Workspace).filter(Workspace.id.in_(workspace_ids)).all()


@router.get("/{workspace_id}", response_model=WorkspaceOut)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ws = _get_workspace_or_404(db, workspace_id)
    return ws


# ================================================================
# MEMBRES
# ================================================================

@router.get("/{workspace_id}/members", response_model=WorkspaceMembersListOut)
def list_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Retourne tous les membres avec leurs infos utilisateur."""
    _get_workspace_or_404(db, workspace_id)
    _require_member(db, workspace_id, user.id)

    members = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id)
        .all()
    )

    result = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        result.append({
            "id": m.id,
            "user_id": m.user_id,
            "role": m.role,
            "joined_at": m.joined_at,
            "name": u.name if u else "Unknown",
            "email": u.email if u else "",
            "avatar": getattr(u, "avatar", None),
        })

    return {"members": result, "total": len(result)}


@router.post("/{workspace_id}/invite", response_model=WorkspaceMemberOut)
def invite_member(
    workspace_id: int,
    data: InviteByIdentifierIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Invite un utilisateur par email ou username.
    Seul un admin ou le créateur peut inviter.
    """
    ws = _get_workspace_or_404(db, workspace_id)
    _require_role(db, workspace_id, user.id, allowed=["admin"])

    # Chercher l'utilisateur cible
    target = (
        db.query(User)
        .filter(
            (User.email == data.identifier) | (User.name == data.identifier)
        )
        .first()
    )
    if not target:
        raise HTTPException(404, f"Utilisateur '{data.identifier}' introuvable")

    if target.id == user.id:
        raise HTTPException(400, "Vous êtes déjà membre de ce workspace")

    # Vérifier la limite de membres
    count = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).count()
    if ws.max_members and count >= ws.max_members:
        raise HTTPException(403, f"Ce workspace est limité à {ws.max_members} membres")

    # Vérifier doublon
    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == target.id,
    ).first()
    if existing:
        raise HTTPException(409, "Cet utilisateur est déjà membre")

    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=target.id,
        role=data.role or "member",
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{workspace_id}/members/{member_user_id}", status_code=204)
def remove_member(
    workspace_id: int,
    member_user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Retirer un membre. Admin uniquement (ou soi-même pour quitter)."""
    _get_workspace_or_404(db, workspace_id)

    is_self = member_user_id == user.id
    if not is_self:
        _require_role(db, workspace_id, user.id, allowed=["admin"])

    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == member_user_id,
    ).first()
    if not member:
        raise HTTPException(404, "Membre introuvable")

    db.delete(member)
    db.commit()


# ================================================================
# MESSAGES
# ================================================================

@router.get("/{workspace_id}/messages", response_model=List[WorkspaceMessageOut])
def get_messages(
    workspace_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_member(db, workspace_id, user.id)
    return (
        db.query(WorkspaceMessage)
        .filter(WorkspaceMessage.workspace_id == workspace_id)
        .order_by(WorkspaceMessage.timestamp)
        .all()
    )


@router.post("/{workspace_id}/messages", response_model=WorkspaceMessageOut)
def send_message(
    workspace_id: int,
    message: WorkspaceMessageCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_member(db, workspace_id, user.id)

    if not (message.message or message.file_url or message.voice_url):
        raise HTTPException(400, "Message vide")

    msg = WorkspaceMessage(
        workspace_id=workspace_id,
        sender_id=user.id,
        message=message.message,
        file_url=message.file_url,
        file_type=message.file_type,
        voice_url=message.voice_url,
        is_ai=message.is_ai,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


# ================================================================
# WEBSOCKET
# ================================================================

connections: dict[int, list[WebSocket]] = {}


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: int):
    await websocket.accept()
    connections.setdefault(workspace_id, []).append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            for conn in connections[workspace_id]:
                await conn.send_json(data)
    except WebSocketDisconnect:
        connections[workspace_id].remove(websocket)
        if not connections[workspace_id]:
            del connections[workspace_id]


# ================================================================
# HELPERS INTERNES
# ================================================================

def _get_workspace_or_404(db: Session, workspace_id: int) -> Workspace:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(404, "Workspace introuvable")
    return ws


def _ensure_member(db: Session, workspace_id: int, user_id: int, role: str = "member"):
    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    ).first()
    if not existing:
        db.add(WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role))
        db.commit()


def _require_member(db: Session, workspace_id: int, user_id: int):
    m = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    ).first()
    if not m:
        raise HTTPException(403, "Accès refusé : vous n'êtes pas membre")


def _require_role(db: Session, workspace_id: int, user_id: int, allowed: list[str]):
    m = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    ).first()
    if not m or m.role not in allowed:
        raise HTTPException(403, "Permissions insuffisantes")


