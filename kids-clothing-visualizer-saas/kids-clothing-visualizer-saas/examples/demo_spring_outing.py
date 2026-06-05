#!/usr/bin/env python3
"""
示例：春游穿搭（7岁偏胖男童，4月初）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from stylist_engine import StylistEngine
from bailian_image_gen import BailianImageGen

engine = StylistEngine()

# 生成搭配方案
result = engine.recommend(
    age=7, gender="男童",
    weight_kg=27.5, height_cm=130,
    body_type="偏胖",
    season="春季", occasion="春游",
    temperature="12-22"
)

print("=" * 60)
print("🎯 搭配方案")
print("=" * 60)
print(f"主题: {result['outfit_plan']['theme']}")
for layer in result['outfit_plan'].get('layers', []):
    print(f"  {layer['layer']}: {layer['color']} {layer['item']} ({layer.get('note','')})")
print(f"\n安全提醒:")
for note in result['safety_notes']:
    print(f"  {note}")
print(f"\n提示词:\n{result['image_prompt'][:200]}...")

# 生成图片
print("\n正在生成效果图...")
gen = BailianImageGen()
image = gen.generate(result['image_prompt'], size="720*1280")
print(f"✅ 图片已生成: {image['images'][0]['local_path']}")
