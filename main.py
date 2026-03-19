from fastapi import FastAPI, Depends, HTTPException, status
from jsonmap import UserGetRegister, UserPostRegister, Token, UserPostLogin, ProductGetMap, ProductPostMap, PurchaseGetMap, PurchasePostMap, SaleGetMap, SalePostMap
from sqlalchemy.orm import Session
from models import User, Product, Purchase, Sale, SalesDetails
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from myjwt import (get_db, get_password_hash,
                   verify_password, create_access_token, get_current_user)
from datetime import timedelta
app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.get("/")
def home():
    return {"Duka FastAPI": "Version 1.0"}


@app.post("/register", response_model=UserGetRegister, status_code=201)
def register(user: UserPostRegister, db: Session = Depends(get_db)):

    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.scalar(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")

    new_user = User(name=user.name, phone=user.phone,
                    email=user.email, password=get_password_hash(user.password))
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

    return new_user


@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username.lower().strip()
    db_user = db.scalar(
        select(User).where(User.email == email)
    )

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": db_user.email, "scope": "me items"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(access_token=access_token, token_type="bearer")



@app.get("/products", response_model=list[ProductGetMap])
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(select(Product)).all()
    # return list(db.scalars(select(Product)))


@app.post("/products", response_model=ProductGetMap, status_code=201)
def create_product(product: ProductPostMap, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)
                   ):
    model = Product(**product.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@app.get("/purchase", response_model=list[PurchaseGetMap])
def get_purchases(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return db.scalars(select(Purchase).where(Purchase.user_id == current_user.id)).all()


@app.post("/purchase", response_model=PurchaseGetMap, status_code=201)
def create_purchase(
    purchase: PurchasePostMap,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_purchase = Purchase(
        quantity=purchase.quantity,
        product_id=purchase.product_id,
        user_id=current_user.id
    )

    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)

    return new_purchase


@app.get("/sales", response_model=list[SaleGetMap])
def get_sales(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return db.scalars(select(Sale).where(Sale.user_id == current_user.id)).all()


@app.post("/sales", response_model=SaleGetMap, status_code=201)
def create_sale(
    sale: SalePostMap,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = Sale(user_id=current_user.id)

    for item in sale.details:

        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        model.details.append(
            SalesDetails(
                product_id=item.product_id,
                quantity=item.quantity
            )
        )

    db.add(model)
    db.commit()
    db.refresh(model)
    return model

# uvicorn main:app --reload
