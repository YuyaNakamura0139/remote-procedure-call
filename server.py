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
            return self.error_response("Internal server error.\n" + str(e), id)

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
        """
        パラメータを指定された型に変換します。

        Args:
            params (List[str]): 変換するパラメータのリスト。
            param_types (List[str]): 各パラメータの型を示す文字列のリスト。

        Returns:
            List[Any]: 変換されたパラメータのリスト。

        Raises:
            ValueError: サポートされていない型が指定された場合、または変換に失敗した場合。
        """
        type_conversion_map = {
            "int": int,
            "float": float,
            "str": str,
            "list": str,
        }
        converted_params = []
        for param, param_type in zip(params, param_types):
            try:
                # param: "1", param_type: int --> 1
                # param: "1.1", param_type: float --> 1.1
                # param: "hello", param_type: str --> "hello"
                # param: "[1, 2, 3]", param_type: list --> [1, 2, 3]
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
    # ソケット通信の実装

    # ①ソケットの作成
    # AF_UNIX: Unixドメインソケットを使用
    # SOCK_STREAM: TCPソケットを使用
    # ローカル通信に使用する。同一マシン上で効率的なプロセス間通信を可能とする。
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # 設定ファイルを読み込んでサーバーのアドレスを取得
    # Unixドメインソケットを使用しているため、サーバーのアドレスはファイルパスとして表現される。
    with open("./config.json") as f:
        config = json.load(f)
    SERVER_ADDRESS = config["server_address"]

    # 既存のソケットファイルを削除しておく
    # ソケットファイルが存在しなかったら何もしない
    try:
        os.unlink(SERVER_ADDRESS)
    except FileNotFoundError:
        pass

    # ②ソケットにサーバーのアドレスをバインド
    sock.bind(SERVER_ADDRESS)

    # ③ソケットをリスニングモードに設定
    sock.listen(1)

    print("Server is listening...")

    while True:
        # ④クライアントからの接続を受け入れる
        connection, client_address = sock.accept()
        try:
            while True:
                # ⑤クライアントからのデータを受信
                data = connection.recv(1024)
                if not data:
                    break
                # 受信したデータをJSON形式に変換
                json_data = json.loads(data.decode("utf-8"))
                print(json_data)
                # リクエストを処理
                handler = RequestHandler(request=json_data)
                response = handler.handle_request()
                # ⑥処理結果をクライアントに送信
                connection.sendall(json.dumps(response).encode("utf-8"))
        finally:
            # ⑦接続を閉じる
            connection.close()


if __name__ == "__main__":
    main()
