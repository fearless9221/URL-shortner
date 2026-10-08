import mysql.connector
import redis
from fastapi import FastAPI, Path, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class longURL(BaseModel):
    long_url: str

def get_short(count: int):
    count+=56801235584
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    s = ""
    while count > 0:
        c = count % 62
        s += base[c]
        count //= 62
    return s[::-1]

def log_click_background(short_code: str, ip_address: str):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",        
            password="2703#Harsh",
            database="url_shortener"
        )
        cursor = db.cursor()
        insert_query = "INSERT INTO clicks (short_url, ip_address) VALUES (%s, %s)"
        cursor.execute(insert_query, (short_code, ip_address))
        db.commit()
    except Exception as e:
        print(f"Background logging failed: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals(): db.close()

@app.post("/shorten")
def create_short_url(request: longURL):
    db = mysql.connector.connect(
        host="localhost",
        user="root",        
        password="2703#Harsh",
        database="url_shortener"
    )
    cursor = db.cursor()

    search_query = "SELECT short_url FROM URLs WHERE long_url = %s"
    cursor.execute(search_query, (request.long_url,)) 
    existing_row = cursor.fetchone()
    
    if existing_row:
        cursor.close()
        db.close()
        return {"short_url": f"http://localhost:8000/r/{existing_row[0]}"}

    insert_query = "INSERT INTO URLs (short_url, long_url) VALUES (%s, %s)"
    cursor.execute(insert_query, ("temp", request.long_url))
    db.commit()

    new_id = cursor.lastrowid
    final_short_code = get_short(new_id)

    update_query = "UPDATE URLs SET short_url = %s WHERE id = %s"
    cursor.execute(update_query, (final_short_code, new_id))
    db.commit()

    cursor.close()
    db.close()

    return {"short_url": f"http://localhost:8000/r/{final_short_code}"}

@app.get("/r/{short_code}")
def redirect_to_url(short_code: str, request: Request, background_tasks: BackgroundTasks):
    current_ip = request.client.host

    background_tasks.add_task(log_click_background, short_code, current_ip)

    try:
        cached_url = cache.get(short_code)
        if cached_url:
            return RedirectResponse(url=cached_url, status_code=307)
    except redis.ConnectionError:
        pass

    db = mysql.connector.connect(
        host="localhost",
        user="root",        
        password="2703#Harsh",
        database="url_shortener"
    )
    cursor = db.cursor()
    query = "SELECT long_url FROM URLs WHERE short_url = %s"
    cursor.execute(query, (short_code,))
    row = cursor.fetchone()

    cursor.close()
    db.close()

    if not row:
        raise HTTPException(status_code=404, detail="Link not found")

    long_url = row[0]

    try:
        cache.setex(short_code, 86400, long_url)
    except redis.ConnectionError:
        pass

    return RedirectResponse(url=long_url, status_code=307)

@app.get("/stats/{short_code}")
def get_stats(short_code: str):

    db = mysql.connector.connect(
        host="localhost",
        user="root",        
        password="2703#Harsh",
        database="url_shortener"
    )
    cursor = db.cursor()

    count_query = "SELECT COUNT(*) FROM clicks WHERE short_url = %s"
    cursor.execute(count_query, (short_code,))
    total_clicks = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return {
        "short_code": short_code,
        "total_clicks": total_clicks
    }