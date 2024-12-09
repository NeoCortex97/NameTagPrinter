from fastapi import APIRouter

router = APIRouter(
    prefix='/nametags',
    tags=['nametags']
)

@router.get('/preview')
def get_preview_image():
    pass