import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from PIL import Image, ImageOps, ImageDraw
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ganti-secret-key-ini")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
RESULT_FOLDER = os.path.join(BASE_DIR, "static", "hasil")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 45 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# Sesuaikan dengan konfigurasi MySQL lokal Anda (contoh default XAMPP).
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "cute_photobooth"),
}

FRAMES = {
    "pink": {
        "name": "Strawberry Milk",
        "bg": (255, 225, 235),
        "accent": (235, 123, 160),
        "label": "strawberry memories",
    },
    "lavender": {
        "name": "Lavender Dream",
        "bg": (237, 229, 255),
        "accent": (151, 124, 209),
        "label": "little happy moments",
    },
    "mint": {
        "name": "Mint Choco",
        "bg": (222, 246, 230),
        "accent": (83, 159, 129),
        "label": "sweet little memories",
    },
}
MAX_SIDE = 1200

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu ya ♡", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()[:100]
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not full_name or not username or not password or not confirm_password:
            flash("Semua kolom wajib diisi ya ♡", "danger")
            return render_template("register.html")
        if len(username) < 3 or len(username) > 30 or not username.replace("_", "").isalnum():
            flash("Username 3–30 karakter, hanya huruf, angka, dan underscore.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password minimal 6 karakter.", "danger")
            return render_template("register.html")
        if password != confirm_password:
            flash("Konfirmasi password belum sama.", "danger")
            return render_template("register.html")

        conn = None
        cur = None
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                flash("Username sudah digunakan. Coba username lain ya.", "danger")
                return render_template("register.html")
            cur.execute(
                "INSERT INTO users (full_name, username, password_hash) VALUES (%s, %s, %s)",
                (full_name, username, generate_password_hash(password))
            )
            conn.commit()
            flash("Akun berhasil dibuat! Silakan login ♡", "success")
            return redirect(url_for("login"))
        except Error:
            app.logger.exception("Gagal membuat akun")
            flash("Pendaftaran gagal. Pastikan database sudah diperbarui dan MySQL aktif.", "danger")
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        conn = None
        cur = None
        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, full_name, username, password_hash FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["full_name"] = user["full_name"]
                session["username"] = user["username"]
                flash(f"Selamat datang, {user['full_name']}! ♡", "success")
                return redirect(url_for("index"))
            flash("Username atau password salah.", "danger")
        except Error:
            app.logger.exception("Gagal login")
            flash("Tidak dapat mengakses database. Pastikan MySQL aktif dan database.sql sudah diimpor.", "danger")
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Kamu berhasil logout. Sampai jumpa lagi ♡", "success")
    return redirect(url_for("login"))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def make_photostrip(source_paths, output_path, frame_key, caption, photo_shape="rounded"):
    frame = FRAMES.get(frame_key, FRAMES["pink"])
    bg, accent = frame["bg"], frame["accent"]

    margin, gap, top = 34, 18, 115
    w, h = 420, 310
    canvas_w = margin * 2 + w * 2 + gap
    canvas_h = top + h * 2 + gap + 130

    canvas = Image.new("RGB", (canvas_w, canvas_h), bg)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 28), frame["label"], fill=accent)
    draw.text((margin, 62), (caption or "my cute day")[:45],
              fill=(52, 70, 92))

    positions = [
        (margin, top),
        (margin + w + gap, top),
        (margin, top + h + gap),
        (margin + w + gap, top + h + gap),
    ]

    for i, (x, y) in enumerate(positions):
        path = source_paths[i % len(source_paths)]

        with Image.open(path) as img:
            original = ImageOps.exif_transpose(img).convert("RGB")

        if photo_shape == "square":
            side = 290
            photo = ImageOps.fit(
                original, (side, side),
                method=Image.Resampling.LANCZOS
            )
            px, py = x + (w-side)//2, y + (h-side)//2
            canvas.paste(photo, (px, py))
            draw.rectangle(
                (px, py, px+side-1, py+side-1),
                outline="white", width=6
            )

        elif photo_shape == "polaroid":
            card = Image.new("RGB", (w, h), "white")
            photo = ImageOps.fit(
                original, (w-34, h-62),
                method=Image.Resampling.LANCZOS
            )
            card.paste(photo, (17, 15))
            ImageDraw.Draw(card).text(
                (18, h-39), "little memory", fill=accent
            )
            canvas.paste(card, (x, y))

        else:
            photo = ImageOps.fit(
                original, (w, h),
                method=Image.Resampling.LANCZOS
            )
            mask = Image.new("L", (w, h), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, w-1, h-1), radius=28, fill=255
            )
            canvas.paste(photo, (x, y), mask)

        draw.ellipse((x+12, y+12, x+42, y+42), fill=accent)
        draw.text((x+22, y+18), str(i+1), fill="white")

    draw.text((margin, canvas_h-70), "made with love", fill=accent)
    draw.text(
        (margin, canvas_h-42),
        datetime.now().strftime("%d %b %Y - %H:%M"),
        fill=(112, 91, 112)
    )
    canvas.save(output_path, quality=92)

@app.route("/")
@login_required
def index():
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, guest_name, caption, frame_style, result_file, created_at FROM sessions ORDER BY created_at DESC LIMIT 6")
        recent = cur.fetchall()
        cur.close()
        conn.close()
    except Error:
        recent = []
        flash("Database belum tersambung. Pastikan MySQL aktif dan database.sql sudah diimpor.", "warning")
    return render_template("index.html", frames=FRAMES, recent=recent)



@app.route("/buat", methods=["POST"])
@login_required
def create():
    guest_name = (request.form.get("guest_name") or "Guest").strip()[:60]
    caption = (request.form.get("caption") or "my cute day").strip()[:45]

    frame_style = request.form.get("frame_style", "pink")
    if frame_style not in FRAMES:
        frame_style = "pink"

    photo_shape = request.form.get("photo_shape", "rounded")
    if photo_shape not in {"square", "rounded", "polaroid"}:
        photo_shape = "rounded"

    # Ambil beberapa foto dari form HTML.
    photos = [
        p for p in request.files.getlist("photos")
        if p and p.filename
    ]

    # Mendukung form HTML versi lama.
    if not photos:
        old_photo = request.files.get("photo")
        if old_photo and old_photo.filename:
            photos = [old_photo]

    if not 1 <= len(photos) <= 4:
        flash("Pilih minimal 1 dan maksimal 4 foto ya ♡", "danger")
        return redirect(url_for("index"))

    for photo in photos:
        if not allowed_file(photo.filename):
            flash("Format foto harus JPG, JPEG, PNG, atau WEBP.", "danger")
            return redirect(url_for("index"))

        photo.seek(0, os.SEEK_END)
        size = photo.tell()
        photo.seek(0)

        if size > 10 * 1024 * 1024:
            flash("Setiap foto maksimal 10 MB.", "danger")
            return redirect(url_for("index"))

    token = uuid.uuid4().hex
    saved_paths = []
    upload_names = []
    result_name = f"photostrip_{token}.jpg"
    result_path = os.path.join(RESULT_FOLDER, result_name)

    conn = None
    cur = None

    try:
        # Simpan semua foto yang diunggah.
        for i, photo in enumerate(photos, start=1):
            ext = secure_filename(photo.filename).rsplit(".", 1)[1].lower()
            filename = f"{token}_{i}.{ext}"
            path = os.path.join(UPLOAD_FOLDER, filename)

            photo.save(path)
            saved_paths.append(path)
            upload_names.append(filename)

            # Periksa apakah file benar-benar gambar.
            with Image.open(path) as img:
                img.verify()

        # BAGIAN PENTING: panggil fungsi dengan 5 argumen yang benar.
        make_photostrip(
            saved_paths,
            result_path,
            frame_style,
            caption,
            photo_shape
        )

        # Simpan informasi hasil ke database.
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO sessions
            (guest_name, caption, frame_style, upload_file, result_file)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                guest_name or "Guest",
                caption or "my cute day",
                frame_style,
                upload_names[0],
                result_name
            )
        )

        session_id = cur.lastrowid
        conn.commit()

        return redirect(url_for("result", session_id=session_id))

    except (Error, OSError, ValueError, TypeError) as exc:
        if conn:
            conn.rollback()

        app.logger.exception("Gagal membuat photostrip: %s", exc)

        for path in saved_paths + [result_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

        flash(
            "Photostrip gagal dibuat. Periksa terminal untuk detail error.",
            "danger"
        )
        return redirect(url_for("index"))

    finally:
        if cur:
            cur.close()

        if conn and conn.is_connected():
            conn.close()



@app.route("/hasil/<int:session_id>")
@login_required
def result(session_id):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
        item = cur.fetchone()
        cur.close()
        conn.close()
    except Error:
        item = None
    if not item:
        flash("Hasil tidak ditemukan.", "danger")
        return redirect(url_for("index"))
    item["frame_name"] = FRAMES.get(item["frame_style"], FRAMES["pink"])["name"]
    return render_template("result.html", item=item)

@app.route("/galeri")
@login_required
def gallery():
    # Fitur baru: pencarian berdasarkan nama/caption dan filter tema frame.
    keyword = (request.args.get("q") or "").strip()[:60]
    frame_style = (request.args.get("frame") or "").strip()

    if frame_style not in {"", *FRAMES.keys()}:
        frame_style = ""
        flash("Pilihan tema tidak dikenali. Filter tema direset.", "warning")

    query = """
        SELECT id, guest_name, caption, frame_style, result_file, created_at
        FROM sessions
        WHERE 1=1
    """
    params = []

    if keyword:
        query += " AND (guest_name LIKE %s OR caption LIKE %s)"
        search_value = f"%{keyword}%"
        params.extend([search_value, search_value])

    if frame_style:
        query += " AND frame_style = %s"
        params.append(frame_style)

    query += " ORDER BY created_at DESC"

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, tuple(params))
        items = cur.fetchall()
    except Error:
        items = []
        flash("Database belum tersambung.", "warning")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template(
        "gallery.html",
        items=items,
        keyword=keyword,
        selected_frame=frame_style,
        result_count=len(items),
        has_filter=bool(keyword or frame_style)
    )

@app.route("/download/<path:filename>")
@login_required
def download(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

@app.errorhandler(413)
def too_large(_error):
    flash("Ukuran foto maksimal 10 MB.", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
