# Hotel Profile Screen — API Reference

All endpoints require authentication (`Authorization: Bearer <access_token>`).
Every response is wrapped in the standard envelope:

```json
{
  "success": true,
  "message": "…",
  "code": 200,
  "data": { … },
  "request_id": null,
  "meta": { "timestamp": "2026-08-28T10:00:00+00:00", "version": "1.0.0" }
}
```

Error envelope:

```json
{
  "success": false,
  "message": "…",
  "code": 404,
  "data": null,
  "errors": { … } | "…" | null,
  "meta": { "timestamp": "…", "version": "1.0.0" }
}
```

---

## 1. `fetchHotelProfile` — `GET /hotel/profile/{hotel_id}/`

Hotel identity/profile block. **Required** — a failure should put the screen in the error state.

### Request
| Part | Value |
|------|-------|
| Path | `hotel_id` (int) |
| Query | `platform=web` (currently ignored by the backend) |
| Body | none |

### Response `data` (200)
| Field | Type | Notes |
|-------|------|-------|
| `name` | string | |
| `phone_number` | string \| null | |
| `avatar` | string (URL) \| null | |
| `address` | string | |
| `location` | GeoJSON point \| null | `{ "type": "Point", "coordinates": [lng, lat] }` |
| `location_link` | string (URL) \| null | |
| `profile_completion` | number | percentage 0–100, computed from name / phone_number / location / avatar |

```json
{
  "name": "Idli House",
  "phone_number": "+919000000000",
  "avatar": "https://bucket.s3.region.amazonaws.com/avatars/12.jpg",
  "address": "12 MG Road",
  "location": { "type": "Point", "coordinates": [76.95, 8.52] },
  "location_link": "https://maps.google.com/…",
  "profile_completion": 75.0
}
```

> Note: the current serializer does **not** return `city`, `is_verified`, or an `id`. If the client needs those, the backend must be extended.

### Errors
| Code | When |
|------|------|
| 404 | `Hotel not found` |

---

## 2. `fetchHotelRatings` — `GET /hotel/{hotel_id}/rating/`

Aggregate rating summary plus the caller's own rating. Failure should degrade to empty ratings.

### Request
| Part | Value |
|------|-------|
| Path | `hotel_id` (int) |
| Body | none |

### Response `data` (200)
| Field | Type | Notes |
|-------|------|-------|
| `average_rating` | number \| null | `null` when there are no ratings |
| `rating_count` | int | total number of ratings |
| `user_rating` | object \| null | the caller's rating, `null` if they haven't rated (or caller is a hotel) |

`user_rating` object:
| Field | Type |
|-------|------|
| `id` | int |
| `user` | `{ id, username, avatar }` |
| `hotel` | int (hotel id) |
| `rating_count` | int (1–5) |
| `created_at` | ISO datetime |

```json
{
  "average_rating": 4.2,
  "rating_count": 18,
  "user_rating": {
    "id": 91,
    "user": { "id": 5, "username": "arjun", "avatar": "https://…" },
    "hotel": 12,
    "rating_count": 5,
    "created_at": "2026-08-20T09:12:00Z"
  }
}
```

### Errors
| Code | When |
|------|------|
| 404 | `Hotel not found` |

---

## 3. `fetchHotelReviews` — `GET /hotel/{hotel_id}/review/`

All reviews (newest first) plus the caller's own review. Failure should degrade to empty reviews.

### Request
| Part | Value |
|------|-------|
| Path | `hotel_id` (int) |
| Body | none |

### Response `data` (200)
| Field | Type | Notes |
|-------|------|-------|
| `reviews` | array | all reviews, ordered by `-created_at` |
| `user_review` | object \| null | the caller's review, `null` if none |

review object:
| Field | Type |
|-------|------|
| `id` | int |
| `user` | `{ id, username, avatar }` |
| `hotel` | int (hotel id) |
| `review_text` | string |
| `created_at` | ISO datetime |

```json
{
  "reviews": [
    {
      "id": 40,
      "user": { "id": 7, "username": "meera", "avatar": null },
      "hotel": 12,
      "review_text": "Great filter coffee.",
      "created_at": "2026-08-25T18:00:00Z"
    }
  ],
  "user_review": null
}
```

### Errors
| Code | When |
|------|------|
| 404 | `Hotel not found` |

---

## 4. `fetchHotelPosts` — `POST /post/author/?view=feed`

All published posts authored by the hotel, in feed shape. Failure should degrade to `[]`.

### Request
| Part | Value |
|------|-------|
| Query | `view=feed` |
| Body | `{ "hotel_id": <int> }` |

(`user_id` or `hotel_id` — at least one is required.)

### Response `data` (200) — array of feed posts
| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `title` | string | |
| `user` | object | `{ id, username }` — for a hotel post: `{ id: hotel_id, username: hotel_name }` |
| `avatar` | string \| null | `null` for hotel posts |
| `description` | string | |
| `media_url` | string \| null | |
| `thumbnail_url` | string \| null | |
| `comment_count` | int | |
| `like_count` | int | |
| `rating_count` | int | |
| `avg_rating` | number | |
| `media_type` | string | e.g. `image` / `video` |
| `composite_score` | number | |
| `is_liked` | bool | whether the caller liked it |
| `is_saved` | bool \| null | whether the caller saved it |
| `created_at` | ISO datetime | |
| `location` | GeoJSON point \| null | post location (geometry) |

```json
[
  {
    "id": 101,
    "title": "New menu",
    "user": { "id": 12, "username": "Idli House" },
    "avatar": null,
    "description": "Now serving…",
    "media_url": "https://…",
    "thumbnail_url": "https://…",
    "comment_count": 3,
    "like_count": 22,
    "rating_count": 4,
    "avg_rating": 4.5,
    "media_type": "image",
    "composite_score": 0.82,
    "is_liked": false,
    "is_saved": false,
    "created_at": "2026-08-27T12:00:00Z",
    "location": { "type": "Point", "coordinates": [76.95, 8.52] }
  }
]
```

> Note: `view` values other than `feed` return a compact shape (`id`, `media`) instead, where `media` is an array of `{ content_type, category, position, media_key, media_url, thumbnail_url }` objects.

### Errors
| Code | When |
|------|------|
| 400 | `user_id or hotel_id is required` |
| 500 | unexpected error |

---

## User actions (from `HotelReviewsSheet`)

### `rateHotel` — `POST /hotel/{hotel_id}/rating/`

Upsert the caller's rating (one per user per hotel).

#### Request
| Part | Value |
|------|-------|
| Path | `hotel_id` (int) |
| Body | `{ "rating_count": <1–5> }` |

#### Response `data`
- `201 Created` on first rating, `200 OK` on update.
- Body is the rating object (same shape as `user_rating` above):

```json
{
  "id": 91,
  "user": { "id": 5, "username": "arjun", "avatar": "https://…" },
  "hotel": 12,
  "rating_count": 4,
  "created_at": "2026-08-20T09:12:00Z"
}
```

#### Errors
| Code | When |
|------|------|
| 403 | `Only users can rate hotels` (caller is a hotel) |
| 404 | `Hotel not found` |
| 400 | `Validation error` (missing / out-of-range `rating_count`) |
| 500 | unexpected error |

Client flow: optimistic update in `submitRating`, rolled back on error, then re-fetch `fetchHotelRatings`.

---

### `reviewHotel` — `POST /hotel/{hotel_id}/review/`

Upsert the caller's review (one per user per hotel).

#### Request
| Part | Value |
|------|-------|
| Path | `hotel_id` (int) |
| Body | `{ "review_text": "<string>" }` |

#### Response `data`
- `201 Created` on first review, `200 OK` on update.
- Body is the review object:

```json
{
  "id": 40,
  "user": { "id": 7, "username": "meera", "avatar": null },
  "hotel": 12,
  "review_text": "Great filter coffee.",
  "created_at": "2026-08-25T18:00:00Z"
}
```

#### Errors
| Code | When |
|------|------|
| 403 | `Only users can review hotels` (caller is a hotel) |
| 404 | `Hotel not found` |
| 400 | `Validation error` (missing / empty `review_text`) |
| 500 | unexpected error |

Client flow: `submitReview` re-fetches `fetchHotelReviews` after success.
