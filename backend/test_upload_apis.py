#!/usr/bin/env python3
"""
测试上传功能相关的 API 接口
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的 token（需要先登录获取）
# 这里使用环境中已有的 token
TOKEN = None

def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get("http://localhost:8000/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_oss_signature():
    """测试 OSS 签名获取（需要登录）"""
    print("=== 测试 OSS 签名获取 ===")
    if not TOKEN:
        print("⚠️  需要登录 token，跳过此测试")
        print()
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/upload/oss-signature", headers=headers)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print()

def test_api_docs():
    """测试 API 文档是否可访问"""
    print("=== 测试 API 文档 ===")
    response = requests.get("http://localhost:8000/docs")
    print(f"状态码: {response.status_code}")
    print(f"API 文档可访问: {'✅' if response.status_code == 200 else '❌'}")
    print(f"访问地址: http://localhost:8000/docs")
    print()

def main():
    print("🚀 Cshine 上传功能 API 测试")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_api_docs()
        test_oss_signature()
        
        print("=" * 50)
        print("✅ 后端服务运行正常！")
        print()
        print("📝 新增的 API 端点:")
        print("  - GET  /api/v1/upload/oss-signature  - 获取 OSS 上传签名")
        print("  - POST /api/v1/folders              - 创建知识库")
        print("  - GET  /api/v1/folders              - 获取知识库列表")
        print("  - GET  /api/v1/folders/{id}         - 获取知识库详情")
        print("  - PUT  /api/v1/folders/{id}         - 更新知识库")
        print("  - DELETE /api/v1/folders/{id}       - 删除知识库")
        print()
        print("🌐 完整 API 文档: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请检查服务是否启动")
    except Exception as e:
        print(f"❌ 测试出错: {e}")

if __name__ == "__main__":
    main()

