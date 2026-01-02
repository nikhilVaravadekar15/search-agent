from fastapi import APIRouter, status

from src.commonlib import types as common_types

router = APIRouter(prefix="/healthz")


@router.get("/")
def health_check():
    return common_types.ApiResponseModel(
        status_code=status.HTTP_200_OK, msg="success", data={"message": "healthy"}
    )
