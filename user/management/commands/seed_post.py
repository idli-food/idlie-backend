import random
import uuid
from faker import Faker
from django.contrib.gis.geos import Point
from geopy.distance import geodesic
from django.core.management.base import BaseCommand
from post.models import Post, PostMedia
from user.models import User

fake = Faker()


# Base location -> Kochi
BASE_LAT = 9.9312
BASE_LON = 76.2673


food_spots = [
    "Paragon Restaurant",
    "Rahmath Hotel",
    "Burger Junction",
    "Alakapuri",
    "Cafe 17",
    "KFC Edappally",
    "Pizza Hut",
    "Arabian Palace",
    "Beyond Burg",
    "Zaatar",
    "Thaff Delicacy",
    "Hotel Galaxy",
    "Burger Lounge",
    "Mehfil Biriyani",
    "Cafe Papaya",
]


titles = [
    "Amazing chicken biriyani",
    "Best alfaham in town",
    "Late night shawarma vibes",
    "Crispy beef burger review",
    "Tried the viral pizza",
    "Perfect evening snack",
    "Budget friendly meals",
    "Best cafe ambience",
    "Spicy grilled chicken",
    "Loaded fries experience",
]


descriptions = [
    fake.paragraph(nb_sentences=3),
    fake.paragraph(nb_sentences=4),
    fake.paragraph(nb_sentences=2),
]


def generate_random_location(base_lat, base_lon):
    """
    Generate random point between 1km and 15km
    from base location.
    """

    distance_km = random.uniform(1, 15)
    bearing = random.uniform(0, 360)

    destination = geodesic(kilometers=distance_km).destination(
        (base_lat, base_lon),
        bearing
    )

    return Point(destination.longitude, destination.latitude)






class Command(BaseCommand):

    help = "Seed fake posts"

    def handle(self, *args, **kwargs):

        user_ids = list(User.objects.values_list("id", flat=True))
        if not user_ids:
            self.stderr.write(self.style.ERROR("No users found, cannot seed posts."))
            return

        posts = []
        media_specs = []

        for _ in range(20):

            # Weighted status distribution
            status = random.choices(
                ["published", "draft", "archived"],
                weights=[70, 20, 10],
                k=1
            )[0]

            media_type = random.choice(["image", "video"])

            extension = "png" if media_type == "image" else "mp4"

            category = "video" if media_type == "video" else random.choice(["instant", "photos"])

            post = Post(
                user_id=random.choice(user_ids),

                foodspot_tag=random.choice(food_spots),

                title=random.choice(titles),

                description=random.choice(descriptions),

                status=status,

                like_count=0,

                avg_rating=0.0,

                rating_count=0,

                composite_score=0.0,

                location=generate_random_location(BASE_LAT, BASE_LON),
            )

            posts.append(post)
            media_specs.append((media_type, category, extension))


        # Bulk insert
        Post.objects.bulk_create(posts)

        PostMedia.objects.bulk_create([
            PostMedia(
                post=post,
                content_type=media_type,
                category=category,
                position=0,
                media_key=f"upload/{uuid.uuid4().hex}.{extension}",
                is_processed=True,
            )
            for post, (media_type, category, extension) in zip(posts, media_specs)
        ])

        print("20 fake posts created successfully")




