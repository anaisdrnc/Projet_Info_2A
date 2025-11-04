from fastapi import APIRouter, HTTPException, status

from src.Model.Movie import Movie

movie_router = APIRouter(prefix="/movies", tags=["Movies"])


@movie_router.get("/{tmdb_id}", status_code=status.HTTP_200_OK)
def get_movie_by_id(tmdb_id: int):
    try:
        if tmdb_id == 1:
            return Movie(original_title="The Wild Rainbow", id=1)
        elif tmdb_id == 2:
            return Movie(original_title="Inside Out 2", id=2)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with id [{tmdb_id}] not found"
        )
