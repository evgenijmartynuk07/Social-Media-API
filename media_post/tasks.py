from datetime import datetime

from media_post.models import Post

from celery import shared_task


@shared_task
def create_post(data, publish_time):
    publish_time = datetime.strptime(publish_time[:-1], "%Y-%m-%dT%H:%M:%S.%f")
    hashtag = data.get("hashtag")
    text_content = data.get("text_content")
    media_attachment = data.get("media_attachment")
    user = data.get("user")
    delay = publish_time - datetime.utcnow()
    if delay.total_seconds() > 0:
        create_post.apply_async(args=[data, publish_time], eta=publish_time)
        return

    post = Post.objects.create(
        hashtag=hashtag,
        text_content=text_content,
        media_attachment=media_attachment,
        user_id=user,
    )
    return post.id
