import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Retailer, Macbook, Offer, Post

app = FastAPI(title="MacBook Price Compare API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MacBook Affiliate Backend Running"}

@app.get("/test")
def test_database():
    """Check database connectivity and list sample collections"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Connected"
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', 'unknown')
            try:
                response["collections"] = db.list_collection_names()[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    # env flags
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else response["database_url"]
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else response["database_name"]

    return response

# --- Seed endpoints (for quick start) ---
class SeedResponse(BaseModel):
    inserted: int

@app.post("/seed/retailers", response_model=SeedResponse)
def seed_retailers():
    """Seed top NL/BE MacBook retailers. Run once safely; duplicates may occur if repeated."""
    retailers: List[Retailer] = [
        # Netherlands
        Retailer(name="Coolblue", country="NL", site_url="https://www.coolblue.nl/", logo_url="https://assets.coolblue.nl/logo.png", affiliate_url="https://prf.hn/click/camref:1101l88G8"),
        Retailer(name="Bol.com", country="NL", site_url="https://www.bol.com/nl/", logo_url="https://www.bol.com/logo.png", affiliate_url="https://partner.bol.com"),
        Retailer(name="MediaMarkt NL", country="NL", site_url="https://www.mediamarkt.nl/", logo_url="https://www.mediamarkt.nl/logo.png", affiliate_url="https://www.awin1.com/"),
        Retailer(name="Amac", country="NL", site_url="https://www.amac.nl/", logo_url="https://www.amac.nl/logo.png", affiliate_url="https://www.tradetracker.com/"),
        Retailer(name="BCC", country="NL", site_url="https://www.bcc.nl/", logo_url="https://www.bcc.nl/logo.png", affiliate_url="https://www.tradetracker.com/"),
        # Belgium
        Retailer(name="Coolblue BE", country="BE", site_url="https://www.coolblue.be/", logo_url="https://www.coolblue.be/logo.png", affiliate_url="https://prf.hn"),
        Retailer(name="Bol.com BE", country="BE", site_url="https://www.bol.com/be-nl/", logo_url="https://www.bol.com/logo.png", affiliate_url="https://partner.bol.com"),
        Retailer(name="MediaMarkt BE", country="BE", site_url="https://www.mediamarkt.be/", logo_url="https://www.mediamarkt.be/logo.png", affiliate_url="https://www.awin1.com/"),
        Retailer(name="Switch", country="BE", site_url="https://www.switch.be/", logo_url="https://www.switch.be/logo.png", affiliate_url="https://www.tradetracker.com/"),
        Retailer(name="Selexion", country="BE", site_url="https://www.selexion.be/", logo_url="https://www.selexion.be/logo.png"),
    ]
    inserted = 0
    for r in retailers:
        try:
            create_document("retailer", r)
            inserted += 1
        except Exception:
            pass
    return SeedResponse(inserted=inserted)

@app.get("/retailers", response_model=List[Retailer])
def list_retailers(country: Optional[str] = None):
    filt = {}
    if country:
        filt["country"] = country
    docs = get_documents("retailer", filt)
    # convert ObjectId etc.
    out = []
    for d in docs:
        d.pop("_id", None)
        out.append(Retailer(**d))
    return out

# Macbook catalogue minimal seed
@app.post("/seed/macbooks", response_model=SeedResponse)
def seed_macbooks():
    macs: List[Macbook] = [
        Macbook(model="MacBook Air 13 M2", chip="M2", size_inches=13.6, base_storage_gb=256, year=2022),
        Macbook(model="MacBook Air 15 M2", chip="M2", size_inches=15.3, base_storage_gb=256, year=2023),
        Macbook(model="MacBook Pro 14 M3", chip="M3", size_inches=14.2, base_storage_gb=512, year=2023),
        Macbook(model="MacBook Pro 16 M3", chip="M3", size_inches=16.2, base_storage_gb=512, year=2023),
    ]
    inserted = 0
    for m in macs:
        try:
            create_document("macbook", m)
            inserted += 1
        except Exception:
            pass
    return SeedResponse(inserted=inserted)

@app.get("/macbooks", response_model=List[Macbook])
def list_macbooks():
    docs = get_documents("macbook", {})
    out = []
    for d in docs:
        d.pop("_id", None)
        out.append(Macbook(**d))
    return out

class OfferIn(Offer):
    pass

@app.get("/offers", response_model=List[Offer])
def list_offers(country: Optional[str] = None, macbook_model: Optional[str] = None):
    filt = {}
    if country:
        filt["country"] = country
    if macbook_model:
        filt["macbook_model"] = macbook_model
    docs = get_documents("offer", filt)
    out = []
    for d in docs:
        d.pop("_id", None)
        out.append(Offer(**d))
    return out

@app.post("/offers", response_model=dict)
def create_offer(offer: OfferIn):
    try:
        create_document("offer", offer)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

# Simple blogging endpoints
@app.get("/posts", response_model=List[Post])
def list_posts():
    docs = get_documents("post", {})
    out = []
    for d in docs:
        d.pop("_id", None)
        out.append(Post(**d))
    return out

@app.post("/posts", response_model=dict)
def create_post(post: Post):
    try:
        create_document("post", post)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
