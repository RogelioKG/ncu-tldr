from typing import Literal

from pydantic import BaseModel


class ReactionRequest(BaseModel):
    reaction: Literal["like", "dislike"]


class ReactionResponse(BaseModel):
    likes: int
    dislikes: int
    user_reaction: Literal["like", "dislike"] | None = None
