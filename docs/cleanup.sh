#!/bin/bash

# 📚 文档自动清理脚本
# 用途：定期清理和归档过期的功能文档

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Cshine 文档清理工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 创建必要的目录
mkdir -p features archive

# 1. 移动 3 个月前的功能文档到归档
echo "1️⃣  检查 features/ 中的文档..."
OLD_DOCS=$(find features -name "DEPLOY_*.md" -mtime +90 2>/dev/null || true)

if [ -n "$OLD_DOCS" ]; then
    echo "   发现 $(echo "$OLD_DOCS" | wc -l) 个超过 3 个月的文档"
    echo "$OLD_DOCS" | while read -r file; do
        echo "   📦 移动: $file -> archive/"
        mv "$file" archive/
    done
    echo "   ✅ 已移动到 archive/"
else
    echo "   ✅ 无需归档的文档"
fi

echo ""

# 2. 检查 1 年前的归档文档
echo "2️⃣  检查 archive/ 中的旧文档..."
VERY_OLD_DOCS=$(find archive -name "*.md" -mtime +365 2>/dev/null || true)

if [ -n "$VERY_OLD_DOCS" ]; then
    echo "   发现 $(echo "$VERY_OLD_DOCS" | wc -l) 个超过 1 年的文档"
    echo ""
    echo "   以下文档超过 1 年，建议删除："
    echo "$VERY_OLD_DOCS" | while read -r file; do
        echo "   📄 $file ($(stat -f "%Sm" -t "%Y-%m-%d" "$file"))"
    done
    echo ""
    read -p "   是否删除这些文档？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$VERY_OLD_DOCS" | while read -r file; do
            echo "   🗑️  删除: $file"
            rm "$file"
        done
        echo "   ✅ 已删除"
    else
        echo "   ⏭️  跳过删除"
    fi
else
    echo "   ✅ 无超过 1 年的文档"
fi

echo ""

# 3. 统计文档数量
echo "3️⃣  文档统计："
echo ""
echo "   📚 核心文档:   $(ls core 2>/dev/null | wc -l | tr -d ' ') 个"
echo "   🚀 部署文档:   $(ls deployment 2>/dev/null | wc -l | tr -d ' ') 个"
echo "   📝 功能文档:   $(ls features 2>/dev/null | wc -l | tr -d ' ') 个"
echo "   📦 归档文档:   $(ls archive 2>/dev/null | wc -l | tr -d ' ') 个"

echo ""

# 4. 检查最近的功能文档
echo "4️⃣  最近的功能文档："
RECENT_DOCS=$(find features -name "DEPLOY_*.md" -mtime -30 2>/dev/null | sort -r | head -5 || true)
if [ -n "$RECENT_DOCS" ]; then
    echo "$RECENT_DOCS" | while read -r file; do
        echo "   📄 $file ($(stat -f "%Sm" -t "%Y-%m-%d" "$file"))"
    done
else
    echo "   (无)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 文档清理完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

