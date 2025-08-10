# mcp/mcp_server.py
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
import csv

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

with open(USER_DATA_FILE, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        users[row["user_id"]] = row


@mcp.tool(
    name="authenticate_user",
    description="Authenticate a user by user ID and 4-digit OTP.",
    tags={"Authentication"},
)
async def authenticate_user(user_id: str, otp: str):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user["otp"] != otp:
        raise HTTPException(status_code=401, detail="OTP is wrong")
    return {
        "status": "success",
        "user_id": user["user_id"],
        "name": user["name"],
    }


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
