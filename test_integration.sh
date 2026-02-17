#!/bin/bash
# Test script for Music Recommendation System

BASE_URL="http://localhost:8001"
TOKEN=""

echo "=========================================="
echo "集成测试开始"
echo "=========================================="

# Helper function
test_api() {
    local name="$1"
    local cmd="$2"
    echo ""
    echo "[TEST] $name"
    eval "$cmd"
}

# ===== 认证模块测试 =====
echo ""
echo "===== 认证模块测试 ====="

# Register new user
echo "[IT-AUTH-01] 用户注册 - 正常数据"
result=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser'"$(date +%s)"'","email":"new'"$(date +%s)"'@test.com","password":"Test123456"}')
if echo "$result" | grep -q '"id"'; then
    echo "✅ PASS - 用户注册成功"
else
    echo "❌ FAIL - $result"
fi

# Register duplicate username
echo ""
echo "[IT-AUTH-02] 用户注册 - 重复用户名"
result=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser'"$(date +%s)"'","email":"test@test.com","password":"Test123456"}')
if echo "$result" | grep -q "already"; then
    echo "✅ PASS - 正确拒绝重复用户名"
else
    echo "❌ FAIL - $result"
fi

# Register invalid email
echo ""
echo "[IT-AUTH-03] 用户注册 - 非法邮箱"
result=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"user'"$(date +%s)"'","email":"notanemail","password":"Test123456"}')
if echo "$result" | grep -q "detail"; then
    echo "✅ PASS - 正确拒绝非法邮箱"
else
    echo "❌ FAIL - $result"
fi

# Login
echo ""
echo "[IT-AUTH-04] 用户登录 - 正确凭证"
result=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","password":"Test123456"}')
if echo "$result" | grep -q "access_token"; then
    TOKEN=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))")
    echo "✅ PASS - 登录成功"
else
    echo "❌ FAIL - $result"
fi

# Login wrong password
echo ""
echo "[IT-AUTH-05] 用户登录 - 错误密码"
result=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","password":"wrongpassword"}')
if echo "$result" | grep -q "detail"; then
    echo "✅ PASS - 正确拒绝错误密码"
else
    echo "❌ FAIL - $result"
fi

# Get current user
echo ""
echo "[IT-AUTH-07] Token验证 - 有效Token"
result=$(curl -s "$BASE_URL/api/auth/me" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q "username"; then
    echo "✅ PASS - Token验证成功"
else
    echo "❌ FAIL - $result"
fi

# ===== 音乐模块测试 =====
echo ""
echo "===== 音乐模块测试 ====="

# Get music list
echo ""
echo "[IT-MUSIC-01] 获取音乐列表"
result=$(curl -s "$BASE_URL/api/music?limit=5")
count=$(echo "$result" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [ "$count" -gt 0 ]; then
    echo "✅ PASS - 获取音乐列表成功 ($count 首)"
else
    echo "❌ FAIL"
fi

# Get music by ID
echo ""
echo "[IT-MUSIC-03] 按ID获取音乐详情"
result=$(curl -s "$BASE_URL/api/music/1")
if echo "$result" | grep -q '"id":1'; then
    echo "✅ PASS - 获取音乐详情成功"
else
    echo "❌ FAIL - $result"
fi

# Search music
echo ""
echo "[IT-MUSIC-05] 搜索音乐 - 按标题"
result=$(curl -s "$BASE_URL/api/music/search?q=rock")
if echo "$result" | grep -q "rock"; then
    echo "✅ PASS - 搜索成功"
else
    echo "❌ FAIL - $result"
fi

# Audio streaming
echo ""
echo "[IT-MUSIC-08] 音频流获取"
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/music/audio/1")
if [ "$status" = "200" ]; then
    echo "✅ PASS - 音频流正常"
else
    echo "❌ FAIL - HTTP $status"
fi

# ===== 收藏功能测试 =====
echo ""
echo "===== 收藏功能测试 ====="

# Add favorite
echo ""
echo "[IT-FAV-01] 添加收藏"
result=$(curl -s -X POST "$BASE_URL/api/favorites/1" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q '"music_id":1'; then
    echo "✅ PASS - 添加收藏成功"
else
    echo "❌ FAIL - $result"
fi

# Get favorites
echo ""
echo "[IT-FAV-05] 获取收藏列表"
result=$(curl -s "$BASE_URL/api/favorites" -H "Authorization: Bearer $TOKEN")
count=$(echo "$result" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [ "$count" -gt 0 ]; then
    echo "✅ PASS - 获取收藏列表成功 ($count 首)"
else
    echo "❌ FAIL"
fi

# Check favorite
echo ""
echo "[IT-FAV-07] 检查收藏状态-已收藏"
result=$(curl -s "$BASE_URL/api/favorites/check/1" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q '"is_favorited":true'; then
    echo "✅ PASS - 收藏状态正确"
else
    echo "❌ FAIL - $result"
fi

# Remove favorite
echo ""
echo "[IT-FAV-03] 取消收藏"
result=$(curl -s -X DELETE "$BASE_URL/api/favorites/1" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q '"message"'; then
    echo "✅ PASS - 取消收藏成功"
else
    echo "❌ FAIL - $result"
fi

# Check favorite again
echo ""
echo "[IT-FAV-08] 检查收藏状态-未收藏"
result=$(curl -s "$BASE_URL/api/favorites/check/1" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q '"is_favorited":false'; then
    echo "✅ PASS - 收藏状态正确"
else
    echo "❌ FAIL - $result"
fi

# Get favorites count
echo ""
echo "[IT-FAV-09] 获取收藏数量"
result=$(curl -s "$BASE_URL/api/favorites/count" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q '"count"'; then
    echo "✅ PASS - 获取数量成功: $result"
else
    echo "❌ FAIL - $result"
fi

# ===== 推荐算法测试 =====
echo ""
echo "===== 推荐算法测试 ====="

# Add favorite again for recommendation test
curl -s -X POST "$BASE_URL/api/favorites/1" -H "Authorization: Bearer $TOKEN" > /dev/null

# Based on favorites recommendation
echo ""
echo "[IT-ALGO-06] 基于收藏推荐"
result=$(curl -s "$BASE_URL/api/recommend/by-favorites?limit=5" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q '"based-on-favorites"'; then
    echo "✅ PASS - 基于收藏推荐成功"
else
    echo "❌ FAIL - $result"
fi

# Regular recommendations
echo ""
echo "[IT-ALGO-01] Content-Based推荐"
result=$(curl -s "$BASE_URL/api/recommend?emotion=happy&limit=5" -H "Authorization: Bearer $TOKEN")
if echo "$result" | grep -q '"recommendations"'; then
    echo "✅ PASS - 情感推荐成功"
else
    echo "❌ FAIL - $result"
fi

# ===== 情感模块测试 =====
echo ""
echo "===== 情感模块测试 ====="

# Record emotion
echo ""
echo "[IT-EMO-01] 记录用户情感"
result=$(curl -s -X POST "$BASE_URL/api/emotion" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"emotion_type":"happy","intensity":1.0}')
if echo "$result" | grep -q '"emotion_type":"happy"'; then
    echo "✅ PASS - 记录情感成功"
else
    echo "❌ FAIL - $result"
fi

# Get emotion history
echo ""
echo "[IT-EMO-03] 获取情感历史"
result=$(curl -s "$BASE_URL/api/emotion/history?limit=10" -H "Authorization: Bearer $TOKEN")
count=$(echo "$result" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [ "$count" -gt 0 ]; then
    echo "✅ PASS - 获取情感历史成功 ($count 条)"
else
    echo "❌ FAIL"
fi

# ===== 数据流测试 =====
echo ""
echo "===== 数据流测试 ====="

echo ""
echo "[IT-DATA-01] GTZAN数据加载"
result=$(curl -s "$BASE_URL/api/music?limit=1000")
count=$(echo "$result" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
echo "当前加载歌曲数: $count"
if [ "$count" -gt 900 ]; then
    echo "✅ PASS - GTZAN数据加载成功"
else
    echo "⚠️ 警告 - 歌曲数量少于预期"
fi

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
