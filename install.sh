#!/bin/bash
set -e

echo "🚀 安装 Health Agent Skill v2.0"
python3 --version

python3 -m venv .venv-health
. .venv-health/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "✅ 安装完成"
echo "使用方法：@health-agent /health-init user_id=demo age=24 sex=female"
