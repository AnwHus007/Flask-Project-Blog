from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
# from .models import Post, User, Comment, Like
from bson import ObjectId
from . import posts,users,comments,likes


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    # posts = Post.query.all()
    posts_data = posts.find()
    user_likes=likes.find({'author':current_user.id})
    CT = [users['post_id'] for users in user_likes]
    user_likes=CT
    print(user_likes)
    posts_list = list(posts_data)
    for i in range(0,len(posts_list)):
        posts_list[i]['username']=users.find_one({'email':posts_list[i]['author']})['username']
        commentTemp=comments.find({'post_id':posts_list[i]['_id']})
        CT = [comments for comments in commentTemp]
        posts_list[i]['comments']=CT
    return render_template("home.html", user=current_user, posts=posts_list,user_likes=user_likes)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            # post = Post(text=text, author=current_user.id)
            # db.session.add(post)
            # db.session.commit()
            post_data = {
                "text": text,
                "author": current_user.id,
                "comments": [],
                "likes": int("0")
            }
            posts.insert_one(post_data)
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    # post = Post.query.filter_by(id=id).first()
    post = posts.find_one({"_id": ObjectId(id)})
    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post["author"]:
        flash('You do not have permission to delete this post.', category='error')
    else:
        # db.session.delete(post)
        # db.session.commit()
        comments.delete_many({"post_id": ObjectId(id)})
        likes.delete_many({"post_id": ObjectId(id)})
        posts.delete_one({"_id": ObjectId(id)})
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def post(username):
    # user = User.query.filter_by(username=username).first()
    user = users.find_one({"username":username})['email']
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    post = posts.find({"author":user})
    return render_template("posts.html", user=current_user, posts=post, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        # post = Post.query.filter_by(id=post_id)
        post = posts.find_one({"_id": ObjectId(post_id)})
        if post:
            # comment = Comment(
            # text=text, author=current_user.id, post_id=post_id)
            # db.session.add(comment)
            # db.session.commit()
            comment_data = {
                "text": text,
                "author": current_user.id,
                "post_id": ObjectId(post_id)
            }
            comment_data['author'] = users.find_one({'email':comment_data['author']})['username']
            print(comment_data)
            comments.insert_one(comment_data)
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    # comment = Comment.query.filter_by(id=comment_id).first()
    comment = comments.find_one({"_id": ObjectId(comment_id)})
    comment['author'] = users.find_one({'username':comment['author']})['email']
    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment['author'] and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        # db.session.delete(comment)
        # db.session.commit()
        comments.delete_one({"_id": ObjectId(comment_id)})

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['GET'])
@login_required
def like(post_id):
    # post = Post.query.filter_by(id=post_id).first()
    # like = Like.query.filter_by(
    # author=current_user.id, post_id=post_id).first()
    post = posts.find_one({"_id": ObjectId(post_id)})
    like = likes.find_one({"author": current_user.id, "post_id": ObjectId(post_id)})
    if not post:
        flash('Post does not exist.', category='error')
    elif like:
        # db.session.delete(like)
        # db.session.commit()
    
        likes.delete_one({"author": current_user.id})
        posts.update_one({"_id": ObjectId(post_id)},{"$inc": {"likes": -1}})
    else:
        # like = Like(author=current_user.id, post_id=post_id)
        # db.session.add(like)
        # db.session.commit()
        like_data = {
            "author": current_user.id,
            "post_id": ObjectId(post_id)
        }
        likes.insert_one(like_data)
        posts.update_one({"_id": ObjectId(post_id)},{"$inc": {"likes": 1}})

    return redirect(url_for('views.home'))