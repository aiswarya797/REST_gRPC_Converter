from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import grpc
import user_pb2
import user_pb2_grpc

# REST JSON models
class CreateUserRequestModel(BaseModel):
    id: str
    name: str
    email: str

class GetUserRequestModel(BaseModel):
    id: str

# Create FastAPI app
app = FastAPI()

# gRPC channel and stub
# A channel in gRPC is basically a virtual connection between a client (your REST gateway) and a gRPC server (your UserService).
channel = grpc.insecure_channel("localhost:50051")
stub = user_pb2_grpc.UserServiceStub(channel)

# REST endpoint for creating a user
@app.post("/users")
def create_user(request: CreateUserRequestModel):
    grpc_request = user_pb2.CreateUserRequest(
        id=request.id,
        name=request.name,
        email=request.email
    )
    try:
        grpc_response = stub.CreateUser(grpc_request)
        return {"success": grpc_response.success, "message": grpc_response.message}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details())

# REST endpoint for getting a user
@app.get("/users/{user_id}")
def get_user(user_id: str):
    grpc_request = user_pb2.GetUserRequest(id=user_id)
    try:
        grpc_response = stub.GetUser(grpc_request)
        if not grpc_response.found:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": grpc_response.id,
            "name": grpc_response.name,
            "email": grpc_response.email
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details())

