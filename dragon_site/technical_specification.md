# Dragon Motorcycle Website - Technical Specification

## Project Overview
A modern web application for documenting annual motorcycle trips with public galleries, interactive maps, rider profiles, and secure member areas.

## Technical Architecture

### Backend Stack (Python/FastAPI)
- **Framework**: FastAPI 0.100+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh mechanism
- **File Storage**: Local filesystem or cloud storage (S3/CloudFlare)
- **Image Processing**: Pillow for thumbnails and optimization
- **Maps Integration**: Google Maps API or OpenStreetMap
- **Testing**: pytest with async support

### Frontend Stack (React/JavaScript)
- **Framework**: React 18+ with Vite
- **Routing**: React Router v6
- **State Management**: React Context + useReducer or Zustand
- **UI Components**: Material-UI or Tailwind CSS + Headless UI
- **Maps**: React-Leaflet or Google Maps React
- **Media**: React-image-gallery, video.js
- **Forms**: React Hook Form with validation
- **HTTP Client**: Axios with interceptors

## Database Schema

### Core Entities

#### Users
```sql
- id (UUID, primary key)
- username (string, unique)
- email (string, unique)
- password_hash (string)
- first_name (string)
- last_name (string)
- is_member (boolean)
- is_admin (boolean)
- profile_photo_url (string, optional)
- created_at (timestamp)
- updated_at (timestamp)
```

#### Trips
```sql
- id (UUID, primary key)
- year (integer, unique)
- title (string)
- description (text)
- start_date (date)
- end_date (date)
- total_miles (integer)
- route_data (jsonb) -- GPS coordinates, waypoints
- cover_photo_url (string)
- is_published (boolean)
- created_at (timestamp)
- updated_at (timestamp)
```

#### Riders
```sql
- id (UUID, primary key)
- user_id (UUID, foreign key to users.id)
- trip_id (UUID, foreign key to trips.id)
- nickname (string)
- bio (text)
- miles_ridden (integer)
- created_at (timestamp)
```

#### Motorcycles
```sql
- id (UUID, primary key)
- rider_id (UUID, foreign key to riders.id)
- make (string)
- model (string)
- year (integer)
- color (string)
- engine_size (string)
- photo_url (string)
- description (text)
- is_primary (boolean)
```

#### Photos
```sql
- id (UUID, primary key)
- trip_id (UUID, foreign key to trips.id)
- uploader_id (UUID, foreign key to users.id)
- filename (string)
- original_url (string)
- thumbnail_url (string)
- caption (text)
- location_name (string)
- latitude (decimal, optional)
- longitude (decimal, optional)
- taken_at (timestamp)
- is_private (boolean)
- created_at (timestamp)
```

#### Videos
```sql
- id (UUID, primary key)
- trip_id (UUID, foreign key to trips.id)
- uploader_id (UUID, foreign key to users.id)
- filename (string)
- video_url (string)
- thumbnail_url (string)
- title (string)
- description (text)
- duration_seconds (integer)
- is_private (boolean)
- created_at (timestamp)
```

#### Beers
```sql
- id (UUID, primary key)
- trip_id (UUID, foreign key to trips.id)
- name (string)
- brewery (string)
- type (string) -- IPA, Lager, etc.
- rating (decimal, 1-5)
- photo_url (string)
- location_name (string)
- notes (text)
- tried_by (jsonb) -- array of user IDs
- created_at (timestamp)
```

#### Route Suggestions
```sql
- id (UUID, primary key)
- submitted_by (UUID, foreign key to users.id)
- title (string)
- description (text)
- start_location (string)
- end_location (string)
- estimated_miles (integer)
- difficulty_level (string) -- Easy, Moderate, Challenging
- road_type (string) -- Mountain, Scenic, Technical, Highway
- photo_url (string, optional)
- map_data (jsonb) -- GPS coordinates, waypoints
- status (string) -- Suggested, Planned, Completed, Archived
- vote_score (integer) -- calculated from votes
- created_at (timestamp)
- updated_at (timestamp)
```

#### Route Votes
```sql
- id (UUID, primary key)
- route_suggestion_id (UUID, foreign key to route_suggestions.id)
- user_id (UUID, foreign key to users.id)
- vote_type (string) -- upvote, downvote
- created_at (timestamp)
- UNIQUE(route_suggestion_id, user_id) -- prevent duplicate votes
```

#### Route Comments
```sql
- id (UUID, primary key)
- route_suggestion_id (UUID, foreign key to route_suggestions.id)
- user_id (UUID, foreign key to users.id)
- comment_text (text)
- created_at (timestamp)
- updated_at (timestamp)
```

#### Restaurants
```sql
- id (UUID, primary key)
- trip_id (UUID, foreign key to trips.id)
- name (string)
- address (text)
- city (string)
- state (string)
- cuisine_type (string) -- BBQ, Italian, Diner, etc.
- phone (string, optional)
- website (string, optional)
- latitude (decimal, optional)
- longitude (decimal, optional)
- photo_url (string, optional)
- price_range (string) -- $, $$, $$$, $$$$
- biker_friendly (boolean) -- parking, atmosphere
- notes (text)
- created_at (timestamp)
- updated_at (timestamp)
```

#### Restaurant Reviews
```sql
- id (UUID, primary key)
- restaurant_id (UUID, foreign key to restaurants.id)
- reviewer_id (UUID, foreign key to users.id)
- trip_id (UUID, foreign key to trips.id)
- overall_rating (decimal, 1-5)
- food_rating (decimal, 1-5)
- service_rating (decimal, 1-5)
- atmosphere_rating (decimal, 1-5)
- review_text (text)
- would_return (boolean)
- created_at (timestamp)
- updated_at (timestamp)
```

#### Recommended Dishes
```sql
- id (UUID, primary key)
- restaurant_id (UUID, foreign key to restaurants.id)
- recommender_id (UUID, foreign key to users.id)
- dish_name (string)
- description (text)
- price (decimal, optional)
- photo_url (string, optional)
- recommendation_notes (text)
- vote_score (integer) -- calculated from votes
- created_at (timestamp)
```

#### Dish Votes
```sql
- id (UUID, primary key)
- dish_id (UUID, foreign key to recommended_dishes.id)
- user_id (UUID, foreign key to users.id)
- vote_type (string) -- upvote, downvote
- created_at (timestamp)
- UNIQUE(dish_id, user_id) -- prevent duplicate votes
```

#### Restaurant Suggestions (Future Planning)
```sql
- id (UUID, primary key)
- submitted_by (UUID, foreign key to users.id)
- name (string)
- address (text, optional)
- city (string)
- state (string)
- cuisine_type (string)
- reason (text) -- why suggesting this restaurant
- website (string, optional)
- photo_url (string, optional)
- status (string) -- Suggested, Planned, Visited, Archived
- vote_score (integer)
- created_at (timestamp)
- updated_at (timestamp)
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Trips
- `GET /api/trips` - List all published trips
- `GET /api/trips/{trip_id}` - Get trip details
- `POST /api/trips` - Create new trip (admin only)
- `PUT /api/trips/{trip_id}` - Update trip (admin only)
- `DELETE /api/trips/{trip_id}` - Delete trip (admin only)

### Photos
- `GET /api/trips/{trip_id}/photos` - Get trip photos
- `POST /api/trips/{trip_id}/photos` - Upload photos
- `PUT /api/photos/{photo_id}` - Update photo metadata
- `DELETE /api/photos/{photo_id}` - Delete photo

### Videos
- `GET /api/trips/{trip_id}/videos` - Get trip videos
- `POST /api/trips/{trip_id}/videos` - Upload videos
- `PUT /api/videos/{video_id}` - Update video metadata
- `DELETE /api/videos/{video_id}` - Delete video

### Riders
- `GET /api/trips/{trip_id}/riders` - Get trip riders
- `GET /api/riders/{rider_id}` - Get rider profile
- `POST /api/trips/{trip_id}/riders` - Add rider to trip
- `PUT /api/riders/{rider_id}` - Update rider profile

### Motorcycles
- `GET /api/riders/{rider_id}/bikes` - Get rider's bikes
- `POST /api/riders/{rider_id}/bikes` - Add bike to rider
- `PUT /api/bikes/{bike_id}` - Update bike info
- `DELETE /api/bikes/{bike_id}` - Remove bike

### Beers
- `GET /api/trips/{trip_id}/beers` - Get trip beers
- `POST /api/trips/{trip_id}/beers` - Add beer entry
- `PUT /api/beers/{beer_id}` - Update beer info

### Route Suggestions (Members Only)
- `GET /api/routes/suggestions` - List all route suggestions with filters
- `POST /api/routes/suggestions` - Submit new route suggestion
- `GET /api/routes/suggestions/{suggestion_id}` - Get detailed route info
- `PUT /api/routes/suggestions/{suggestion_id}` - Update route suggestion (owner only)
- `DELETE /api/routes/suggestions/{suggestion_id}` - Delete suggestion (owner/admin)
- `POST /api/routes/suggestions/{suggestion_id}/vote` - Vote on route
- `GET /api/routes/suggestions/{suggestion_id}/comments` - Get route comments
- `POST /api/routes/suggestions/{suggestion_id}/comments` - Add comment
- `PUT /api/routes/comments/{comment_id}` - Update comment (owner only)
- `DELETE /api/routes/comments/{comment_id}` - Delete comment (owner/admin)

### Restaurants (Members Only)
- `GET /api/trips/{trip_id}/restaurants` - Get restaurants for trip
- `POST /api/trips/{trip_id}/restaurants` - Add restaurant to trip
- `GET /api/restaurants/{restaurant_id}` - Get restaurant details
- `PUT /api/restaurants/{restaurant_id}` - Update restaurant info
- `DELETE /api/restaurants/{restaurant_id}` - Delete restaurant (admin)
- `POST /api/restaurants/{restaurant_id}/reviews` - Add restaurant review
- `GET /api/restaurants/{restaurant_id}/reviews` - Get restaurant reviews
- `PUT /api/reviews/{review_id}` - Update review (owner only)
- `POST /api/restaurants/{restaurant_id}/dishes` - Recommend a dish
- `GET /api/restaurants/{restaurant_id}/dishes` - Get recommended dishes
- `POST /api/dishes/{dish_id}/vote` - Vote on dish recommendation

### Restaurant Suggestions (Members Only)
- `GET /api/restaurants/suggestions` - List restaurant suggestions
- `POST /api/restaurants/suggestions` - Submit restaurant suggestion
- `GET /api/restaurants/suggestions/{suggestion_id}` - Get suggestion details
- `PUT /api/restaurants/suggestions/{suggestion_id}` - Update suggestion
- `POST /api/restaurants/suggestions/{suggestion_id}/vote` - Vote on suggestion
- `GET /api/restaurants/suggestions/{suggestion_id}/comments` - Get comments
- `POST /api/restaurants/suggestions/{suggestion_id}/comments` - Add comment

## Frontend Page Structure

### Public Pages
1. **Home Page** (`/`) - Current Year Spotlight
   - Hero section with current year's featured photo
   - "This year" quick stats and highlights
   - Featured photo grid from current year (4-6 best photos)
   - Current year rider spotlight with quick cards
   - Call-to-action to explore all adventures
   - Quick navigation to main sections

2. **Trip Explorer** (`/explorer`) - Complete Historical Experience
   - **Year Selector**: Interactive slider/dropdown to choose any year
   - **Dynamic Photo Gallery**: Complete photo collection for selected year
   - **Video Collection**: All videos for selected year with playlist
   - **Interactive Maps**: Full route visualization with waypoints
   - **Rider Profiles**: Detailed rider info and bikes for selected year
   - **Statistics Dashboard**: Comprehensive data and charts for selected year
   - **Beer Archive**: Complete beer collection for selected year
   - **Restaurant Guide**: All restaurants visited during selected year with reviews and dish recommendations
   - **Trip Narrative**: Detailed story and highlights of selected year

### Private Members Area (`/members/*`)
3. **Member Dashboard** (`/members`)
   - Personal statistics
   - Private content access
   - Quick actions and notifications

4. **Route Suggestions** (`/members/routes`)
   - **Submit New Routes**: Form to suggest roads/routes for future trips
   - **Browse Suggestions**: View all submitted route ideas with photos/maps
   - **Voting System**: Upvote/downvote route suggestions
   - **Discussion Threads**: Comment and discuss each route suggestion
   - **Category Filters**: Mountain roads, scenic routes, technical challenges, etc.
   - **Status Tracking**: Mark routes as "planned", "completed", or "archived"

5. **Trip Planning** (`/members/planning`)
   - Traditional trip planning tools
   - Accommodation suggestions
   - Group coordination and logistics

6. **Private Gallery** (`/members/photos`)
   - Members-only photos/videos
   - Upload capabilities
   - Sharing controls

7. **Restaurant Hub** (`/members/restaurants`)
   - **Trip Restaurant Reviews**: Browse and review restaurants from past trips
   - **Dish Recommendations**: Vote on and discuss recommended dishes
   - **Restaurant Suggestions**: Suggest restaurants for future trips
   - **Biker-Friendly Ratings**: Special focus on parking, atmosphere, group size accommodation
   - **Cuisine Filtering**: Filter by food type, price range, location

8. **Admin Panel** (`/members/admin`)
   - User management
   - Content moderation
   - Site configuration
   - Route suggestion moderation
   - Restaurant data management

## Security Considerations

### Authentication & Authorization
- JWT tokens with short expiration (15 minutes)
- Refresh tokens with longer expiration (7 days)
- Role-based access control (public, member, admin)
- Password hashing with bcrypt
- Rate limiting on authentication endpoints

### File Upload Security
- File type validation (images: jpg, png, gif; videos: mp4, mov)
- File size limits (images: 10MB, videos: 100MB)
- Virus scanning for uploaded files
- Secure file naming to prevent directory traversal
- Image metadata stripping for privacy

### API Security
- CORS configuration for frontend domain
- Input validation and sanitization
- SQL injection prevention with parameterized queries
- XSS protection with output encoding
- CSRF protection for state-changing operations

## Performance Considerations

### Frontend Optimization
- Code splitting and lazy loading
- Image lazy loading and responsive images
- Video streaming optimization
- Service worker for caching
- Bundle size monitoring

### Backend Optimization
- Database indexing for common queries
- Image thumbnail generation
- CDN for static assets
- API response caching
- Database connection pooling

### Mobile Optimization
- Responsive design for all screen sizes
- Touch-friendly navigation
- Optimized image sizes for mobile
- Progressive Web App capabilities
- Offline viewing for cached content

## Deployment Architecture

### Production Environment
- **Backend**: Docker container on cloud platform (AWS, DigitalOcean)
- **Frontend**: Static hosting (Netlify, Vercel) or CDN
- **Database**: Managed PostgreSQL service
- **File Storage**: Cloud storage with CDN
- **Domain**: Custom domain with SSL certificate
- **Monitoring**: Application performance monitoring
- **Backups**: Automated database and file backups

### Development Environment
- Docker Compose for local development
- Hot reloading for both frontend and backend
- Local PostgreSQL database
- Mock file storage for development
- Environment-specific configuration

## Success Metrics & Analytics

### User Engagement
- Page views and session duration
- Photo/video interaction rates
- Member area usage
- Mobile vs desktop usage

### Content Metrics
- Photo upload frequency
- Video view counts
- Beer entries per trip
- Map interaction rates

### Technical Metrics
- Page load times
- API response times
- Error rates and types
- Storage usage trends