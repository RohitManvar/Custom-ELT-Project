WITH films_with_rating AS (
    SELECT
        film_id,
        title,
        release_data,
        price,
        rating,
        user_rating,
        CASE
            WHEN user_rating >= 4.5 THEN 'Excellent'
            WHEN user_rating >= 4.0 THEN 'Good'
            WHEN user_rating >= 3.0 THEN 'Average'
            ELSE 'Poor'
        END as rating_category
    FROM {{ref('films')}}
),

films_with_actors AS(
    SELECT
)