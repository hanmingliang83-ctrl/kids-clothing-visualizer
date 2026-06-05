#!/usr/bin/env python3
"""
阿里云百炼(通义万相2.7) 文生图核心引擎
支持：文生图、尺寸选择、批量生成、异步任务轮询
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import uuid

API_BASE = "https://dashscope.aliyuncs.com"


class BailianImageGen:
    """阿里云百炼文生图引擎"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("BAILIAN_API_KEY")
        if not self.api_key:
            raise ValueError("需要设置 BAILIAN_API_KEY 环境变量或传入 api_key 参数")

    def generate(self, prompt: str, size: str = "1024*1024", n: int = 1,
                 model: str = "wan2.7-image", max_wait: int = 120) -> dict:
        """
        生成图片
        返回: {"success": bool, "images": [...], "time_taken": str, ...}
        """
        start_time = time.time()
        task_id = self._submit_task(prompt, size, n, model)
        result = self._poll_task(task_id, max_wait)
        images = self._extract_images(result)
        time_taken = round(time.time() - start_time, 1)

        return {
            "success": True,
            "images": images,
            "model": model,
            "size": size,
            "n": len(images),
            "time_taken": f"{time_taken}s",
            "task_id": task_id
        }

    def _submit_task(self, prompt: str, size: str, n: int, model: str) -> str:
        url = f"{API_BASE}/api/v1/services/aigc/image-generation/generation"
        payload = {
            "model": model,
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [{"text": prompt}]
                }]
            },
            "parameters": {"size": size, "n": n}
        }
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable"
            }, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result["output"]["task_id"]

    def _poll_task(self, task_id: str, max_wait: int) -> dict:
        url = f"{API_BASE}/api/v1/tasks/{task_id}"
        start = time.time()
        while time.time() - start < max_wait:
            req = urllib.request.Request(
                url, headers={"Authorization": f"Bearer {self.api_key}"}, method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                status = result["output"]["task_status"]
                if status == "SUCCEEDED":
                    return result
                elif status in ("FAILED", "CANCELED"):
                    raise RuntimeError(f"任务失败: {result.get('output', {}).get('message', '')}")
                time.sleep(3)
        raise TimeoutError(f"任务超时 ({max_wait}s)")

    def _extract_images(self, result: dict) -> list:
        images = []
        for choice in result.get("output", {}).get("choices", []):
            for content in choice.get("message", {}).get("content", []):
                if content.get("type") == "image":
                    images.append({
                        "url": content["image"],
                        "local_path": self._download(content["image"])
                    })
        return images

    def _download(self, image_url: str) -> str:
        os.makedirs("/tmp/hermes-images", exist_ok=True)
        local_path = f"/tmp/hermes-images/bailian_{uuid.uuid4().hex[:8]}.png"
        with urllib.request.urlopen(image_url, timeout=30) as resp:
            with open(local_path, "wb") as f:
                f.write(resp.read())
        return local_path


# CLI 入口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="阿里云百炼文生图")
    parser.add_argument("--prompt", required=True, help="图片描述提示词")
    parser.add_argument("--size", default="1024*1024")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--model", default="wan2.7-image")
    args = parser.parse_args()

    gen = BailianImageGen()
    result = gen.generate(args.prompt, args.size, args.n, args.model)
    print(json.dumps(result, ensure_ascii=False, indent=2))
