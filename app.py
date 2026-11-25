import sqlite3
from datetime import date, datetime
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------
# 기본 설정 및 데이터베이스
# ---------------------------------------------------------
st.set_page_config(
    page_title="책장을 채우는 독후감",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_PATH = Path(__file__).with_name("book_reviews.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                total_pages INTEGER NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                rating INTEGER,
                one_line_review TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                UNIQUE(user_name, title, author)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reading_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                reading_date TEXT NOT NULL,
                pages_read INTEGER NOT NULL,
                memorable_scene TEXT NOT NULL,
                thoughts TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(book_id) REFERENCES books(id)
            )
        """)
        conn.commit()


def get_books(user_name, completed=None):
    with get_connection() as conn:
        if completed is None:
            rows = conn.execute(
                "SELECT * FROM books WHERE user_name=? ORDER BY created_at DESC",
                (user_name,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM books WHERE user_name=? AND completed=? ORDER BY completed_at DESC",
                (user_name, int(completed)),
            ).fetchall()
    return rows


def get_entries(book_id):
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM reading_entries
               WHERE book_id=?
               ORDER BY reading_date ASC, created_at ASC""",
            (book_id,),
        ).fetchall()


def get_book(book_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()


def save_entry(book_id, reading_date, pages_read, scene, thoughts):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO reading_entries
               (book_id, reading_date, pages_read, memorable_scene, thoughts, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                book_id,
                reading_date.isoformat(),
                pages_read,
                scene.strip(),
                thoughts.strip(),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()


def save_review(book_id, rating, one_line_review):
    with get_connection() as conn:
        conn.execute(
            """UPDATE books
               SET completed=1, rating=?, one_line_review=?, completed_at=?
               WHERE id=?""",
            (rating, one_line_review.strip(), datetime.now().isoformat(timespec="seconds"), book_id),
        )
        conn.commit()


init_db()

# ---------------------------------------------------------
# 디자인
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

:root {
    --ink: #34271f;
    --muted: #806f60;
    --paper: #f7f1e6;
    --cream: #fffaf1;
    --wood: #78533c;
    --wood-dark: #4e3528;
    --gold: #c59b58;
}
.stApp {
    background:
      radial-gradient(ellipse at top left, rgba(255,255,255,.75), transparent 45%),
      linear-gradient(135deg, #f6efe2 0%, #eee2d0 100%);
    color: var(--ink);
    font-family: 'Noto Sans KR', sans-serif;
}
.block-container { max-width: 1050px; padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { font-family: 'Gowun Batang', serif !important; color: var(--wood-dark); }
.hero {
    padding: 2rem 2.2rem;
    border-radius: 18px;
    background: linear-gradient(115deg, #5b3d2e, #866044);
    color: #fff8eb;
    box-shadow: 0 10px 24px rgba(67,43,28,.16);
    margin-bottom: 1.5rem;
}
.hero h1 { color: #fff8eb !important; margin: 0 0 .45rem 0; font-size: 2.25rem; }
.hero p { color: #f1dfc6; margin: 0; }
.shelf {
    background: linear-gradient(180deg, #9b704e 0%, #6b4833 88%, #4b3022 89%, #4b3022 100%);
    padding: 15px 15px 22px 15px;
    border-radius: 12px;
    box-shadow: inset 0 2px 5px rgba(255,255,255,.2), 0 8px 16px rgba(60,38,25,.15);
    margin: 1rem 0 1.5rem;
}
.book-spine {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    writing-mode: vertical-rl;
    height: 145px;
    min-width: 48px;
    padding: 10px 7px;
    margin: 0 5px;
    border-radius: 5px 5px 2px 2px;
    color: #fff8e8;
    font-family: 'Gowun Batang', serif;
    font-weight: 700;
    font-size: 14px;
    box-shadow: inset 4px 0 5px rgba(255,255,255,.13), inset -4px 0 5px rgba(0,0,0,.12);
    overflow: hidden;
}
.panel {
    background: rgba(255,250,241,.88);
    border: 1px solid rgba(120,83,60,.15);
    border-radius: 15px;
    padding: 1.2rem 1.4rem;
    margin: .7rem 0 1rem;
    box-shadow: 0 4px 14px rgba(77,53,35,.06);
}
.small-muted { color: #806f60; font-size: .9rem; }
div.stButton > button {
    border-radius: 10px;
    border: 1px solid #9b7658;
    background: #fffaf1;
    color: #563b2a;
    font-weight: 600;
    min-height: 2.8rem;
}
div.stButton > button:hover {
    background: #ead9c2;
    color: #3f2b20;
    border-color: #78533c;
}
div.stButton > button[kind="primary"] {
    background: #684832;
    color: #fff8eb;
    border-color: #684832;
}
div.stButton > button[kind="primary"]:hover { background: #4e3528; color: white; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input, [data-testid="stDateInput"] input {
    background: #fffdf8;
    border-radius: 9px;
}
hr { border-color: rgba(120,83,60,.2); }
.stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


def go(page):
    st.session_state.page = page
    st.rerun()


def header(title, subtitle=None):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle or "오늘의 한 페이지가 내일의 지혜가 됩니다."}</p></div>',
        unsafe_allow_html=True,
    )


def show_user():
    if st.session_state.get("logged_in"):
        st.markdown(
            f'<div style="text-align:right;color:#73563f;font-size:.95rem;">👤 {st.session_state.user_name} 님으로 로그인됨</div>',
            unsafe_allow_html=True,
        )


def shelf_for_books(books):
    if not books:
        st.markdown('<div class="shelf" style="color:#fff4df;text-align:center;">아직 책장에 꽂힌 책이 없어요. 첫 번째 책을 기록해 보세요. 📖</div>', unsafe_allow_html=True)
        return
    colors = ["#8b4d3e", "#526b5a", "#455d78", "#b08045", "#6d5878", "#557b7a", "#9b654b", "#596b8b"]
    spines = ""
    for i, book in enumerate(books):
        title = book["title"].replace("<", "&lt;").replace(">", "&gt;")
        spines += f'<span class="book-spine" style="background:{colors[i % len(colors)]};">{title}</span>'
    st.markdown(f'<div class="shelf">{spines}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# 세션 상태
# ---------------------------------------------------------
defaults = {
    "page": "login",
    "logged_in": False,
    "user_name": "",
    "login_date": date.today(),
    "selected_book_id": None,
    "detail_book_id": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# 로그인
# ---------------------------------------------------------
if not st.session_state.logged_in:
    header("나만의 독서 서재", "책 한 권, 한 문장, 한 번의 생각을 차곡차곡 모아 보세요.")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("서재에 들어가기")
    st.write("이름과 오늘 날짜를 입력하면 나만의 독서 기록장이 열립니다.")
    with st.form("login_form"):
        name = st.text_input("이름", placeholder="이름을 입력해 주세요")
        login_date = st.date_input("오늘 날짜", value=date.today())
        submitted = st.form_submit_button("서재 입장하기", type="primary", use_container_width=True)
    if submitted:
        if not name.strip():
            st.error("이름을 입력해 주세요.")
        else:
            st.session_state.user_name = name.strip()
            st.session_state.login_date = login_date
            st.session_state.logged_in = True
            st.session_state.page = "home"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("※ 같은 이름으로 다시 로그인하면 이전에 저장한 독서 기록을 이어서 볼 수 있습니다.")
    st.stop()

show_user()

# ---------------------------------------------------------
# 메뉴 / 홈
# ---------------------------------------------------------
if st.session_state.page == "home":
    header("나만의 독서 서재", f"{st.session_state.login_date.strftime('%Y년 %m월 %d일')} · 책장을 한 권씩 채워 보세요.")
    all_books = get_books(st.session_state.user_name)
    completed_books = get_books(st.session_state.user_name, completed=True)
    st.markdown("### 나의 책장")
    shelf_for_books(completed_books)
    col1, col2, col3 = st.columns(3)
    col1.metric("기록 중인 책", len([b for b in all_books if not b["completed"]]))
    col2.metric("완독한 책", len(completed_books))
    col3.metric("차곡차곡 쌓인 독후 기록", sum(len(get_entries(b["id"])) for b in all_books))
    st.write("")
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel">### ✍️ 독후감 입력\n읽은 쪽수와 인상 깊었던 장면, 생각을 기록해요.</div>', unsafe_allow_html=True)
        if st.button("독후감 입력하기", type="primary", use_container_width=True):
            go("write")
    with right:
        st.markdown('<div class="panel">### 📚 읽은 책 목록\n완독한 책과 그동안의 기록을 다시 읽어 봐요.</div>', unsafe_allow_html=True)
        if st.button("읽은 책 목록 보기", use_container_width=True):
            go("library")
    st.caption("나의 서재는 이름을 기준으로 기록을 불러옵니다. 다른 사람과 공유하는 기기에서는 로그아웃 후 이용해 주세요.")

# ---------------------------------------------------------
# 독후감 입력
# ---------------------------------------------------------
elif st.session_state.page == "write":
    header("오늘의 독서 기록", "읽은 만큼 기록하고, 마음에 남은 장면을 붙잡아 보세요.")
    user_books = get_books(st.session_state.user_name, completed=False)
    st.markdown("### 책 선택하기")
    options = {"새 책 등록하기": None}
    for b in user_books:
        options[f'{b["title"]} · {b["author"]}'] = b["id"]

    selected_label = st.selectbox("책 제목", list(options.keys()), key="book_choice")
    selected_id = options[selected_label]

    if selected_id is None:
        with st.form("new_book_form"):
            st.write("처음 기록하는 책이라면 책 정보를 입력해 주세요.")
            title = st.text_input("책 제목", placeholder="예: 긴긴밤")
            author = st.text_input("지은이", placeholder="예: 루리")
            total_pages = st.number_input("전체 쪽수", min_value=1, step=1, value=100)
            create_book = st.form_submit_button("책 정보 등록하기", type="primary")
        if create_book:
            if not title.strip() or not author.strip():
                st.error("책 제목과 지은이를 모두 입력해 주세요.")
            else:
                try:
                    with get_connection() as conn:
                        cur = conn.execute(
                            """INSERT INTO books (user_name, title, author, total_pages, created_at)
                               VALUES (?, ?, ?, ?, ?)""",
                            (st.session_state.user_name, title.strip(), author.strip(), int(total_pages), datetime.now().isoformat(timespec="seconds")),
                        )
                        conn.commit()
                        st.session_state.selected_book_id = cur.lastrowid
                    st.success("책 정보가 등록되었어요. 아래에서 오늘의 독서 기록을 작성해 주세요.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("이미 등록한 책이에요. 위 목록에서 선택해 주세요.")
        active_id = st.session_state.get("selected_book_id")
    else:
        active_id = selected_id
        st.session_state.selected_book_id = selected_id

    if active_id:
        book = get_book(active_id)
        if book and book["user_name"] == st.session_state.user_name and not book["completed"]:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown(f'**{book["title"]}**  ·  {book["author"]}')
            st.caption(f'전체 {book["total_pages"]}쪽')
            prior_entries = get_entries(active_id)
            if prior_entries:
                st.markdown("#### 이전 독후 기록")
                for entry in prior_entries:
                    with st.expander(f'{entry["reading_date"]} · {entry["pages_read"]}쪽 읽음'):
                        st.write("**인상 깊은 장면**")
                        st.write(entry["memorable_scene"])
                        st.write("**생각과 느낌**")
                        st.write(entry["thoughts"])
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("### 오늘의 기록")
            with st.form("reading_entry_form"):
                reading_date = st.date_input("읽은 날짜", value=st.session_state.login_date)
                pages_read = st.number_input("오늘 읽은 쪽수", min_value=1, max_value=int(book["total_pages"]), step=1)
                scene = st.text_area("인상 깊은 장면", placeholder="어떤 장면이 가장 기억에 남았나요?", height=110)
                thoughts = st.text_area("생각과 느낌", placeholder="읽으면서 어떤 생각이나 감정이 들었나요?", height=140)
                save = st.form_submit_button("저장", type="primary", use_container_width=True)
            if save:
                if not scene.strip() or not thoughts.strip():
                    st.error("인상 깊은 장면과 생각과 느낌을 모두 작성해 주세요.")
                else:
                    save_entry(active_id, reading_date, int(pages_read), scene, thoughts)
                    st.success("독후 기록이 서재에 저장되었어요.")
                    st.rerun()

            if st.button("다 읽었어요", use_container_width=True):
                st.session_state.selected_book_id = active_id
                go("review")
        else:
            st.info("책 정보를 등록하거나 읽을 책을 선택해 주세요.")

    st.divider()
    if st.button("홈으로 가기"):
        go("home")

# ---------------------------------------------------------
# 책 평가
# ---------------------------------------------------------
elif st.session_state.page == "review":
    book_id = st.session_state.get("selected_book_id")
    book = get_book(book_id) if book_id else None
    if not book or book["user_name"] != st.session_state.user_name:
        st.warning("평가할 책을 찾을 수 없어요.")
        if st.button("홈으로 가기"):
            go("home")
    else:
        header("책과 마지막 인사", "한 권의 책을 덮으며, 나만의 별점과 한 줄을 남겨 보세요.")
        st.markdown(f'### 📖 {book["title"]}')
        st.caption(f'지은이: {book["author"]} · 전체 {book["total_pages"]}쪽')
        with st.form("book_review_form"):
            rating = st.slider("책에 대한 전체 평점", min_value=0, max_value=10, value=8, step=1)
            one_line = st.text_input("한줄평", placeholder="이 책을 한 문장으로 표현한다면?")
            submitted = st.form_submit_button("평가 저장하기", type="primary", use_container_width=True)
        if submitted:
            if not one_line.strip():
                st.error("한줄평을 작성해 주세요.")
            else:
                save_review(book_id, rating, one_line)
                st.session_state.review_saved = True
                st.rerun()
        if st.session_state.get("review_saved"):
            st.balloons()
            st.success("✨ 저장되었습니다! 책 한 권이 나의 서가에 더해졌어요.")
            if st.button("읽은 책 목록으로 가기", type="primary"):
                st.session_state.review_saved = False
                go("library")
        if st.button("독후감으로 돌아가기"):
            go("write")

# ---------------------------------------------------------
# 읽은 책 목록 및 상세 기록
# ---------------------------------------------------------
elif st.session_state.page == "library":
    header("내가 읽은 책", "완독한 책들이 나만의 서가를 이루고 있어요.")
    books = get_books(st.session_state.user_name, completed=True)
    shelf_for_books(books)
    if not books:
        st.info("아직 평가를 마친 책이 없어요. 책을 다 읽고 별점과 한줄평을 남기면 이곳에 모입니다.")
    else:
        st.markdown("### 책 목록")
        for book in books:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f'**📕 {book["title"]}**')
                    st.caption(f'{book["author"]} · ⭐ {book["rating"]}/10')
                    st.write(book["one_line_review"])
                with c2:
                    if st.button("기록 보기", key=f'open_{book["id"]}'):
                        st.session_state.detail_book_id = book["id"]
                        go("detail")
                st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    if st.button("홈으로 가기"):
        go("home")

elif st.session_state.page == "detail":
    book_id = st.session_state.get("detail_book_id")
    book = get_book(book_id) if book_id else None
    if not book or book["user_name"] != st.session_state.user_name:
        st.warning("책 기록을 찾을 수 없어요.")
    else:
        header("한 권의 독서 여정", "날짜 순서대로 다시 읽으며 그때의 나를 만나 보세요.")
        st.markdown(f'## 📕 {book["title"]}')
        st.write(f'**지은이:** {book["author"]}　 **전체 쪽수:** {book["total_pages"]}쪽')
        st.write(f'**나의 평점:** ⭐ {book["rating"]}/10')
        st.markdown(f'> {book["one_line_review"]}')
        st.divider()
        entries = get_entries(book_id)
        st.markdown("### 날짜별 독후 기록")
        if not entries:
            st.info("저장된 독후 기록이 없습니다.")
        for i, entry in enumerate(entries, start=1):
            st.markdown(f'#### {i}. {entry["reading_date"]} · {entry["pages_read"]}쪽 읽음')
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("**인상 깊은 장면**")
                st.write(entry["memorable_scene"])
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("**생각과 느낌**")
                st.write(entry["thoughts"])
                st.markdown('</div>', unsafe_allow_html=True)
        st.divider()
        if st.button("읽은 책 목록으로 돌아가기"):
            go("library")
        if st.button("홈으로 가기"):
            go("home")
