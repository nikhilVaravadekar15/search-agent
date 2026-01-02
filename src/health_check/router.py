from fastapi import APIRouter, status

from src.commonlib import types

router = APIRouter(prefix="/healthz")


@router.get("/")
def health_check():
    return types.ApiResponseModel(
        status=status.HTTP_200_OK, message="healthy", data=None, success=True
    )
