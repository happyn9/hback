from sqlalchemy import Column, Integer, String, ForeignKey, Float,Date, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import date

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)           # ex: "Monthly Plan"
    description = Column(String(255), nullable=True)
    duration_days = Column(Integer, nullable=False)      # durée en jours
    price = Column(Float, nullable=False)
    billing_type = Column(String(20), nullable=False)  # "monthly" | "yearly"
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    # Relation vers Course
    course = relationship("Course", back_populates="subscriptions")
    
    # Relation vers UserSubscription
    user_subscriptions = relationship("UserSubscription", back_populates="subscription")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relations
    subscription = relationship("Subscription", back_populates="user_subscriptions")
    user = relationship("User", back_populates="subscriptions")
    def check_active(self):
        """Vérifie si l'abonnement est encore actif aujourd'hui"""
        return self.is_active and self.start_date <= date.today() <= self.end_date