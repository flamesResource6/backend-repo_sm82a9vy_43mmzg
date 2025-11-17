"""
Database Schemas for MacBook Affiliate Blog

Each Pydantic model represents a collection in MongoDB. The collection name is the lowercase of the class name.
- Retailer -> "retailer"
- Macbook -> "macbook"
- Offer -> "offer"
- Post -> "post"
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from datetime import datetime

CountryCode = Literal["NL", "BE"]

class Retailer(BaseModel):
    name: str = Field(..., description="Retailer display name")
    country: CountryCode = Field(..., description="Country code for market focus")
    logo_url: Optional[HttpUrl] = Field(None, description="Public logo URL")
    site_url: HttpUrl = Field(..., description="Homepage URL")
    affiliate_url: Optional[HttpUrl] = Field(None, description="Affiliate deep link or placeholder")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating out of 5")

class Macbook(BaseModel):
    model: str = Field(..., description="Model identifier e.g., MacBook Air 13 M2")
    chip: str = Field(..., description="Chip designation e.g., M1, M2, M3")
    size_inches: float = Field(..., description="Screen size in inches")
    base_storage_gb: int = Field(..., ge=128, description="Base storage capacity")
    year: int = Field(..., ge=2015, description="Release year")

class Offer(BaseModel):
    macbook_model: str = Field(..., description="Reference to Macbook.model")
    retailer_name: str = Field(..., description="Reference to Retailer.name")
    country: CountryCode = Field(..., description="Country for which the price applies")
    price_eur: float = Field(..., ge=0, description="Price in EUR")
    product_url: HttpUrl = Field(..., description="Product page (affiliate if possible)")
    in_stock: bool = Field(True, description="Availability")
    last_checked: Optional[datetime] = Field(None, description="Timestamp when price was last verified")

class Post(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content_md: str = Field(..., description="Markdown content")
    country: Optional[CountryCode] = None
    cover_image: Optional[HttpUrl] = None
