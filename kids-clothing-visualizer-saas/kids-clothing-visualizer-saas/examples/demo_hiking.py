#!/usr/bin/env python3
"""
示例：爬山穿搭（7岁偏瘦女童，6月）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
from stylist_engine import StylistEngine
from bailian_image_gen import BailianImageGen

engine = StylistEngine()
result = engine.recommend(
    age=7, gender="女童",
    weight_kg=20, height_cm=120,
    body_type="偏瘦",
    season="夏季", occasion="爬山",
    temperature="28-32"
)

print(f"🎯 {result['outfit_plan']['theme']}")
for layer in result['outfit_plan'].get('layers', []):
    print(f"  {layer['layer']}: {layer['color']} {layer['item']}")
print(f"必带物品: {', '.join(result['outfit_plan'].get('bring_items',[]))}")

gen = BailianImageGen()
image = gen.generate(result['image_prompt'], size="720*1280")
print(f"✅ 图片: {image['images'][0]['local_path']}")
