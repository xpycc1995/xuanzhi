"""
Task 1: 技术假设验证脚本
验证百炼Embedding API连接
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()


async def test_bailian_embedding():
    """测试阿里云百炼Embedding API"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("❌ 未配置DASHSCOPE_API_KEY环境变量")
        return False
    
    print(f"✓ DASHSCOPE_API_KEY已配置: {api_key[:10]}...")
    
    # 百炼Embedding API端点
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # 使用text-embedding-v3模型 (1024维)
    payload = {
        "model": "text-embedding-v3",
        "input": "测试文本：规划选址论证报告",
        "dimensions": 1024,  # 可选: 1024, 768, 512
    }
    
    print(f"\n发送请求到: {url}")
    print(f"模型: text-embedding-v3")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                embedding = data.get("data", [{}])[0].get("embedding", [])
                print(f"\n✅ 百炼Embedding API验证成功!")
                print(f"   - 向量维度: {len(embedding)}")
                print(f"   - 向量前5个值: {embedding[:5]}")
                return True
            else:
                print(f"\n❌ API调用失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"\n❌ 连接失败: {str(e)}")
            return False


def test_chromadb_import():
    """测试ChromaDB是否可导入"""
    try:
        import chromadb
        print(f"\n✅ ChromaDB已安装: {chromadb.__version__}")
        return True
    except ImportError:
        print("\n⚠️ ChromaDB未安装, 需要运行: pip install chromadb")
        return False


def test_pdf_import():
    """测试PDF解析库是否可导入"""
    try:
        import pypdf
        print(f"✅ pypdf已安装: {pypdf.__version__}")
        return True
    except ImportError:
        print("⚠️ pypdf未安装, 需要运行: pip install pypdf")
        return False


def test_docx_import():
    """测试python-docx是否可导入"""
    try:
        import docx
        print(f"✅ python-docx已安装")
        return True
    except ImportError:
        print("⚠️ python-docx未安装 (已存在于项目中)")
        return False


def main():
    print("=" * 60)
    print("Wave 1 - Task 1: 技术假设验证")
    print("=" * 60)
    
    print("\n[1/4] 百炼Embedding API验证")
    embedding_ok = asyncio.run(test_bailian_embedding())
    
    print("\n[2/4] ChromaDB导入验证")
    chromadb_ok = test_chromadb_import()
    
    print("\n[3/4] PDF解析库验证")
    pdf_ok = test_pdf_import()
    
    print("\n[4/4] Word解析库验证")
    docx_ok = test_docx_import()
    
    print("\n" + "=" * 60)
    print("验证结果汇总:")
    print("=" * 60)
    print(f"  百炼Embedding: {'✅ 通过' if embedding_ok else '❌ 失败'}")
    print(f"  ChromaDB: {'✅ 已安装' if chromadb_ok else '⚠️ 需安装'}")
    print(f"  PDF解析: {'✅ 已安装' if pdf_ok else '⚠️ 需安装'}")
    print(f"  Word解析: {'✅ 已安装' if docx_ok else '⚠️ 需安装'}")
    
    if embedding_ok:
        print("\n✅ 核心技术假设验证通过!")
        if not (chromadb_ok and pdf_ok):
            print("⚠️  需要安装缺失的依赖: pip install chromadb pypdf")
    else:
        print("\n❌ 核心技术假设验证失败, 请检查API配置")


if __name__ == "__main__":
    main()