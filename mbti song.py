import os, csv, random, webbrowser, tkinter as tk
from tkinter import messagebox
from urllib.parse import quote_plus

CSV_PATH = r"C:\Users\김태경님\PycharmProjects\PythonProject2\korean_songs_mbti_2500 (2).csv"

def load_songs_by_mbti(path):
    if not os.path.exists(path): return {}
    data = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mbti  = (row.get("MBTI")  or "").strip().upper()
            title = (row.get("title") or "").strip()
            artist= (row.get("artist")or "").strip()
            era   = (row.get("era")   or "").strip()
            if not mbti or not title: continue
            data.setdefault(mbti, []).append((title, artist, era))
    return data

MBTI_QUESTIONS = [
    ("주기적으로 새로운 친구를 만든다.", "EI"),
    ("자유 시간 중 다양한 관심사를 탐구한다.", "NS"),
    ("다른 사람이 울면 함께 울고 싶어진다.", "FT"),
    ("일이 잘못될 때 미리 대비책을 세운다.", "JP"),
    ("압박감 속에서도 평정심을 유지하는 편이다.", "TF"),
    ("파티에서 친한 사람과만 대화하는 편이다.", "IE"),
    ("하나의 프로젝트를 끝내고 다음을 시작한다.", "JP"),
    ("감정보다는 이성으로 판단하는 편이다.", "TF"),
    ("계획을 세우기보다 즉흥을 선호한다.", "PJ"),
    ("혼자보다는 사람들과 시간을 보내고 싶어한다.", "EI"),
]

BG = "#f1eaff"
FG_MAIN = "#000000"
PURPLE  = "#7E57FF"
PINK    = "#FF5E86"
ORANGE  = "#FF914D"
ERA_CARD_BG = "#F5F0FF"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E5DAFD"   # 카드 테두리 컬러(연보라)
SHADOW = "#e9e0ff"       # 소프트 섀도우

win = tk.Tk()
win.title("MBTI SONG")
win.geometry("600x600")
win.configure(bg=BG)

FONT_TITLE = ("맑은 고딕", 18, "bold")
FONT_LABEL = ("맑은 고딕", 17, "bold")
FONT_BTN   = ("맑은 고딕", 13, "bold")
FONT_OPT   = ("맑은 고딕", 12, "bold")

header = tk.Canvas(win, height=56, highlightthickness=0, bd=0, bg=BG)
header.place(relx=0.0, rely=0.0, relwidth=1.0, height=56)

def draw_gradient(cvs, w, h):
    from_col = (123, 92, 252); mid_col = (196, 109, 189); to_col = (255, 140, 90)
    cvs.delete("grad")
    if w <= 0: return
    for i in range(w):
        t = i / max(w - 1, 1)
        if t < 0.5:
            tt = t / 0.5
            r = int(from_col[0] + (mid_col[0] - from_col[0]) * tt)
            g = int(from_col[1] + (mid_col[1] - from_col[1]) * tt)
            b = int(from_col[2] + (mid_col[2] - from_col[2]) * tt)
        else:
            tt = (t - 0.5) / 0.5
            r = int(mid_col[0] + (to_col[0] - mid_col[0]) * tt)
            g = int(mid_col[1] + (to_col[1] - mid_col[1]) * tt)
            b = int(mid_col[2] + (to_col[2] - mid_col[2]) * tt)
        cvs.create_line(i, 0, i, h, fill=f"#{r:02x}{g:02x}{b:02x}", tags="grad")
    cvs.tag_raise("title")

header_title_id = header.create_text(300, 28, text="MBTI SONG", fill="white", font=FONT_TITLE, tags="title")
header.bind("<Configure>", lambda e: (draw_gradient(header, e.width, 56), header.coords(header_title_id, e.width//2, 28)))

top_shadow = tk.Frame(win, bg=SHADOW, bd=0, relief="flat", highlightthickness=0)
top_shadow.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.88, relheight=0.46)

top_card = tk.Frame(win, bg=CARD_BG, bd=0, relief="flat", highlightthickness=2, highlightbackground=CARD_BORDER)
top_card.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.86, relheight=0.44)

question_var = tk.StringVar(value="MBTI검사")
question_label = tk.Label(top_card, textvariable=question_var, font=FONT_LABEL, bg=CARD_BG, fg=FG_MAIN, wraplength=520, justify="center")
question_label.place(relx=0.5, rely=0.33, anchor="center")

yes_btn = tk.Button(top_card, text="YES", font=FONT_BTN, bg=PURPLE, fg="white", activebackground="#6d46ff", width=10, bd=0)
play_btn = tk.Button(top_card, text="▶",   font=("Arial", 16, "bold"), bg=ORANGE, fg="white", activebackground="#ff7a2a", width=6, height=1, bd=0)
no_btn  = tk.Button(top_card, text="NO",   font=FONT_BTN, bg=PINK,   fg="white", activebackground="#ff476f", width=10, bd=0)

yes_pos  = dict(relx=0.25, rely=0.80, anchor="center")
play_pos = dict(relx=0.50, rely=0.80, anchor="center")
no_pos   = dict(relx=0.75, rely=0.80, anchor="center")

# era panel shadow + panel
era_shadow = tk.Frame(win, bg=SHADOW, bd=0, relief="flat", highlightthickness=0)
era_panel  = tk.Frame(win, bg=ERA_CARD_BG, bd=0, relief="flat", highlightthickness=2, highlightbackground=PURPLE)
tk.Label(era_panel, text="시대 선택", font=FONT_LABEL, bg=ERA_CARD_BG, fg=PURPLE).place(relx=0.05, rely=0.15, anchor="w")
era_vars = {}

def build_era_checkboxes():
    for w in era_panel.winfo_children():
        if isinstance(w, tk.Checkbutton): w.destroy()
    items = ["M세대 이전", "M세대 이후"]
    for i, text in enumerate(items):
        era_vars[text] = tk.IntVar(value=0)
        cb = tk.Checkbutton(era_panel, text=text, variable=era_vars[text], font=FONT_OPT,
                            bg=ERA_CARD_BG, fg=FG_MAIN, selectcolor="#E7DBFF",
                            activebackground=ERA_CARD_BG, activeforeground=FG_MAIN,
                            anchor="w", padx=10)
        cb.place(relx=0.07, rely=0.45 + i*0.22, anchor="w")

def show_era_panel():
    era_panel.place(relx=0.5, rely=0.8, anchor="center", relwidth=0.86, relheight=0.26)
    build_era_checkboxes()


def selected_eras():
    return [e for e,v in era_vars.items() if v.get()==1]

def _bind_hover(btn, normal, hover):
    btn.bind("<Enter>", lambda _e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda _e: btn.configure(bg=normal))

SONGS_BY_MBTI = load_songs_by_mbti(CSV_PATH)
scores = {k:0 for k in "EISNTFJP"}
q_idx = 0
mbti_result = ""
current_song_title = None
stage = "idle"

def set_stage(s):
    global stage
    stage = s
    if s == "idle":
        yes_btn.place_forget(); no_btn.place_forget()
        play_btn.place(**play_pos)
        question_label.place_configure(relx=0.5, rely=0.33)
    elif s == "quiz":
        play_btn.place_forget()
        yes_btn.place(**yes_pos)
        no_btn.place(**no_pos)
        question_label.place_configure(relx=0.5, rely=0.33)
    elif s == "select":
        yes_btn.place_forget(); no_btn.place_forget()
        play_btn.place(**play_pos)
        question_label.place_configure(relx=0.5, rely=0.28)
    elif s == "recommended":
        yes_btn.place_forget(); no_btn.place_forget()
        play_btn.place(**play_pos)
        question_label.place_configure(relx=0.5, rely=0.33)

def calculate_mbti():
    return "".join([
        'E' if scores['E']>=scores['I'] else 'I',
        'S' if scores['S']>=scores['N'] else 'N',
        'T' if scores['T']>=scores['F'] else 'F',
        'J' if scores['J']>=scores['P'] else 'P'
    ])

def pick_song_for_mbti(mbti_code, eras):
    pool = SONGS_BY_MBTI.get(mbti_code, [])
    if not pool: return None, None
    cand = [x for x in pool if (not eras or x[2] in eras)]
    if not cand: cand = pool
    t, a, _ = random.choice(cand)
    return t, a

def open_youtube(title):
    url = f"https://www.youtube.com/results?search_query={quote_plus(title)}"
    webbrowser.open(url, new=2)

def ask_next():
    global q_idx
    if q_idx < len(MBTI_QUESTIONS):
        question_var.set(MBTI_QUESTIONS[q_idx][0])
    else:
        show_mbti_result()

def on_yes():
    global q_idx
    _, pair = MBTI_QUESTIONS[q_idx]
    scores[pair[0]] += 1
    q_idx += 1
    ask_next()

def on_no():
    global q_idx
    _, pair = MBTI_QUESTIONS[q_idx]
    scores[pair[1]] += 1
    q_idx += 1
    ask_next()

def on_play():
    global mbti_result, current_song_title
    if stage == "idle":
        if not SONGS_BY_MBTI:
            messagebox.showerror("데이터 없음", f"CSV에서 데이터를 불러오지 못했습니다.\n경로: {CSV_PATH}")
            return
        set_stage("quiz"); ask_next()
    elif stage == "select":
        eras = selected_eras()
        title, artist = pick_song_for_mbti(mbti_result, eras)
        era_shadow.place_forget(); era_panel.place_forget()
        current_song_title = title
        if title: question_var.set(f"{mbti_result}\n추천 곡: “{title}”" + (f" - {artist}" if artist else ""))
        else:     question_var.set(f"{mbti_result}\n추천 곡: (없음)")
        set_stage("recommended")
    elif stage == "recommended":
        if current_song_title: open_youtube(current_song_title)

def show_mbti_result():
    global mbti_result
    mbti_result = calculate_mbti()
    question_var.set(f"당신의 MBTI는 {mbti_result} 입니다.\n아래에서 시대를 체크하고 ▶")
    show_era_panel()
    set_stage("select")

yes_btn.config(command=on_yes)
no_btn.config(command=on_no)
play_btn.config(command=on_play)

# hover
_bind_hover(yes_btn, PURPLE, "#6d46ff")
_bind_hover(no_btn,  PINK,   "#ff476f")
_bind_hover(play_btn, ORANGE, "#ff7a2a")

set_stage("idle")

SONGS_BY_MBTI = load_songs_by_mbti(CSV_PATH)
if not SONGS_BY_MBTI:
    question_var.set("CSV 로드 실패. 경로/파일 형식을 확인해 주세요.")

win.mainloop()
