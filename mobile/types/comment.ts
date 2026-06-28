export type Comment = {
    "id": number,
    "post_id": number,
    "user_id": number,
    "content": string,
    "created_at": string,
    "user": CommentAuthor
}

type CommentAuthor = {

    "id": number,
    "username": string,
    "avatar_url": string | null
}