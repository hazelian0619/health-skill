"""Profile models and helpers."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Surgery(BaseModel):
    name: str = Field(..., min_length=1)
    date: date
    notes: str | None = None


class StaticProfile(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Literal["female", "male", "other", "unspecified"]
    height_cm: float | None = Field(default=None, ge=40, le=250)
    weight_kg: float | None = Field(default=None, ge=2, le=300)
    surgeries: list[Surgery] = Field(default_factory=list)
    medical_history: list[str] = Field(default_factory=list)
    training_forbidden: list[str] = Field(default_factory=list)
    location: str | None = None
    allergies: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)
    tcm_constitution: Literal[
        "balanced",
        "qi_deficiency",
        "yang_deficiency",
        "yin_deficiency",
        "phlegm_damp",
        "damp_heat",
        "blood_stasis",
        "qi_stagnation",
        "special",
    ] = "balanced"


class DynamicProfile(BaseModel):
    goals: list[str] = Field(default_factory=list)
    activity_level: Literal["sedentary", "light", "moderate", "high"] | None = None
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    diet_preferences: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    stress_level: int | None = Field(default=None, ge=0, le=10)


class RealtimeProfile(BaseModel):
    heart_rate_bpm: int | None = Field(default=None, ge=30, le=220)
    blood_pressure_sys: int | None = Field(default=None, ge=70, le=220)
    blood_pressure_dia: int | None = Field(default=None, ge=40, le=140)
    steps_today: int | None = Field(default=None, ge=0)
    pain_scale: int | None = Field(default=None, ge=0, le=10)
    reported_symptoms: list[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    static: StaticProfile
    dynamic: DynamicProfile = Field(default_factory=DynamicProfile)
    realtime: RealtimeProfile = Field(default_factory=RealtimeProfile)


def normalize_profile(profile: UserProfile) -> UserProfile:
    """Normalize profile data (currently no-op but kept for future rules)."""
    return profile
