# mcp/mcp_server.py
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
import csv
import random
import time

# FastAPI app instance
# MCP server instance
mcp = FastMCP("Custom MCP server")
streamable_http_app = mcp.http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.
    """
    async with streamable_http_app.router.lifespan_context(app):
        print("MCP server is starting up...")
        yield
    # Cleanup code can be added here if needed


app = FastAPI(
    title="MCP Server",
    description="A custom MCP server implementation",
    lifespan=lifespan,
)
# Middleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", streamable_http_app)

# Load user data
USER_DATA_FILE = "user_data.csv"
users = {}

# Store OTPs temporarily (in production, use Redis or database)
otp_store = {}

with open(USER_DATA_FILE, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        users[row["user_id"]] = row


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


@mcp.tool(
    name="authenticate_user",
    description="Authenticate a user by user_id and OTP. First call with user_id to get OTP, then call with user_id and OTP to authenticate.",
    tags={"Authentication"},
)
async def authenticate_user(user_id: str, otp: str = None):
    """
    Authenticate user with user_id and OTP.
    If OTP is not provided, generate and return OTP for the user.
    If OTP is provided, verify it and return user details.
    """
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User ID not found")
    
    if otp is None:
        # Generate OTP for the user
        generated_otp = generate_otp()
        otp_store[user_id] = {
            'otp': generated_otp,
            'timestamp': time.time(),
            'attempts': 0
        }
        
        return {
            "status": "otp_sent",
            "message": f"OTP sent to mobile {user['mobile']}",
            "user_id": user_id,
            "mobile": user['mobile']
        }
    else:
        # Verify OTP
        stored_otp_data = otp_store.get(user_id)
        if not stored_otp_data:
            raise HTTPException(status_code=400, detail="No OTP requested for this user")
        
        # Check if OTP is expired (5 minutes)
        if time.time() - stored_otp_data['timestamp'] > 300:
            del otp_store[user_id]
            raise HTTPException(status_code=400, detail="OTP expired. Please request a new one.")
        
        # Check attempts
        if stored_otp_data['attempts'] >= 3:
            del otp_store[user_id]
            raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new OTP.")
        
        # Verify OTP
        if stored_otp_data['otp'] == otp:
            # Authentication successful
            del otp_store[user_id]
            return {
                "status": "success",
                "user_id": user_id,
                "name": user["name"],
                "mobile": user["mobile"]
            }
        else:
            # Increment attempts
            stored_otp_data['attempts'] += 1
            raise HTTPException(status_code=401, detail=f"Invalid OTP. {3 - stored_otp_data['attempts']} attempts remaining.")


@mcp.tool(
    name="get_user_info",
    description="Retrieve name, DOB, and transactions for a user.",
    tags={"User Info"},
)
async def get_user_info(user_id: str):
    user = users.get(user_id)
    if user:
        return {
            "name": user["name"],
            "dob": user["dob"],
            "transactions": user["transactions"],
        }
    raise HTTPException(status_code=404, detail="User not found")


@mcp.tool(
    name="get_user_bill",
    description="Retrieve bill amount for a user.",
    tags={"Billing"},
)
async def get_user_bill(user_id: str):
    user = users.get(user_id)
    if user:
        return {
            "bill_amount": user["bill_amount"],
        }
    raise HTTPException(status_code=404, detail="User not found")


@mcp.tool(
    name="get_user_contact",
    description="Retrieve email and address for a user.",
    tags={"Contact"},
)
async def get_user_contact(user_id: str):
    user = users.get(user_id)
    if user:
        return {
            "email": user["email"],
            "address": user["address"],
        }
    raise HTTPException(status_code=404, detail="User not found")


@mcp.tool(
    name="get_user_last_login",
    description="Retrieve last login time for a user.",
    tags={"Login"},
)
async def get_user_last_login(user_id: str):
    user = users.get(user_id)
    if user:
        return {
            "last_login": user["last_login"],
        }
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok"}
