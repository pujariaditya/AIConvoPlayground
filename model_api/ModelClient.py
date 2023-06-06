import grpc

import protos.model_pb2 as model_pb2
import protos.model_pb2_grpc as model_pb2_grpc
import logging

logger = logging.getLogger(__name__)

class ModelClient:
    def __init__(self, server_address):
        self.channel = grpc.insecure_channel(server_address)
        self.stub = model_pb2_grpc.ModelServiceStub(self.channel)

    def generate_text(self, message):
        request = model_pb2.TextGenerateRequest(message=message)
        response = self.stub.TextGenerate(request)
        return response.reply