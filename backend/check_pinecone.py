from app.core.vector_store import vector_store
from app.core.database import db
from app.lms.models.lesson_media import LessonMedia

# Get video details
session = db.get_session()
video = session.query(LessonMedia).filter(LessonMedia.id == '1ca17fa1-f085-4049-97fe-08e189e332be').first()

if video:
    print(f'Video: {video.title}')
    print(f'Lesson ID: {video.lesson_id}')

    # Query Pinecone for vectors related to this video
    results = vector_store.index.query(
        vector=[0.0] * 1024,  # Dummy vector to search all
        filter={'media_id': str(video.id)},
        top_k=5,
        include_metadata=True
    )

    print(f'\nFound {len(results.matches)} chunks in Pinecone')
    if results.matches:
        print('\nFirst chunk metadata:')
        for key, value in results.matches[0].metadata.items():
            if key != 'content':
                print(f'  {key}: {value}')

        print(f'\nContent preview: {results.matches[0].metadata.get("content", "")[:200]}...')

session.close()
