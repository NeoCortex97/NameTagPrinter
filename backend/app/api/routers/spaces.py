import spacedirectory.directory
from fastapi import APIRouter

router = APIRouter(
    prefix='/spaces',
    tags=['spaces']
)

@router.get('/')
def get_all_space_names():
    return list(spacedirectory.directory.get_spaces_list().keys())

@router.get('/details')
def get_space_logo_by_name(name: str):
    space = spacedirectory.directory.get_space_from_name(name)
    return {
        'logo': space.logo_url,
        'name': space.name,
        'website': space.website_url
    }