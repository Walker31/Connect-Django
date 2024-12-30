from django.http import JsonResponse
from user.models import User
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from user.models import Profile
from .models import Post

@csrf_exempt
def create_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Get the User instance
            author_id = data.get("author")
            author = get_object_or_404(User, id=author_id)
            
            # Create the Post
            post = Post.objects.create(
                pic=data.get("pic"),
                post_text=data.get("post_text"),
                author=author,  # Pass the User instance
                interest=data.get("interest")
            )
            return JsonResponse({"message": "Post created successfully", "post_id": post.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def list_posts(request):
    if request.method == "GET":
        posts = Post.objects.all()
        posts_data = []
        try: 
            for post in posts:
                # Get the author's profile
                profile = get_object_or_404(Profile, user_id=post.author_id)
                posts_data.append({
                    "id": post.id,
                    "post_text": post.post_text,
                    "author": profile.user.username,
                    "author_pic" : profile.profile_picture,
                    "location": profile.location,
                    "interest": post.interest,
                    "background": post.pic,
                    "created_at": post.created_at,
                    "updated_at": post.updated_at
                })
            return JsonResponse(posts_data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)

def detail_post(request, post_id):
    if request.method == "GET":
        post = get_object_or_404(Post, id=post_id)
        return JsonResponse({
            "id": post.id,
            "post_text": post.post_text,
            "author_id": post.author.id,  # Include `author_id`
            "author_username": post.author.username,  # Optionally include username
            "interest": post.interest,
            "pic": post.pic
        }, status=200)
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)

@csrf_exempt
def update_post(request, post_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            post = get_object_or_404(Post, id=post_id)
            
            # Update fields
            post.post_text = data.get("post_text", post.post_text)
            author_id = data.get("author")
            if author_id:  # Update the author if provided
                post.author = get_object_or_404(User, id=author_id)
            post.interest = data.get("interest", post.interest)
            post.pic = data.get("pic", post.pic)
            post.save()
            
            return JsonResponse({"message": "Post updated successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@csrf_exempt
def delete_post(request, post_id):
    if request.method == "DELETE":
        try:
            post = get_object_or_404(Post, id=post_id)
            post.delete()
            return JsonResponse({"message": "Post deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)
