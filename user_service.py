import grpc
from concurrent import futures
import time

import user_pb2
import user_pb2_grpc

# Simple in-memory storage
USERS = {}

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        if request.id in USERS:
            return user_pb2.CreateUserResponse(success=False, message="User already exists")
        USERS[request.id] = {"name": request.name, "email": request.email}
        print(f"[UserService] Created user: {request.id} -> {request.name}")
        return user_pb2.CreateUserResponse(success=True, message="User created")

    def GetUser(self, request, context):
        user = USERS.get(request.id)
        if not user:
            return user_pb2.GetUserResponse(found=False)
        return user_pb2.GetUserResponse(
            id=request.id, name=user["name"], email=user["email"], found=True
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("UserService running on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
