from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base

# ----------------- WORKSPACE -----------------
class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    max_members = Column(Integer, default=3)
    creator = relationship("User")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    messages = relationship("WorkspaceMessage", back_populates="workspace", cascade="all, delete-orphan")
    activities = relationship("WorkspaceActivity", back_populates="workspace", cascade="all, delete-orphan")
# ----------------- WORKSPACE MEMBER -----------------
class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # member | admin
    joined_at = Column(DateTime, server_default=func.now())

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")

class WorkspaceMessage(Base):
    __tablename__ = "workspace_messages"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))

    message = Column(String, nullable=True)  # texte optionnel

    file_url = Column(String, nullable=True)  # 📎 docs/images
    file_type = Column(String, nullable=True)  # image/pdf/audio

    voice_url = Column(String, nullable=True)  # 🎤 vocal

    is_ai = Column(Boolean, default=False)
    timestamp = Column(DateTime, server_default=func.now())

    workspace = relationship("Workspace", back_populates="messages")
    sender = relationship("User")

# ----------------- WORKSPACE ACTIVITY -----------------
class WorkspaceActivity(Base):
    __tablename__ = "workspace_activities"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # ex: "added lesson", "commented"
    created_at = Column(DateTime, server_default=func.now())

    workspace = relationship("Workspace")
    user = relationship("User")