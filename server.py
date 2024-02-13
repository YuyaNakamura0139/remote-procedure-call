import os
import json
import socket
import math
from typing import List, Dict, Any, Callable


class RequestHandler:
    def __init__(self, request: Dict[str, Any]):
        self.request = request

    def handle_request(self) -> Dict[str, Any]:
        method_name = self.request.get("method")
        params = self.request.get("params")
        param_types = self.request.get("param_types")
        id = self.request.get("id")

        method = self.get_method(method_name)
        if not method:
            return self.error_response("Method not found", id)

        try:
            converted_params = self.convert_params(params, param_types)
            result = method(*converted_params)
            return self.success_response(result, id)
        except ValueError as e:
            return self.error_response(str(e), id)
        except Exception as e:
            return self.error_response("Internal server error", id)

    def get_method(self, method_name: str) -> Callable:
        method_map = {
            "floor": self.floor,
            "nroot": self.nroot,
            "reverse": self.reverse,
            "valid_anagram": self.valid_anagram,
            "sort": self.sort,
        }
        return method_map.get(method_name)

    @staticmethod
    def convert_params(params: List[str], param_types: List[str]) -> List[Any]:
        type_conversion_map = {
            "int": int,
            "float": float,
            "str": str,
            "list": list,
        }
        converted_params = []
        for param, param_type in zip(params, param_types):
            try:
                converted_param = type_conversion_map[param_type](param)
                converted_params.append(converted_param)
            except KeyError:
                raise ValueError(f"Unsupported parameter type: {param_type}")
            except ValueError:
                raise ValueError(f"Invalid value for type {param_type}: {param}")
        return converted_params

    @staticmethod
    def floor(x: float) -> int:
        return math.floor(x)

    @staticmethod
    def nroot(n: int, x: float) -> float:
        return x ** (1 / n)

    @staticmethod
    def reverse(s: str) -> str:
        return s[::-1]

    @staticmethod
    def valid_anagram(s1: str, s2: str) -> bool:
        return sorted(s1) == sorted(s2)

    @staticmethod
    def sort(s_arr: List[str]) -> List[str]:
        return sorted(s_arr)

    @staticmethod
    def success_response(result: Any, id: str) -> Dict[str, Any]:
        result_type = type(result).__name__
        return {"results": result, "result_type": result_type, "id": id}

    @staticmethod
    def error_response(message: str, id: str) -> Dict[str, Any]:
        return {"error": message, "id": id}


def main():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    with open("./config.json") as f:
        config = json.load(f)

    SERVER_ADDRESS = config["server_address"]

    try:
        os.unlink(SERVER_ADDRESS)
    except FileNotFoundError:
        pass

    sock.bind(SERVER_ADDRESS)
    sock.listen(1)

    print("Server is listening...")

    while True:
        connection, client_address = sock.accept()
        try:
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                json_data = json.loads(data.decode("utf-8"))
                handler = RequestHandler(json_data)
                response = handler.handle_request()
                connection.sendall(json.dumps(response).encode("utf-8"))
        finally:
            connection.close()


if __name__ == "__main__":
    main()
