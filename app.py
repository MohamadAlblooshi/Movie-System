import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

DEFAULT_MOVIES = [
    {"id": 1, "title": "The Martian", "genre": "Science Fiction", "year": 2015, "rating": 4.6, "views": 980},
    {"id": 2, "title": "Skyfall", "genre": "Action", "year": 2012, "rating": 4.4, "views": 920},
    {"id": 3, "title": "The Prestige", "genre": "Mystery", "year": 2006, "rating": 4.6, "views": 810},
    {"id": 4, "title": "Oppenheimer", "genre": "Drama", "year": 2023, "rating": 4.7, "views": 1480},
    {"id": 5, "title": "Dune: Part Two", "genre": "Science Fiction", "year": 2024, "rating": 4.8, "views": 1390},
    {"id": 6, "title": "Top Gun: Maverick", "genre": "Action", "year": 2022, "rating": 4.7, "views": 1160},
    {"id": 7, "title": "The Batman", "genre": "Thriller", "year": 2022, "rating": 4.5, "views": 1090},
    {"id": 8, "title": "Everything Everywhere All at Once", "genre": "Comedy", "year": 2022, "rating": 4.4, "views": 1210},
    {"id": 9, "title": "Arrival", "genre": "Science Fiction", "year": 2016, "rating": 4.5, "views": 870},
    {"id": 10, "title": "John Wick", "genre": "Action", "year": 2014, "rating": 4.5, "views": 1025},
]

WATCH_HISTORY = [
    {"movie": "The Martian", "genre": "Science Fiction", "date": "10/08/2026", "duration": 135},
    {"movie": "Skyfall", "genre": "Action", "date": "12/08/2026", "duration": 143},
    {"movie": "The Prestige", "genre": "Mystery", "date": "14/08/2026", "duration": 130},
    {"movie": "Oppenheimer", "genre": "Drama", "date": "16/08/2026", "duration": 172},
]

if "movies" not in st.session_state:
    st.session_state.movies = [m.copy() for m in DEFAULT_MOVIES]

if "ratings" not in st.session_state:
    st.session_state.ratings = {
        "The Martian": 5,
        "Skyfall": 4,
        "The Prestige": 5,
        "Oppenheimer": 4
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


def movie_dataframe():
    return pd.DataFrame(st.session_state.movies)


def recommendations():
    rated_titles = set(st.session_state.ratings.keys())
    genre_scores = {}

    for title, score in st.session_state.ratings.items():
        movie = next((m for m in st.session_state.movies if m["title"] == title), None)
        if movie:
            genre_scores[movie["genre"]] = genre_scores.get(movie["genre"], 0) + score

    preferred = sorted(genre_scores, key=genre_scores.get, reverse=True)

    candidates = [m for m in st.session_state.movies if m["title"] not in rated_titles]
    candidates.sort(
        key=lambda m: (
            preferred.index(m["genre"]) if m["genre"] in preferred else 999,
            -m["rating"]
        )
    )
    return candidates[:5]


def user_app():
    st.title("🎬 AI Movie Recommendation System")
    st.caption("Search movies, rate content and receive personalised recommendations.")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Search & Rate", "Recommendations", "Dashboard", "Watch History"]
    )

    with tab1:
        st.subheader("Search Movies")
        query = st.text_input("Search by title, genre or release year")

        movies = st.session_state.movies
        if query:
            q = query.lower().strip()
            movies = [
                m for m in movies
                if q in m["title"].lower()
                or q in m["genre"].lower()
                or q in str(m["year"])
            ]

        st.dataframe(
            pd.DataFrame(movies)[["title", "genre", "year", "rating"]],
            use_container_width=True,
            hide_index=True
        )

        if st.session_state.movies:
            selected = st.selectbox(
                "Choose a movie to rate",
                [m["title"] for m in st.session_state.movies]
            )
            rating = st.slider("Your rating", 1, 5, 5)
            if st.button("Submit Rating", type="primary"):
                st.session_state.ratings[selected] = rating
                st.success(f"Rating saved: {selected} = {rating}/5")

    with tab2:
        st.subheader("Top Recommended Movies")
        recs = recommendations()
        if not recs:
            st.info("Rate more movies to generate recommendations.")
        else:
            st.dataframe(
                pd.DataFrame(recs)[["title", "genre", "year", "rating"]],
                use_container_width=True,
                hide_index=True
            )

    with tab3:
        st.subheader("User Dashboard")
        df = movie_dataframe()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Movies Rated", len(st.session_state.ratings))
        with c2:
            most_watched = df.sort_values("views", ascending=False).iloc[0]
            st.metric("Trending Movie", most_watched["title"])
        with c3:
            genre_views = df.groupby("genre")["views"].sum().sort_values(ascending=False)
            st.metric("Popular Genre", genre_views.index[0])

        st.markdown("#### Trending Movies")
        st.dataframe(
            df.sort_values("views", ascending=False)[["title", "genre", "views"]].head(5),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Popular Genres")
        genre_df = (
            df.groupby("genre", as_index=False)["views"]
            .sum()
            .sort_values("views", ascending=False)
        )
        st.bar_chart(genre_df.set_index("genre"))

        st.markdown("#### Rating Insights")
        rating_df = pd.DataFrame(
            [{"movie": title, "rating": score} for title, score in st.session_state.ratings.items()]
        )
        if not rating_df.empty:
            st.bar_chart(rating_df.set_index("movie"))

    with tab4:
        st.subheader("Watch History")
        st.dataframe(
            pd.DataFrame(WATCH_HISTORY),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Rating Logs")
        rating_df = pd.DataFrame(
            [{"movie": title, "rating": f"{score}/5"} for title, score in st.session_state.ratings.items()]
        )
        st.dataframe(rating_df, use_container_width=True, hide_index=True)


def admin_console():
    st.title("🛠️ Administrator Console")

    if not st.session_state.admin_logged_in:
        key = st.text_input("Administrator login key", type="password")
        if st.button("Access Admin Console"):
            if key == "MRS-ADMIN-2026":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid administrator key.")
        return

    tab1, tab2 = st.tabs(["Movie Management", "Engagement Analytics"])

    with tab1:
        st.subheader("Current Movie Database")
        st.dataframe(movie_dataframe(), use_container_width=True, hide_index=True)

        action = st.radio("Management action", ["Add", "Edit", "Remove"], horizontal=True)

        if action == "Add":
            with st.form("add_movie"):
                title = st.text_input("Title")
                genre = st.text_input("Genre")
                year = st.number_input("Release year", min_value=1900, max_value=2100, value=2026)
                rating = st.number_input("Average rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
                submitted = st.form_submit_button("Add Movie")

            if submitted and title and genre:
                next_id = max(m["id"] for m in st.session_state.movies) + 1
                st.session_state.movies.append({
                    "id": next_id,
                    "title": title,
                    "genre": genre,
                    "year": int(year),
                    "rating": float(rating),
                    "views": 0
                })
                st.success("Movie added successfully.")
                st.rerun()

        elif action == "Edit":
            selected = st.selectbox("Select movie", [m["title"] for m in st.session_state.movies])
            movie = next(m for m in st.session_state.movies if m["title"] == selected)

            with st.form("edit_movie"):
                new_title = st.text_input("Title", movie["title"])
                genre = st.text_input("Genre", movie["genre"])
                year = st.number_input("Release year", 1900, 2100, movie["year"])
                rating = st.number_input("Average rating", 0.0, 5.0, float(movie["rating"]), 0.1)
                submitted = st.form_submit_button("Save Changes")

            if submitted:
                movie.update({
                    "title": new_title,
                    "genre": genre,
                    "year": int(year),
                    "rating": float(rating)
                })
                st.success("Movie updated successfully.")
                st.rerun()

        else:
            selected = st.selectbox("Select movie to remove", [m["title"] for m in st.session_state.movies])
            if st.button("Remove Movie", type="primary"):
                st.session_state.movies = [
                    m for m in st.session_state.movies if m["title"] != selected
                ]
                st.success("Movie removed successfully.")
                st.rerun()

    with tab2:
        st.subheader("User Engagement Trends")
        df = movie_dataframe()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Views", f"{int(df['views'].sum()):,}")
        with c2:
            top = df.sort_values("views", ascending=False).iloc[0]
            st.metric("Most Watched", top["title"])
        with c3:
            genre_views = df.groupby("genre")["views"].sum().sort_values(ascending=False)
            st.metric("Top Genre", genre_views.index[0])

        st.markdown("#### Most-Watched Movies")
        top_movies = df.sort_values("views", ascending=False).head(7)
        st.bar_chart(top_movies.set_index("title")["views"])

        st.dataframe(
            top_movies[["title", "genre", "views", "rating"]],
            use_container_width=True,
            hide_index=True
        )


st.sidebar.title("MRS Navigation")
mode = st.sidebar.radio("Choose portal", ["User Application", "Administrator"])

if mode == "User Application":
    if not st.session_state.logged_in:
        st.title("Registered User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            if username == "viewer01" and password == "movie123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.caption("Demo login: viewer01 / movie123")
    else:
        if st.sidebar.button("Log out user"):
            st.session_state.logged_in = False
            st.rerun()
        user_app()
else:
    if st.session_state.admin_logged_in and st.sidebar.button("Log out administrator"):
        st.session_state.admin_logged_in = False
        st.rerun()
    admin_console()
