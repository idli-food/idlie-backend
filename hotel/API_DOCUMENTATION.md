# Hotel App API Documentation

Base path: `/hotel/` (adjust per your root `urls.py` include prefix)

All endpoints return a common envelope from `core.utils.api_response`:

**Success envelope**
```json
{
  "success": true,
  "message": "string",
  "code": 200,
  "data": {},
  "request_id": null,
  "meta": { "timestamp": "ISO-8601", "version": "1.0.0" }
}
```

**Error envelope**
```json
{
  "success": false,
  "message": "string",
  "code": 400,
  "data": null,
  "errors": {},
  "meta": { "timestamp": "ISO-8601", "version": "1.0.0" }
}
```

---

## 1. Signup (Request OTP for new hotel)

`POST /hotel/signup/` — name: `signup`

Sends an OTP to a phone number that is not yet registered, as the first step of hotel account creation.

**View:** `hotel/authentication/views/signup.py::SignupView`

### Request body
| Field | Type | Required | Notes |
|---|---|---|---|
| `phone_number` | string | yes | Must pass `OTPServices.validate_phonenumber` |

```json
{ "phone_number": "9876543210" }
```

### Responses

**200 — OTP sent**
```json
{
  "success": true,
  "message": "otp send",
  "code": 200,
  "data": null,
  "request_id": "<otp request id>",
  "meta": { "timestamp": "...", "version": "1.0.0" }
}
```

**400 — invalid phone number**
```json
{ "success": false, "message": "invalid phone number pls check", "data": "9876543210", "errors": null, "code": 400 }
```

**400 — phone number already registered**
```json
{ "success": false, "message": "phone number already taken", "data": "login", "errors": null, "code": 400 }
```
> `data: "login"` is a hint to the client to redirect the user to the login flow instead.

**400 — OTP generation failed**
```json
{ "success": false, "message": "Unexpected error occured", "code": 400 }
```

---

## 2. Validate OTP (Signup)

`POST /hotel/validate-otp/` — name: `validate-otp`

Validates the OTP sent during signup and issues a short‑lived `request_id` used to authorize the subsequent `create/` (hotel creation) call.

**View:** `hotel/authentication/views/validate_otp.py::ValidateOTPView`

### Request body
| Field | Type | Required | Notes |
|---|---|---|---|
| `otp` | string | yes | Raises `KeyError` (500) if missing — see note below |
| `phone_number` | string | yes | Raises `KeyError` (500) if missing — see note below |

```json
{ "otp": "123456", "phone_number": "9876543210" }
```

> ⚠️ Unlike other views, this one uses `request.data["otp"]` / `request.data["phone_number"]` (bracket access), so a missing key throws an unhandled `KeyError` → Django returns a 500, not a clean `error_response`.

### Responses

**200 — OTP verified**
```json
{
  "success": true,
  "message": "OTP verfied",
  "code": 200,
  "data": null,
  "request_id": "<request id for hotel creation>",
  "meta": { "timestamp": "...", "version": "1.0.0" }
}
```

**400 — OTP not provided** (only triggers if `otp` is falsy, e.g. empty string, not if key is absent)
```json
{ "success": false, "message": "OTP not provided", "code": 400 }
```

**400 — wrong OTP**
```json
{ "success": false, "message": "Wrong OTP", "code": 400 }
```

---

## 3. Create Hotel

`POST /hotel/create/` — name: `create-hotel`

Creates the `Hotel` record after phone verification, and returns JWT access/refresh tokens for the new hotel account.

**View:** `hotel/views/create_hotel_view.py::CreateHotelView`
**Serializer:** `hotel/serializers/hotel_serializer.py::CreateHotelSerializer`

### Request body
| Field | Type | Required | Notes |
|---|---|---|---|
| `request_id` | string | yes | Must equal the `request_id` returned by `validate-otp/`; validated via `HotelCreation.is_request_id_valid` |
| `name` | string | yes | Hotel model field |
| `address` | string | yes | Hotel model field |
| `city` | string | yes | Hotel model field |
| `phone_number` | string | no | max 20 chars |
| `email` | string | no | valid email format |
| `description` | string | no | free text |
| `location` | GeoJSON geometry (Point) | no | e.g. `{ "type": "Point", "coordinates": [lon, lat] }` |

```json
{
  "request_id": "abc123",
  "name": "Sea View Hotel",
  "address": "123 Beach Road",
  "city": "Kochi",
  "phone_number": "9876543210",
  "email": "contact@seaview.com",
  "description": "A beachfront hotel",
  "location": { "type": "Point", "coordinates": [76.2673, 9.9312] }
}
```

### Responses

**201 — Hotel created**
```json
{
  "success": true,
  "message": "Hotel created successfully",
  "code": 201,
  "data": {
    "hotel": {
      "id": 1,
      "name": "Sea View Hotel",
      "address": "123 Beach Road",
      "city": "Kochi",
      "phone_number": "9876543210",
      "email": "contact@seaview.com",
      "description": "A beachfront hotel",
      "location": { "type": "Point", "coordinates": [76.2673, 9.9312] }
    },
    "access_token": "<jwt access token>",
    "refresh_token": "<jwt refresh token>"
  },
  "meta": { "timestamp": "...", "version": "1.0.0" }
}
```

**400 — missing/invalid `request_id`**
```json
{ "success": false, "message": "request_id not provided or not valid", "code": 400 }
```

**400 — validation error** (field-level errors from the serializer)
```json
{
  "success": false,
  "message": "Validation error",
  "errors": { "name": ["This field is required."] },
  "code": 400
}
```

**500 — unexpected error**
```json
{ "success": false, "message": "An error occurred", "errors": "<exception string>", "code": 500 }
```

---

## 4. Login — Send OTP

`POST /hotel/login-otp/` — name: `login-otp`

Sends a login OTP to an already-registered hotel's phone number.

**View:** `hotel/authentication/views/login.py::SendLoginOTPView`

### Request body
| Field | Type | Required | Notes |
|---|---|---|---|
| `phone_number` | string | yes | Must pass both `OTPServices.validate_phonenumber` and `validate_phone_number` |

```json
{ "phone_number": "9876543210" }
```

### Responses

**200 — OTP sent**
```json
{ "success": true, "message": "otp send", "code": 200, "data": null }
```

**400 — invalid phone number** (fails `OTPServices.validate_phonenumber`)
```json
{ "success": false, "message": "invalid phone number pls check", "data": "9876543210", "code": 400 }
```

**400 — invalid phone number** (fails `validate_phone_number`, raw DRF response, not `error_response`)
```json
{ "message": "Invalid phone number" }
```
> ⚠️ Inconsistent with the rest of the API — this branch returns a plain `Response`, not the standard envelope.

**400 — OTP generation failed**
```json
{ "success": false, "message": "Unexpected error occured", "code": 400 }
```

---

## 5. Login — Validate OTP

`POST /hotel/validate-login-otp/` — name: `validate-login-otp`

Validates the login OTP, looks up the hotel by phone number, and issues JWT access/refresh tokens.

**View:** `hotel/authentication/views/login.py::ValidateLoginOTPView`

### Request body
| Field | Type | Required | Notes |
|---|---|---|---|
| `otp` | string | yes | |
| `phone_number` | string | yes | Used to look up the hotel id via `get_hotel_id_by_phone_number` |

```json
{ "otp": "123456", "phone_number": "9876543210" }
```

### Responses

**200 — login successful**
```json
{
  "success": true,
  "message": "Login successful",
  "code": 200,
  "data": {
    "phone_number": "9876543210",
    "id": 1,
    "access": "<jwt access token>",
    "refresh": "<jwt refresh token>"
  },
  "meta": { "timestamp": "...", "version": "1.0.0" }
}
```

**400 — OTP not provided**
```json
{ "success": false, "message": "OTP not provided", "code": 400 }
```

**400 — wrong OTP**
```json
{ "success": false, "message": "Wrong OTP", "code": 400 }
```

**400 — hotel not found for this phone number**
```json
{ "success": false, "message": "Hotel not found for this phone number", "code": 400 }
```

---

## 6. Get Hotel Profile

`GET /hotel/profile/` — name: `hotel-profile`

Returns the authenticated hotel's profile details plus a computed profile-completion percentage. Requires a valid JWT access token.

**View:** `hotel/views/get_hotel_profile.py::GetHotelProfileView`
**Serializer:** `hotel/serializers/hotel_serializer.py::HotelProfileSerializer`
**Auth:** `Authorization: Bearer <access_token>` (via `hotel.authentication.services.jwt.authentications.JWTAuthentication`); `permission_classes = [IsAuthenticated]`

### Request

No body. `request.user.id` (from the decoded JWT `user_id`) is used to look up the `Hotel`.

### Responses

**200 — profile fetched**
```json
{
  "success": true,
  "message": "Hotel profile fetched successfully",
  "code": 200,
  "data": {
    "name": "Sea View Hotel",
    "phone_number": "9876543210",
    "bio": "A beachfront hotel with a rooftop restaurant.",
    "location": { "type": "Point", "coordinates": [76.2673, 9.9312] },
    "nof_post": 4,
    "profile_completion": 100.0
  },
  "meta": { "timestamp": "...", "version": "1.0.0" }
}
```

- `bio` and `nof_post` come from the related `HotelProfile` row (`profile.bio`, `profile.nof_post`); if no `HotelProfile` exists yet, they default to `null` and `0`.
- `profile_completion` is computed by `hotel/services/hotel_services.py::calculate_profile_completion` from 4 fields — `name`, `phone_number`, `location`, `bio` (`nof_post` excluded, since it's a count, not a fillable detail). `filled_fields / 4 * 100`.

**401 — missing/invalid/expired token**
```json
{ "detail": "Authentication credentials were not provided." }
```
> Raised by DRF/`JWTAuthentication` directly, not the standard `error_response` envelope.

**404 — hotel not found**
```json
{ "success": false, "message": "Hotel not found", "code": 404 }
```

---

## 7. Update Hotel Profile

`PATCH /hotel/profile/` — name: `hotel-profile`

Partially updates the authenticated hotel's profile. Same URL as the GET above; only the HTTP method differs.

**View:** `hotel/views/get_hotel_profile.py::GetHotelProfileView`
**Serializer:** `hotel/serializers/hotel_serializer.py::HotelProfileSerializer`
**Auth:** `Authorization: Bearer <access_token>`; `permission_classes = [IsAuthenticated]`

### Request body
All fields optional — send only what you want to change.

| Field | Type | Writable | Notes |
|---|---|---|---|
| `name` | string | yes | `Hotel.name` |
| `phone_number` | string | yes | `Hotel.phone_number` |
| `bio` | string \| null | yes | `HotelProfile.bio`; a `HotelProfile` row is created via `get_or_create` if one doesn't exist yet |
| `location` | GeoJSON geometry (Point) | yes | `Hotel.location` |
| `nof_post` | integer | **no** | Read-only — ignored if sent; not settable by the client |

```json
{ "bio": "Now with a rooftop pool!", "phone_number": "9876500000" }
```

### Responses

**200 — profile updated**
```json
{
  "success": true,
  "message": "Hotel profile updated successfully",
  "code": 200,
  "data": {
    "name": "Sea View Hotel",
    "phone_number": "9876500000",
    "bio": "Now with a rooftop pool!",
    "location": { "type": "Point", "coordinates": [76.2673, 9.9312] },
    "nof_post": 4
  },
  "meta": { "timestamp": "...", "version": "1.0.0" }
}
```
> Note: unlike the GET response, this response does not include `profile_completion`.

**400 — validation error**
```json
{
  "success": false,
  "message": "Validation error",
  "errors": { "phone_number": ["Ensure this field has no more than 20 characters."] },
  "code": 400
}
```

**401 — missing/invalid/expired token**
```json
{ "detail": "Authentication credentials were not provided." }
```

**404 — hotel not found**
```json
{ "success": false, "message": "Hotel not found", "code": 404 }
```

---

## Notes / inconsistencies observed while documenting

1. **`validate-otp/`** uses `request.data["otp"]` (bracket indexing) instead of `.get()`, so a missing key causes an unhandled `KeyError` (HTTP 500) rather than a clean 400.
2. **`login-otp/`** has one branch (`validate_phone_number` failing) that returns a raw `Response({"message": ...})` instead of the standard `error_response` envelope — response shape differs from every other error case in this file.
3. **`validate-login-otp/`** now returns `access`/`refresh` tokens using `hotel_id` as the JWT `user_id`, but the global authenticator (`authentication/jwt/authentications.py`, registered in `settings.py`) resolves `request.user` via `User.objects.get(id=payload["user_id"])` from the `user` app, while `GetHotelProfileView` does `Hotel.objects.get(id=request.user.id)`. Unless hotel ids and user ids are guaranteed to line up, `/hotel/profile/` will 401 or 404 for hotel logins — worth reconciling with a hotel-specific authenticator or a shared identity.
4. `hotel/views/hotel_test_view.py::HotelTestView` (`GET`, returns `{"message": "Hotel test view is working!"}`) exists but is **not registered** in `urls.py`.
5. `POST /hotel/refresh-token/` (`RefreshAccessToken`) is registered but not yet documented above.
6. The `PATCH /hotel/profile/` response omits `profile_completion` (only `GET` computes and includes it) — worth adding if clients need the updated percentage right after a save.
