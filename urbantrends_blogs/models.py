from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class BlogPost(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_posts"
    )
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(
        upload_to="blog_images/",
        null=True,
        blank=True
    )
    relevant_link = models.URLField(
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"


class Like(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user} liked {self.post}"