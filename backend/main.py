from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import get_connection

app = FastAPI()

# Serve templates and static CSS
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# -------------------------------
# LOGIN PAGE (GET)
# -------------------------------
@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Optional – also allow GET /login
@app.get("/login")
def login_page_alt(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------------------
# LOGIN PROCESS (POST)
# -------------------------------
@app.post("/login")
def login(request: Request, username: str = Form(), password: str = Form()):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        # Store username in cookie
        response = RedirectResponse(url="/menu", status_code=302)
        response.set_cookie("username", username)
        return response

    # Login failed
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": "Invalid username or password"}
    )


# -------------------------------
# MENU PAGE
# -------------------------------
@app.get("/menu")
def menu(request: Request):
    username = request.cookies.get("username")

    if not username:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        "menu.html", {"request": request, "username": username}
    )


# ====================================================
#                    WITHDRAW
# ====================================================

# -------------------------------
# WITHDRAW PAGE
# -------------------------------
@app.get("/withdraw")
def withdraw_page(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/")
    return templates.TemplateResponse("withdraw.html", {"request": request})


# -------------------------------
# WITHDRAW PROCESS
# -------------------------------
@app.post("/withdraw")
def withdraw(request: Request,
             account_type: str = Form(),
             amount: float = Form()):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT balance FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if not user:
        return RedirectResponse("/")

    current_balance = user["balance"]

    if current_balance < amount:
        return templates.TemplateResponse(
            "withdraw_result.html",
            {
                "request": request,
                "message": "❌ Insufficient Balance",
                "remaining_balance": None
            }
        )

    new_balance = current_balance - amount

    cursor.execute("UPDATE users SET balance=%s WHERE username=%s",
                   (new_balance, username))
    db.commit()

    return templates.TemplateResponse(
        "withdraw_result.html",
        {
            "request": request,
            "message": "Withdrawal Successful!",
            "remaining_balance": new_balance
        }
    )


# ====================================================
#                    DEPOSIT
# ====================================================

# -------------------------------
# DEPOSIT PAGE
# -------------------------------
@app.get("/deposit")
def deposit_page(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/")
    return templates.TemplateResponse("deposit.html", {"request": request})


# -------------------------------
# DEPOSIT PROCESS
# -------------------------------
@app.post("/deposit")
def deposit(request: Request,
            account_type: str = Form(),
            amount: float = Form()):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT balance FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if not user:
        return RedirectResponse("/")

    new_balance = user["balance"] + amount

    cursor.execute("UPDATE users SET balance=%s WHERE username=%s",
                   (new_balance, username))
    db.commit()

    return templates.TemplateResponse(
        "deposit_result.html",
        {"request": request, "balance": new_balance}
    )


# ====================================================
#                    BALANCE ENQUIRY
# ====================================================

# -------------------------------
# BALANCE PAGE
# -------------------------------
@app.get("/balance")
def balance_page(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/")
    return templates.TemplateResponse("balance.html", {"request": request})


# -------------------------------
# BALANCE PROCESS
# -------------------------------
@app.post("/balance")
def balance(request: Request, pin: str = Form()):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT balance FROM users WHERE username=%s AND pin=%s",
        (username, pin)
    )
    user = cursor.fetchone()

    if not user:
        return templates.TemplateResponse(
            "balance_result.html",
            {"request": request, "balance": None, "message": "❌ Incorrect PIN"}
        )

    return templates.TemplateResponse(
        "balance_result.html",
        {"request": request, "balance": user["balance"]}
    )
